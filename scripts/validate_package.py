"""Issue #9: instalações editável/wheel em venvs novos, fora do checkout."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import venv
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CORE_CHECK = """
import importlib.metadata
import importlib.util
import sigma_eng
from sigma_eng import anomaly, approvals, audit_chain, incidents, probe, runbooks, slo, stats
assert importlib.metadata.version('sigma-eng') == sigma_eng.__version__
assert importlib.util.find_spec('fastapi') is None, 'O núcleo instalou dependências da API'
assert 'auth' not in __import__('sys').modules
print(sigma_eng.__file__)
"""
API_CHECK = """
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sigma_eng.api import create_router
from sigma_eng.audit_chain import AuditChain
assert 'auth' not in __import__('sys').modules
try:
    create_router()
except TypeError:
    pass
else:
    raise AssertionError('Política de autorização deve ser obrigatória')
def policy(role):
    def deny():
        raise HTTPException(403)
    return deny
app = FastAPI()
app.include_router(create_router(policy, auditoria=AuditChain()))
with TestClient(app) as client:
    for method, path, body in [
        ('POST', '/probe', {'host': '127.0.0.1', 'port': 80}),
        ('POST', '/slo/avaliar', {'indisponibilidades': []}),
        ('POST', '/incidentes/metricas', []),
        ('POST', '/anomalias', {'serie': [1, 2]}),
        ('GET', '/auditoria/verificar', None),
    ]:
        assert client.request(method, '/api/eng' + path, json=body).status_code == 403
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'test-results/package.json')
    args = parser.parse_args()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    report = {'status': 'running', 'checks': [], 'provider': 'none'}
    env = {k: v for k, v in os.environ.items() if k not in {'PYTHONPATH', 'PYTHONHOME'}}
    env['PIP_DISABLE_PIP_VERSION_CHECK'] = '1'
    temp_root = ROOT / 'test-results'
    temp_root.mkdir(exist_ok=True)

    def run(command, cwd):
        r = subprocess.run(command, cwd=cwd, env=env, text=True, capture_output=True,
                           encoding='utf-8', errors='replace', timeout=240)
        if r.returncode:
            raise RuntimeError((r.stderr + r.stdout)[-4000:])
        return r.stdout.strip()

    def passed(name):
        report['checks'].append({'name': name, 'passed': True})
        print('PASS: ' + name, flush=True)

    def interpreter(directory):
        venv.create(directory, with_pip=True)
        return str(directory / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python'))

    try:
        with tempfile.TemporaryDirectory(prefix='sigma-package-', dir=temp_root) as tmp:
            work = Path(tmp).resolve()
            if not work.is_relative_to(temp_root.resolve()):
                raise RuntimeError('Diretório temporário fora do destino previsto.')
            outside = work / 'outside'
            outside.mkdir()
            editable = interpreter(work / 'editable')
            run([editable, '-m', 'pip', 'install', '-e', str(ROOT / 'engenharia')], outside)
            run([editable, '-I', '-c', CORE_CHECK], outside)
            passed('editable_core_outside_checkout_without_api_dependencies')

            # A mesma forma exigida no CI: pip install -e .[dev], dentro de engenharia.
            run([editable, '-m', 'pip', 'install', '-e', '.[dev]'], ROOT / 'engenharia')
            run([editable, '-I', '-c', API_CHECK], outside)
            run([editable, '-m', 'pip', 'check'], outside)
            passed('editable_dev_api_outside_checkout_with_required_authorization')

            wheels = output.parent / (output.stem + '-wheels')
            wheels.mkdir(exist_ok=True)
            run([editable, '-m', 'pip', 'wheel', '--no-deps', '--wheel-dir', str(wheels),
                 str(ROOT / 'engenharia')], outside)
            wheel = wheels / 'sigma_eng-0.1.0-py3-none-any.whl'
            with zipfile.ZipFile(wheel) as archive:
                names = archive.namelist()
                if not all(n.startswith(('sigma_eng/', 'sigma_eng-0.1.0.dist-info/')) for n in names):
                    raise RuntimeError('Wheel contém arquivos fora do pacote e seus metadados.')
                if any(n.endswith(('.jsonl', '.env', '.json')) for n in names):
                    raise RuntimeError('Wheel contém artefatos de execução inesperados.')
            report['wheel_sha256'] = hashlib.sha256(wheel.read_bytes()).hexdigest()
            report['wheel'] = wheel.name
            passed('wheel_contains_only_package_and_metadata')

            regular = interpreter(work / 'regular')
            run([regular, '-m', 'pip', 'install', '--no-deps', str(wheel)], outside)
            origin = run([regular, '-I', '-c', CORE_CHECK], outside)
            if (ROOT / 'engenharia').resolve() in Path(origin).resolve().parents:
                raise RuntimeError('O import da wheel ainda depende do checkout.')
            passed('regular_wheel_import_outside_checkout_without_api_dependencies')
            run([regular, '-m', 'pip', 'install', str(wheel) + '[api]'], outside)
            run([regular, '-I', '-c', 'import sigma_eng.api; import sys; assert "auth" not in sys.modules'], outside)
            run([regular, '-m', 'pip', 'check'], outside)
            passed('regular_wheel_api_extra_without_host_modules')
        report['status'] = 'passed'
    except Exception as exc:
        report['status'] = 'failed'
        report['error'] = str(exc)
        print('FAIL: ' + str(exc), flush=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
