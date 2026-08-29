import hashlib
import json
import sys
from pathlib import Path

import pytest
from gltest.direct.loader import deploy_contract
from gltest.direct.vm import VMContext


CONTRACT = Path(__file__).parents[2] / "contracts" / "appeal_ground_response_coverage_covenant.py"
OWNER = "0x1111111111111111111111111111111111111111"
AUTHORITY = "0x2222222222222222222222222222222222222222"
READER = "0x3333333333333333333333333333333333333333"
OTHER = "0x4444444444444444444444444444444444444444"
APPEAL = "appeal-001"
ORIGINAL_URL = "https://appeals.example.org/original.txt"
GROUNDS_URL = "https://appeals.example.org/grounds.txt"
RESPONSE_URL = "https://authority.example.org/response.txt"
CORRECTION_URL = "https://authority.example.org/correction.txt"
ORIGINAL = "Original decision: the institution issued a final decision."
GROUNDS = json.dumps([{"ground_id": "g1", "text": "The decision omitted the reason."}, {"ground_id": "g2", "text": "The decision did not address the requested remedy."}], separators=(",", ":"))
RESPONSE = "Final response: Ground g1 is addressed with a reason. Ground g2 remedy is granted with reasons."
CORRECTION = "Corrected response: Ground g1 is addressed with a reason. Ground g2 remedy is granted with reasons."


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def reset_genlayer_state():
    for module in list(sys.modules.values()):
        if hasattr(module, "__known_contract__"):
            module.__known_contract__ = None


@pytest.fixture
def env():
    reset_genlayer_state()
    vm = VMContext()
    vm.strict_mocks = True
    vm.check_pickling = True
    vm.sender = OWNER
    vm.warp("2026-08-20T00:00:00Z")
    contract = deploy_contract(str(CONTRACT), vm)
    with vm.activate():
        yield vm, contract


def seed(vm, contract):
    vm.sender = OWNER
    contract.file_appeal(APPEAL, ORIGINAL_URL, digest(ORIGINAL), GROUNDS_URL, digest(GROUNDS), GROUNDS, AUTHORITY, READER)
    contract.lock_grounds(APPEAL)
    vm.sender = AUTHORITY
    contract.submit_response(APPEAL, RESPONSE_URL, digest(RESPONSE), "rev-1")


def accepted_llm(digest_value, covered=True):
    result = [
        {"ground_id": "g1", "identity_match": True, "disposition_present": True, "reason_relevant": True},
        {"ground_id": "g2", "identity_match": covered, "disposition_present": covered, "reason_relevant": covered},
    ]
    return json.dumps({"ground_identity_match": covered, "disposition_present": covered, "reason_relevant": covered, "omitted_ground_ids": [] if covered else ["g2"], "ground_results": result, "reason": "All locked grounds are addressed.", "references": [RESPONSE_URL], "evidence_digest": digest_value})


def setup_assessment(vm, contract, llm_output, response=RESPONSE, response_url=RESPONSE_URL, revision="rev-1"):
    seed(vm, contract)
    expected = digest(json.dumps({"original_hash": digest(ORIGINAL), "grounds_hash": digest(GROUNDS), "response_hash": digest(response), "revision": revision}, sort_keys=True, separators=(",", ":")))
    vm.mock_web(r"appeals\.example\.org/original", {"status": 200, "body": ORIGINAL})
    vm.mock_web(r"appeals\.example\.org/grounds", {"status": 200, "body": GROUNDS})
    vm.mock_web(r"authority\.example\.org/(?:response|correction)", {"status": 200, "body": response})
    vm.mock_llm(r"You evaluate whether", llm_output(expected))


def test_file_lock_submit_and_view(env):
    vm, contract = env
    seed(vm, contract)
    data = json.loads(contract.read_case(APPEAL))
    assert data["status"] == "RESPONSE_SUBMITTED"
    assert data["ground_ids"] == ["g1", "g2"]
    assert [item["evidence_revision"] for item in data["revision_history"]] == ["rev-1"]


def test_studio_numeric_address_inputs_are_coerced(env):
    vm, contract = env
    vm.sender = OWNER
    contract.file_appeal(
        APPEAL,
        ORIGINAL_URL,
        digest(ORIGINAL),
        GROUNDS_URL,
        digest(GROUNDS),
        GROUNDS,
        int(AUTHORITY, 16),
        int(READER, 16),
    )
    assert json.loads(contract.read_case(APPEAL))["status"] == "FILED"


def test_invalid_numeric_address_inputs_are_rejected(env):
    vm, contract = env
    vm.sender = OWNER
    for index, bad_address in enumerate((True, False, 0), start=1):
        with vm.expect_revert("nonzero 160-bit"):
            contract.file_appeal(
                f"appeal-invalid-address-{index}",
                ORIGINAL_URL,
                digest(ORIGINAL),
                GROUNDS_URL,
                digest(GROUNDS),
                GROUNDS,
                bad_address,
                int(READER, 16),
            )


def test_auth_and_invalid_transition(env):
    vm, contract = env
    seed(vm, contract)
    vm.sender = OTHER
    with vm.expect_revert("only responding authority"):
        contract.submit_response(APPEAL, RESPONSE_URL, digest(RESPONSE), "rev-1")
    vm.sender = OWNER
    with vm.expect_revert("only owner may lock"):
        contract.lock_grounds(APPEAL)


def test_duplicate_filing_and_ground_bounds_are_rejected(env):
    vm, contract = env
    vm.sender = OWNER
    contract.file_appeal(APPEAL, ORIGINAL_URL, digest(ORIGINAL), GROUNDS_URL, digest(GROUNDS), GROUNDS, AUTHORITY, READER)
    with vm.expect_revert("already exists"):
        contract.file_appeal(APPEAL, ORIGINAL_URL, digest(ORIGINAL), GROUNDS_URL, digest(GROUNDS), GROUNDS, AUTHORITY, READER)
    duplicate = json.dumps([{"ground_id": "g1", "text": "one"}, {"ground_id": "g1", "text": "two"}])
    with vm.expect_revert("unique"):
        contract.file_appeal("appeal-duplicate-ground", ORIGINAL_URL, digest(ORIGINAL), GROUNDS_URL, digest(duplicate), duplicate, AUTHORITY, READER)
    too_many = json.dumps([{"ground_id": f"g{i}", "text": "ground"} for i in range(9)])
    with vm.expect_revert("1 to 8"):
        contract.file_appeal("appeal-too-many", ORIGINAL_URL, digest(ORIGINAL), GROUNDS_URL, digest(too_many), too_many, AUTHORITY, READER)
    too_long = json.dumps([{"ground_id": "g1", "text": "x" * 601}])
    with vm.expect_revert("ground text"):
        contract.file_appeal("appeal-long-ground", ORIGINAL_URL, digest(ORIGINAL), GROUNDS_URL, digest(too_long), too_long, AUTHORITY, READER)


def test_covered_response_closes(env):
    vm, contract = env
    setup_assessment(vm, contract, accepted_llm)
    contract.assess_coverage(APPEAL)
    vm.sender = OWNER
    contract.close_case(APPEAL)
    assert json.loads(contract.read_case(APPEAL))["status"] == "CLOSED"


def test_gap_correction_requires_reassessment(env):
    vm, contract = env
    setup_assessment(vm, contract, lambda value: accepted_llm(value, covered=False))
    contract.assess_coverage(APPEAL)
    assert json.loads(contract.read_case(APPEAL))["status"] == "GAPS_FOUND"
    with vm.expect_revert("only a covered appeal"):
        vm.sender = OWNER
        contract.close_case(APPEAL)
    vm.sender = AUTHORITY
    contract.correct_response(APPEAL, CORRECTION_URL, digest(CORRECTION), "rev-2")
    corrected = json.loads(contract.read_case(APPEAL))
    assert corrected["status"] == "CORRECTED"
    assert [item["evidence_revision"] for item in corrected["revision_history"]] == ["rev-1", "rev-2"]


def test_correction_replay_and_aggregate_mismatch_fail(env):
    vm, contract = env
    setup_assessment(vm, contract, lambda value: accepted_llm(value, covered=False))
    contract.assess_coverage(APPEAL)
    vm.sender = AUTHORITY
    with vm.expect_revert("already exists"):
        contract.correct_response(APPEAL, CORRECTION_URL, digest(CORRECTION), "rev-1")


def test_revision_reuse_across_history_is_rejected(env):
    vm, contract = env
    setup_assessment(vm, contract, lambda value: accepted_llm(value, covered=False))
    contract.assess_coverage(APPEAL)
    vm.sender = AUTHORITY
    contract.correct_response(APPEAL, CORRECTION_URL, digest(CORRECTION), "rev-2")
    with vm.expect_revert("already exists"):
        contract.submit_response(APPEAL, RESPONSE_URL, digest(RESPONSE), "rev-1")
    with vm.expect_revert("already exists"):
        contract.submit_response(APPEAL, RESPONSE_URL, digest("different response"), "rev-2")


def test_aggregate_mismatch_fails_closed(env):
    vm, contract = env
    seed(vm, contract)
    vm.mock_web(r"appeals\.example\.org/original", {"status": 200, "body": ORIGINAL})
    vm.mock_web(r"appeals\.example\.org/grounds", {"status": 200, "body": GROUNDS})
    vm.mock_web(r"authority\.example\.org/response", {"status": 200, "body": RESPONSE})
    expected = digest(json.dumps({"original_hash": digest(ORIGINAL), "grounds_hash": digest(GROUNDS), "response_hash": digest(RESPONSE), "revision": "rev-1"}, sort_keys=True, separators=(",", ":")))
    bad = json.loads(accepted_llm(expected))
    bad["ground_identity_match"] = False
    vm.mock_llm(r"You evaluate whether", json.dumps(bad))
    with vm.expect_revert("aggregate"):
        contract.assess_coverage(APPEAL)


def test_bad_evidence_fails_closed(env):
    vm, contract = env
    seed(vm, contract)
    vm.mock_web(r"appeals\.example\.org/original", {"status": 200, "body": "changed"})
    with vm.expect_revert("evidence digest"):
        contract.assess_coverage(APPEAL)


def test_hash_verified_but_different_grounds_fail_closed(env):
    vm, contract = env
    different_grounds = json.dumps([{"ground_id": "g1", "text": "The decision omitted the reason."}, {"ground_id": "g3", "text": "A different ground."}], separators=(",", ":"))
    vm.sender = OWNER
    contract.file_appeal(APPEAL, ORIGINAL_URL, digest(ORIGINAL), GROUNDS_URL, digest(different_grounds), GROUNDS, AUTHORITY, READER)
    contract.lock_grounds(APPEAL)
    vm.sender = AUTHORITY
    contract.submit_response(APPEAL, RESPONSE_URL, digest(RESPONSE), "rev-1")
    vm.mock_web(r"appeals\.example\.org/original", {"status": 200, "body": ORIGINAL})
    vm.mock_web(r"appeals\.example\.org/grounds", {"status": 200, "body": different_grounds})
    with vm.expect_revert("does not match filed grounds"):
        contract.assess_coverage(APPEAL)
    assert json.loads(contract.read_case(APPEAL))["status"] == "RESPONSE_SUBMITTED"


def test_validator_agreement_and_disagreement_bind_vector(env):
    vm, contract = env
    setup_assessment(vm, contract, accepted_llm)
    contract.assess_coverage(APPEAL)
    assert vm.run_validator() is True
    vm.clear_mocks()
    expected = digest(json.dumps({"original_hash": digest(ORIGINAL), "grounds_hash": digest(GROUNDS), "response_hash": digest(RESPONSE), "revision": "rev-1"}, sort_keys=True, separators=(",", ":")))
    vm.mock_web(r"appeals\.example\.org/original", {"status": 200, "body": ORIGINAL})
    vm.mock_web(r"appeals\.example\.org/grounds", {"status": 200, "body": GROUNDS})
    vm.mock_web(r"authority\.example\.org/response", {"status": 200, "body": RESPONSE})
    vm.mock_llm(r"You evaluate whether", accepted_llm(expected, covered=False))
    assert vm.run_validator() is False


def test_private_evidence_endpoint_is_rejected(env):
    vm, contract = env
    vm.sender = OWNER
    with vm.expect_revert("must be public"):
        contract.file_appeal(APPEAL, "https://127.0.0.1/original", digest(ORIGINAL), GROUNDS_URL, digest(GROUNDS), GROUNDS, AUTHORITY, READER)


def test_malformed_consensus_output_writes_no_state(env):
    vm, contract = env
    seed(vm, contract)
    vm.mock_web(r"appeals\.example\.org/original", {"status": 200, "body": ORIGINAL})
    vm.mock_web(r"appeals\.example\.org/grounds", {"status": 200, "body": GROUNDS})
    vm.mock_web(r"authority\.example\.org/response", {"status": 200, "body": RESPONSE})
    vm.mock_llm(r"You evaluate whether", '{"unexpected": true}')
    with vm.expect_revert():
        contract.assess_coverage(APPEAL)
    assert json.loads(contract.read_case(APPEAL))["status"] == "RESPONSE_SUBMITTED"


def test_consensus_rejection_writes_no_state(env, monkeypatch):
    vm, contract = env
    seed(vm, contract)
    vm.mock_web(r"appeals\.example\.org/original", {"status": 200, "body": ORIGINAL})
    vm.mock_web(r"appeals\.example\.org/grounds", {"status": 200, "body": GROUNDS})
    vm.mock_web(r"authority\.example\.org/response", {"status": 200, "body": RESPONSE})
    expected = digest(json.dumps({"original_hash": digest(ORIGINAL), "grounds_hash": digest(GROUNDS), "response_hash": digest(RESPONSE), "revision": "rev-1"}, sort_keys=True, separators=(",", ":")))
    vm.mock_llm(r"You evaluate whether", accepted_llm(expected))

    import genlayer.gl.vm as gl_vm

    def reject_consensus(leader_fn, validator_fn):
        leader_fn()
        raise gl_vm.UserError("consensus disagreement")

    monkeypatch.setattr(gl_vm, "run_nondet_unsafe", reject_consensus)
    with vm.expect_revert("consensus disagreement"):
        contract.assess_coverage(APPEAL)
    assert json.loads(contract.read_case(APPEAL))["status"] == "RESPONSE_SUBMITTED"
