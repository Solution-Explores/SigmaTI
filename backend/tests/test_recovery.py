import hashlib
import hmac
import json
import os
import stat
from pathlib import Path
import pytest
from scripts import recovery
from sigma_eng.audit_chain import AuditChain


@pytest.fixture
def bundle(tmp_path,monkeypatch):
    monkeypatch.setenv("SIGMA_AUDIT_KEY","s"*64)
    folder=tmp_path/"bundle";folder.mkdir()
    (folder/"database.dump").write_bytes(b"synthetic-only")
    AuditChain(folder/"audit.jsonl",chave=recovery.key()).registrar("synthetic","test")
    data={"format":1,"postgres_major":15,"tables":{},"audit_entries":1,
          "files":{name:recovery.digest(folder/name) for name in ("database.dump","audit.jsonl")}}
    signed={"manifest":data,"hmac_sha256":hmac.new(recovery.key(),recovery.canonical(data),hashlib.sha256).hexdigest()}
    (folder/"manifest.json").write_text(json.dumps(signed),encoding="utf-8")
    return folder


def test_verify_authenticates_manifest_and_audit(bundle):
    assert recovery.verify(bundle)["audit_entries"]==1


@pytest.mark.parametrize("file",["database.dump","audit.jsonl","manifest.json"])
def test_tampered_bundle_is_rejected_before_database(bundle,file,monkeypatch,tmp_path):
    path=bundle/file;path.write_bytes(path.read_bytes().replace(b"synthetic",b"modified")+b"x")
    def forbidden(*args,**kwargs):pytest.fail("não deveria acessar o banco")
    monkeypatch.setattr(recovery,"docker",forbidden)
    with pytest.raises((ValueError,KeyError)):
        recovery.restore("target",bundle,tmp_path/"audit.jsonl",quiesced=True)


def test_wrong_key_is_rejected(bundle,monkeypatch):
    monkeypatch.setenv("SIGMA_AUDIT_KEY","wrong"*16)
    with pytest.raises(ValueError,match="autenticado"):
        recovery.verify(bundle)


def test_recovery_requires_offline_acknowledgement(bundle,tmp_path):
    with pytest.raises(ValueError,match="offline"):
        recovery.restore("target",bundle,tmp_path/"audit.jsonl")
    with pytest.raises(ValueError,match="escritores"):
        recovery.backup("source",bundle/"audit.jsonl",tmp_path/"new")


def test_existing_audit_is_not_overwritten(bundle,tmp_path,monkeypatch):
    target=tmp_path/"audit.jsonl";target.write_text("keep")
    monkeypatch.setattr(recovery,"docker",lambda *a,**kw:pytest.fail("não deveria acessar o banco"))
    with pytest.raises(ValueError,match="sobrescrito"):
        recovery.restore("target",bundle,target,quiesced=True)
    assert target.read_text()=="keep"


def test_backup_private_permissions_on_posix(tmp_path,monkeypatch):
    if os.name!="posix":pytest.skip("controle POSIX verificado no CI Linux")
    monkeypatch.setenv("SIGMA_AUDIT_KEY","s"*64)
    trail=tmp_path/"source.jsonl";AuditChain(trail,chave=recovery.key()).registrar("synthetic","test")
    monkeypatch.setattr(recovery,"fingerprint",lambda c:{})
    monkeypatch.setattr(recovery,"sql",lambda *a:"150000")
    def dump(*args,destination=None,**kwargs):destination.write(b"synthetic")
    monkeypatch.setattr(recovery,"docker",dump)
    output=tmp_path/"backup"
    recovery.backup("source",trail,output,quiesced=True)
    assert stat.S_IMODE(output.stat().st_mode)==0o700
    assert all(stat.S_IMODE(p.stat().st_mode)==0o600 for p in output.iterdir())
