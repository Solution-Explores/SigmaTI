from pathlib import Path
import os


def test_e2_thirty_failures_200_targets_restart_and_sse(pg):
    from scripts.validate_collection import run
    report = run(os.environ["SIGMA_TEST_DATABASE_URL"], Path("test-results/collection-e2.json"))
    assert report["repetitions"] == 30
    assert report["within_5_seconds"] == 1
    assert report["load"]["targets"] == 200
