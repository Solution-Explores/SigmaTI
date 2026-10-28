# tests/test_infrastructure_policy.py

- baseline · function · L13-L21 — def baseline()
- validate · function · L24-L25 — def validate(model, lock)
- test_valid_model · function · L28-L29 — def test_valid_model(baseline)
- test_bank_cannot_publish_port · function · L33-L37 — def test_bank_cannot_publish_port(baseline, service)
- test_wildcard_bind_is_rejected · function · L42-L46 — def test_wildcard_bind_is_rejected(baseline, service, address)
- test_ipv4_mapped_wildcard_or_multicast_is_rejected · function · L50-L54 — def test_ipv4_mapped_wildcard_or_multicast_is_rejected(baseline, address)
- test_unpinned_foreign_or_altered_image_is_rejected · function · L58-L62 — def test_unpinned_foreign_or_altered_image_is_rejected(baseline, image)
- test_changed_port_or_implicit_bind_is_rejected · function · L66-L70 — def test_changed_port_or_implicit_bind_is_rejected(baseline, key, value)
- test_extra_port_is_rejected · function · L73-L77 — def test_extra_port_is_rejected(baseline)
- test_host_network_is_rejected · function · L80-L84 — def test_host_network_is_rejected(baseline)
- test_lock_cannot_hide_moving_release_or_wrong_publisher · function · L88-L92 — def test_lock_cannot_hide_moving_release_or_wrong_publisher(baseline, key, value)
