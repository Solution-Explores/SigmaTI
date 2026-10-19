"""K09/K12: instalação isolada, autenticação e persistência dos volumes."""
import argparse
import base64
import json
import os
import re
from pathlib import Path
import secrets
import socket
import subprocess
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    project = 'sigma-acceptance-' + secrets.token_hex(5)
    names = ('POSTGRES_USER','POSTGRES_PASSWORD','ZABBIX_DB_USER','ZABBIX_DB_PASS',
             'GF_SECURITY_ADMIN_USER','GF_SECURITY_ADMIN_PASSWORD')
    credentials = {k: 'test_' + secrets.token_hex(16) for k in names}
    env = {**os.environ, **credentials, 'COMPOSE_PROJECT_NAME': project, 'POSTGRES_DB': 'sigmadb'}
    credentials['N8N_OWNER_PASSWORD'] = 'Test!' + secrets.token_hex(16)
    empty = out / 'empty.env'; empty.touch()
    report = {'project': project, 'checks': [], 'status': 'running'}
    compose = None

    def safe(text):
        for value in credentials.values(): text = text.replace(value, '[REDACTED]')
        return text

    def run(command, timeout=180, check=True):
        r = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True,
                           encoding='utf-8', errors='replace', timeout=timeout)
        if check and r.returncode:
            raise RuntimeError(safe((r.stderr or r.stdout)[-3000:]))
        return r

    def check(name, ok, observed=None):
        report['checks'].append({'name': name, 'passed': bool(ok), **({'observed':observed} if observed is not None else {})})
        print(('PASS: ' if ok else 'FAIL: ') + name + (f' (observed={observed})' if observed is not None else ''), flush=True)
        if not ok: raise RuntimeError(name)

    def eventually(fn, timeout=120):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                value = fn()
                if value: return value
            except (OSError, ValueError, RuntimeError): pass
            time.sleep(1)
        raise RuntimeError('Serviço não ficou pronto dentro do prazo.')

    def sql(service, query, valid=True):
        userkey, passkey = ('POSTGRES_USER','POSTGRES_PASSWORD') if service == 'db' else ('ZABBIX_DB_USER','ZABBIX_DB_PASS')
        user = credentials[userkey]
        db = 'sigmadb' if service == 'db' else 'zabbix'
        # Test authentication on the bridge address: the image trusts loopback during initdb.
        return run(compose + ['exec','-T','-e','PGPASSWORD=' + (credentials[passkey] if valid else secrets.token_hex(24)),
            service,'psql','-h',service,'-U',user,'-d',db,'-At','-c',query], check=False)

    def http(port, path, auth=None, payload=None, method=None, cookie=None):
        req = urllib.request.Request(f'http://localhost:{port}{path}',
            data=json.dumps(payload).encode() if payload is not None else None, method=method)
        if payload is not None: req.add_header('Content-Type','application/json')
        if auth: req.add_header('Authorization','Basic '+base64.b64encode(auth.encode()).decode())
        if cookie: req.add_header('Cookie',cookie)
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *args): return None
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
        try:
            with opener.open(req,timeout=5) as r: return r.status, r.read().decode(), r.headers
        except urllib.error.HTTPError as e: return e.code, e.read().decode(), e.headers

    def zabbix_listening():
        with socket.create_connection(('127.0.0.1', ports['zabbix-server']), timeout=3):
            return True

    try:
        run(['docker','info','--format','{{.ServerVersion}}'])
        rendered = run(['docker','compose','--env-file',str(empty),'-p',project,
            '-f',str(ROOT/'docker-compose.yml'),'--profile','monitoring','config','--format','json'])
        model = json.loads(rendered.stdout)
        ports = {}
        for name,service in model['services'].items():
            service['container_name'] = project + '-' + name
            if service.get('ports'):
                with socket.socket() as sock:
                    sock.bind(('127.0.0.1',0)); port = sock.getsockname()[1]
                ports[name] = port
                for mapping in service['ports']:
                    mapping.update({'published':str(port),'host_ip':'127.0.0.1'})
            for mount in service.get('volumes',[]):
                if mount['type'] != 'volume': raise RuntimeError('Montagem externa inesperada.')
        for name,volume in model.get('volumes',{}).items():
            volume['name'] = project + '-' + name
            if run(['docker','volume','inspect',volume['name']],check=False).returncode == 0:
                raise RuntimeError('O volume de teste já existe; operação cancelada.')
        for name,network in model.get('networks',{}).items(): network['name'] = project + '-' + name
        model['name'] = project
        fixture = out/'compose.json'; fixture.write_text(json.dumps(model),encoding='utf-8')
        compose = ['docker','compose','--env-file',str(empty),'-p',project,'-f',str(fixture),'--profile','monitoring']
        report['ports'] = ports
        check('isolated_config', run(compose+['config','--quiet']).returncode == 0)
        print('Downloading locked images with TLS validation...',flush=True)
        run(compose+['pull','--quiet'],timeout=300)
        print('Starting isolated services...',flush=True)
        run(compose+['up','-d','--wait','--wait-timeout','180'],timeout=240)
        eventually(lambda: sql('db','SELECT 1').returncode == 0)
        check('postgres_authentication', sql('db','SELECT 1').stdout.strip() == '1')
        check('postgres_rejects_wrong_password', sql('db','SELECT 1',False).returncode != 0)
        # /healthz is liveness only: during migrations the other routes return an HTML 200.
        eventually(lambda: http(ports['n8n'],'/healthz/readiness')[0] == 200,timeout=240)
        eventually(lambda: http(ports['n8n'],'/rest/settings')[2].get('Content-Type','').startswith('application/json'))
        owner = {'email':'demo@example.invalid','firstName':'Demo','lastName':'Acceptance',
                 'password':credentials['N8N_OWNER_PASSWORD']}
        setup = http(ports['n8n'],'/rest/owner/setup',payload=owner)
        report['n8n_setup_content_type'] = setup[2].get('Content-Type')
        try:
            setup_json = json.loads(setup[1])
        except ValueError:
            setup_json = {}
            (out/'n8n-response.txt').write_text(safe(setup[1]),encoding='utf-8')
            title = re.search(r'<title>(.*?)</title>',setup[1],re.IGNORECASE)
            report['n8n_setup_page_title'] = title.group(1) if title else None
        report['n8n_setup_json_keys'] = list(setup_json) if isinstance(setup_json,dict) else []
        check('n8n_native_owner_setup',setup[0] == 200 and setup_json.get('data',{}).get('email') == owner['email'],
            {'status':setup[0], 'content_type':setup[2].get('Content-Type')})
        unauthenticated = http(ports['n8n'],'/rest/workflows')
        check('n8n_protected_api', unauthenticated[0] == 401, unauthenticated[0])
        login = http(ports['n8n'],'/rest/login',payload={'email':owner['email'],'password':owner['password']})
        check('n8n_login',login[0] == 200)
        cookie = login[2].get('Set-Cookie','').split(';',1)[0]
        check('n8n_authenticated_api',http(ports['n8n'],'/rest/workflows',cookie=cookie)[0] == 200)
        check('n8n_rejects_wrong_password',http(ports['n8n'],'/rest/login',payload={
            'email':owner['email'],'password':secrets.token_hex(24)})[0] == 401)
        eventually(lambda: http(ports['grafana'],'/api/health')[0] == 200)
        admin = credentials['GF_SECURITY_ADMIN_USER']+':'+credentials['GF_SECURITY_ADMIN_PASSWORD']
        check('grafana_authentication', http(ports['grafana'],'/api/user',admin)[0] == 200)
        check('grafana_rejects_wrong_password', http(ports['grafana'],'/api/user','invalid:invalid')[0] == 401)
        check('grafana_write_preference',http(ports['grafana'],'/api/user/preferences',admin,
            payload={'theme':'dark','timezone':'utc'},method='PUT')[0] == 200)
        eventually(lambda: sql('postgres-server','SELECT count(*) FROM hosts').returncode == 0)
        check('zabbix_database_ready', sql('postgres-server','SELECT count(*) FROM hosts').returncode == 0)
        check('zabbix_server_listening', eventually(zabbix_listening))
        check('zabbix_database_rejects_wrong_password', sql('postgres-server','SELECT 1',False).returncode != 0)
        for service in ('db','postgres-server'):
            check(service+'_write_marker',sql(service,
                "CREATE TABLE acceptance_marker(id integer PRIMARY KEY); INSERT INTO acceptance_marker VALUES (1);").returncode == 0)
        # Fingerprints of service-owned persistent files; contents/keys are never printed.
        n8n_cmd = ['exec','-T','n8n','node','-e',"console.log(require('crypto').createHash('sha256').update(require('fs').readFileSync('/home/node/.n8n/config')).digest('hex'))"]
        n8n_before = run(compose+n8n_cmd).stdout.strip()
        print('Recreating only the isolated containers...',flush=True)
        run(compose+['up','-d','--force-recreate','--wait','--wait-timeout','180'],timeout=240)
        eventually(lambda: sql('db','SELECT count(*) FROM acceptance_marker').stdout.strip() == '1')
        check('postgres_persistence',sql('db','SELECT count(*) FROM acceptance_marker').stdout.strip() == '1')
        eventually(lambda: http(ports['n8n'],'/healthz/readiness')[0] == 200,timeout=240)
        check('n8n_config_persistence',run(compose+n8n_cmd).stdout.strip() == n8n_before)
        eventually(lambda: http(ports['n8n'],'/rest/settings')[2].get('Content-Type','').startswith('application/json'))
        check('n8n_owner_persistence',http(ports['n8n'],'/rest/login',payload={
            'email':owner['email'],'password':owner['password']})[0] == 200)
        eventually(lambda: http(ports['grafana'],'/api/health')[0] == 200)
        check('grafana_user_persistence',http(ports['grafana'],'/api/user',admin)[0] == 200)
        check('grafana_preference_persistence',json.loads(http(ports['grafana'],
            '/api/user/preferences',admin)[1]).get('timezone') == 'utc')
        check('zabbix_database_persistence',sql('postgres-server','SELECT count(*) FROM acceptance_marker').stdout.strip() == '1')
        check('zabbix_server_listening_after_recreation', eventually(zabbix_listening))
        report['status'] = 'passed'
    except Exception as e:
        report['status'] = 'failed'
        report['error'] = safe(str(e))
        print('FAIL: '+report['error'],flush=True)
    finally:
        if compose:
            # The file names and project were generated above and every volume was absent before this run.
            try:
                cleanup = run(compose+['down','--volumes','--timeout','30'],timeout=90,check=False)
                report['cleanup_exit_code'] = cleanup.returncode
                if cleanup.returncode:
                    report['status'] = 'cleanup_failed'
            except Exception as e:
                report['status'] = 'cleanup_failed'
                report['cleanup_error'] = safe(str(e))
        (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
