"""Regressões reais de política: exposição de bancos, binds e imagens alteradas."""

from copy import deepcopy
import json

import pytest

from scripts.validate_compose_credentials import CredentialChecks, ROOT, ValidationError
from scripts.validate_infrastructure import BINDS, image_map, render, validate_model


@pytest.fixture(scope="module")
def baseline():
    checks = CredentialChecks()
    lock = json.loads((ROOT / "docker-images.lock.json").read_text(encoding="utf-8"))
    model = render(checks, checks.valid_env)
    # As credenciais não participam desta política e não devem aparecer nem
    # na representação de uma fixture caso outro teste falhe.
    for service in model["services"].values():
        service.pop("environment", None)
    return model, lock


def validate(model, lock):
    validate_model(model, image_map(lock), {name: "127.0.0.1" for name in BINDS})


def test_valid_model(baseline):
    validate(*baseline)


@pytest.mark.parametrize("service", ["db", "postgres-server"])
def test_bank_cannot_publish_port(baseline, service):
    model, lock = deepcopy(baseline)
    model["services"][service]["ports"] = [{"target": 5432, "published": "5432", "host_ip": "127.0.0.1", "protocol": "tcp"}]
    with pytest.raises(ValidationError, match="bancos"):
        validate(model, lock)


@pytest.mark.parametrize("service", list(BINDS))
@pytest.mark.parametrize("address", ["0.0.0.0", "::"])
def test_wildcard_bind_is_rejected(baseline, service, address):
    model, lock = deepcopy(baseline)
    model["services"][service]["ports"][0]["host_ip"] = address
    with pytest.raises(ValidationError, match="Bind amplo"):
        validate(model, lock)


@pytest.mark.parametrize("address", ["::ffff:0.0.0.0", "::ffff:224.0.0.1"])
def test_ipv4_mapped_wildcard_or_multicast_is_rejected(baseline, address):
    model, lock = deepcopy(baseline)
    model["services"]["n8n"]["ports"][0]["host_ip"] = address
    with pytest.raises(ValidationError, match="Bind amplo"):
        validate(model, lock)


@pytest.mark.parametrize("image", ["postgres:15-alpine", "untrusted/postgres:15.19", "postgres:15.19-alpine3.24@sha256:" + "0" * 64])
def test_unpinned_foreign_or_altered_image_is_rejected(baseline, image):
    model, lock = deepcopy(baseline)
    model["services"]["db"]["image"] = image
    with pytest.raises(ValidationError, match="Imagem"):
        validate(model, lock)


@pytest.mark.parametrize(("key", "value"), [("published", "80"), ("target", 80), ("protocol", "udp"), ("host_ip", "")])
def test_changed_port_or_implicit_bind_is_rejected(baseline, key, value):
    model, lock = deepcopy(baseline)
    model["services"]["n8n"]["ports"][0][key] = value
    with pytest.raises(ValidationError):
        validate(model, lock)


def test_extra_port_is_rejected(baseline):
    model, lock = deepcopy(baseline)
    model["services"]["n8n"]["ports"].append({"target": 80, "published": "80", "host_ip": "127.0.0.1", "protocol": "tcp"})
    with pytest.raises(ValidationError, match="Publicações"):
        validate(model, lock)


def test_host_network_is_rejected(baseline):
    model, lock = deepcopy(baseline)
    model["services"]["n8n"]["network_mode"] = "host"
    with pytest.raises(ValidationError, match="Rede host"):
        validate(model, lock)


@pytest.mark.parametrize(("key", "value"), [("tag", "15-alpine"), ("tag", "latest"), ("tag", "16.0-alpine3.24"), ("digest", "sha256:invalid"), ("registry_repository", "untrusted/postgres")])
def test_lock_cannot_hide_moving_release_or_wrong_publisher(baseline, key, value):
    _, lock = deepcopy(baseline)
    lock["images"][0][key] = value
    with pytest.raises(ValidationError):
        image_map(lock)


# --- #56: a checagem que reprova PR não depende do Docker Hub -------------------

import sys

from scripts import validate_infrastructure as infra


def _lock():
    return json.loads((ROOT / "docker-images.lock.json").read_text(encoding="utf-8"))


def test_pr_workflow_has_no_registry_dependency():
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "--verify-registry" not in workflow and "--drift" not in workflow


def test_default_run_never_touches_the_network(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("a execução padrão não pode consultar a rede")

    monkeypatch.setattr(infra, "urlopen", forbidden)
    monkeypatch.setattr(sys, "argv", ["validate_infrastructure.py"])
    assert infra.main() == 0


def test_republished_tag_is_reported_but_never_fails():
    lock = _lock()
    other = "sha256:" + "a" * 64

    def republished(repository, reference):
        # A tag aponta para outro digest; o digest fixado continua existindo.
        return (other if not reference.startswith("sha256:") else reference), b""

    assert len(infra.registry_drift(lock, republished)) == len(lock["images"])
    assert infra.report_drift(lock, republished) == 0


def test_no_drift_when_tag_matches_lock():
    lock = _lock()
    by_tag = {e["tag"]: e["digest"] for e in lock["images"]}
    assert infra.registry_drift(lock, lambda repo, ref: (by_tag[ref], b"")) == []


def test_drift_check_tolerates_registry_outage():
    def down(repository, reference):
        raise OSError("sem rede")

    assert infra.report_drift(_lock(), down) == 0


def test_digest_mismatch_still_fails_the_integrity_check():
    lock = _lock()
    body = b'{"manifests": []}'
    wrong = "sha256:" + "b" * 64
    with pytest.raises(ValidationError, match="diverge do lock"):
        infra.verify_registry(lock, lambda repo, ref: (wrong, body))
