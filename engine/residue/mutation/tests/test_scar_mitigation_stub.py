from engine.residue.mutation import scar_mitigation_stub


def test_apply_scar_mitigation_is_bounded_and_not_erased():
    scarring = {"scar_intensity": 0.5, "hazard_bias": 0.3}
    rec = scar_mitigation_stub.apply_scar_mitigation("node_a", 2, scarring_record=scarring, mitigation_credit=0.25)
    assert 0.0 <= rec["mitigated_scar_intensity"] <= 1.0
    assert rec["mitigated_scar_intensity"] >= 0.10
    assert rec["mitigated_scar_intensity"] < rec["base_scar_intensity"]
    assert rec["bounded_flags_clean"] is True

