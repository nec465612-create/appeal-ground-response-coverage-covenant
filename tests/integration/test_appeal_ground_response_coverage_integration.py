import json
from pathlib import Path

import pytest
from gltest.direct.loader import deploy_contract
from gltest.direct.vm import VMContext

from tests.direct.test_appeal_ground_response_coverage_covenant import (
    APPEAL,
    AUTHORITY,
    CORRECTION,
    CORRECTION_URL,
    CONTRACT,
    GROUNDS,
    GROUNDS_URL,
    ORIGINAL,
    ORIGINAL_URL,
    OWNER,
    READER,
    RESPONSE,
    RESPONSE_URL,
    accepted_llm,
    digest,
    reset_genlayer_state,
)


@pytest.fixture
def integration_env():
    reset_genlayer_state()
    vm = VMContext()
    vm.strict_mocks = True
    vm.check_pickling = True
    vm.sender = OWNER
    vm.warp("2026-08-20T00:00:00Z")
    contract = deploy_contract(str(CONTRACT), vm)
    with vm.activate():
        yield vm, contract


def mock_assessment(vm, response=RESPONSE, revision="rev-1", covered=True):
    vm.clear_mocks()
    evidence_digest = digest(json.dumps({"original_hash": digest(ORIGINAL), "grounds_hash": digest(GROUNDS), "response_hash": digest(response), "revision": revision}, sort_keys=True, separators=(",", ":")))
    vm.mock_web(r"appeals\.example\.org/original", {"status": 200, "body": ORIGINAL})
    vm.mock_web(r"appeals\.example\.org/grounds", {"status": 200, "body": GROUNDS})
    vm.mock_web(r"authority\.example\.org/(?:response|correction)", {"status": 200, "body": response})
    vm.mock_llm(r"You evaluate whether", accepted_llm(evidence_digest, covered=covered))


def prepare(vm, contract, response=RESPONSE, response_url=RESPONSE_URL, revision="rev-1", covered=True):
    vm.sender = OWNER
    contract.file_appeal(APPEAL, ORIGINAL_URL, digest(ORIGINAL), GROUNDS_URL, digest(GROUNDS), GROUNDS, AUTHORITY, READER)
    contract.lock_grounds(APPEAL)
    vm.sender = AUTHORITY
    contract.submit_response(APPEAL, response_url, digest(response), revision)
    mock_assessment(vm, response, revision, covered)


def test_covered_lifecycle_is_executable(integration_env):
    vm, contract = integration_env
    prepare(vm, contract)
    contract.assess_coverage(APPEAL)
    vm.sender = OWNER
    contract.close_case(APPEAL)
    result = json.loads(contract.read_case(APPEAL))
    assert result["status"] == "CLOSED"
    assert result["closure_ready"] is True


def test_gap_correction_reassessment_lifecycle_is_executable(integration_env):
    vm, contract = integration_env
    prepare(vm, contract, covered=False)
    contract.assess_coverage(APPEAL)
    assert json.loads(contract.read_case(APPEAL))["status"] == "GAPS_FOUND"
    vm.sender = AUTHORITY
    contract.correct_response(APPEAL, CORRECTION_URL, digest(CORRECTION), "rev-2")
    corrected = json.loads(contract.read_case(APPEAL))
    assert corrected["status"] == "CORRECTED"
    assert [item["evidence_revision"] for item in corrected["revision_history"]] == ["rev-1", "rev-2"]
    mock_assessment(vm, CORRECTION, "rev-2", covered=True)
    contract.assess_coverage(APPEAL)
    vm.sender = OWNER
    contract.close_case(APPEAL)
    final = json.loads(contract.read_case(APPEAL))
    assert final["status"] == "CLOSED"
    assert final["closure_ready"] is True


def test_matrix_lists_all_required_scenarios():
    matrix = Path(__file__).parents[2] / "verification" / "e2e-matrix.md"
    text = matrix.read_text(encoding="utf-8")
    for scenario in ("AGRCC-01", "AGRCC-02", "AGRCC-03", "AGRCC-04", "AGRCC-05", "AGRCC-06"):
        assert scenario in text
