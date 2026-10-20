import os


def test_panel_real_browser_approval_health_and_sse(pg):
    from scripts.validate_panel import run
    assert run(os.environ["SIGMA_TEST_DATABASE_URL"])["exit_code"] == 0
