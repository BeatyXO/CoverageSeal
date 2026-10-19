"""Direct Mode scenario/adversarial tests. Requires pinned genlayer-test and GenVM assets."""
import json
from Crypto.Hash import keccak
import pytest

C = 'contracts/coverage_seal.py'
BASE = 'https://raw.githubusercontent.com/BeatyXO/CoverageSeal/0123456789abcdef0123456789abcdef01234567/fixtures/'
URL_A = BASE + 'ownership.txt'
URL_B = BASE + 'finances.txt'
TEXT_A = 'Atlas Labs is owned by Ada (60 percent) and Bob (40 percent).'
TEXT_B = 'The company reported financial history for 2024 and 2025.'


def digest(s):
    k = keccak.new(digest_bits=256)
    k.update(s.encode())
    return k.hexdigest()


def setup(direct_vm, direct_deploy, policy=1, threshold=0, two=False, second=TEXT_B):
    c = direct_deploy(C, sdk_version="v0.3.0-rc7")
    sid = c.create_schema('Atlas due diligence', BASE)
    rid = c.add_requirement(sid, 'OWNERS', 'Identify the company owners and ownership percentages', policy, threshold)
    sh = c.seal_schema(sid)
    pid = c.create_package(sid, sh)
    a = c.add_artifact(pid, 'ownership', URL_A, digest(TEXT_A))
    b = None
    if two:
        b = c.add_artifact(pid, 'financials', URL_B, digest(second))
    ph = c.seal_package(pid)
    return c, sid, rid, pid, a, b, sh, ph


def mock_edge(vm, code, quote='', url=URL_A, text=TEXT_A):
    vm.mock_web(url.replace('.', r'\.'), {'status': 200, 'body': text})
    vm.mock_llm('COVERAGESEAL / COVERAGE EDGE', json.dumps({'code': code, 'quote': quote, 'reason': 'bounded decision'}))


def test_sealed_schema_has_definition_hash(direct_vm, direct_deploy):
    c, sid, rid, pid, aid, _, sh, ph = setup(direct_vm, direct_deploy)
    assert len(sh) == 64 and len(ph) == 64 and sh != ph
    assert c.get_schema(sid)['sealed'] is True
    assert c.get_package(pid)['schema_hash'] == sh
    assert c.get_requirement_id(sid, 1) == rid
    assert c.get_artifact_id(pid, 1) == aid
    assert not c.is_complete(pid, sh, ph, '0' * 64)


def test_schema_immutability(direct_vm, direct_deploy):
    c, sid, *_ = setup(direct_vm, direct_deploy)
    with direct_vm.expect_revert('schema locked'):
        c.add_requirement(sid, 'NEW', 'New field', 1, 0)


def test_source_namespace_and_replay_digest(direct_vm, direct_deploy):
    c = direct_deploy(C, sdk_version="v0.3.0-rc7")
    sid = c.create_schema('Domain', BASE)
    c.add_requirement(sid, 'R1', 'A valid substantive requirement', 1, 0)
    sh = c.seal_schema(sid)
    p = c.create_package(sid, sh)
    c.add_artifact(p, 'one', URL_A, digest(TEXT_A))
    with direct_vm.expect_revert('source outside'):
        c.add_artifact(p, 'evil', 'https://example.com/ownership.txt', 'a' * 64)
    with direct_vm.expect_revert('duplicate source'):
        c.add_artifact(p, 'duplicate', URL_B, digest(TEXT_A))
    with direct_vm.expect_revert('unsafe source'):
        c.add_artifact(p, 'traversal', BASE + '../escape.txt', 'b' * 64)


def test_invalid_policy_and_threshold(direct_vm, direct_deploy):
    c = direct_deploy(C, sdk_version="v0.3.0-rc7")
    sid = c.create_schema('Name', BASE)
    with direct_vm.expect_revert('partial threshold'):
        c.add_requirement(sid, 'R1', 'Requirement description', 2, 1)
    with direct_vm.expect_revert('invalid coverage policy'):
        c.add_requirement(sid, 'R1', 'Requirement description', 9, 0)


def test_fully_covered_and_hash_pinning(direct_vm, direct_deploy):
    c, sid, rid, pid, a, _, sh, ph = setup(direct_vm, direct_deploy)
    mock_edge(direct_vm, 3, 'Atlas Labs is owned by Ada (60 percent) and Bob (40 percent).')
    assert c.assess_artifact(pid, rid, a) == 3
    assert c.get_requirement_status(pid, rid)['status'] == 3
    snap = c.finalize_package(pid)
    assert len(snap) == 64 and c.is_complete(pid, sh, ph, snap)
    assert not c.is_complete(pid, 'f' * 64, ph, snap)
    assert not c.is_complete(pid, sh, 'e' * 64, snap)
    assert not c.is_complete(pid, sh, ph, 'd' * 64)
    with direct_vm.expect_revert('package not open'):
        c.assess_artifact(pid, rid, a)
    with direct_vm.expect_revert('package not finalizable'):
        c.finalize_package(pid)


def test_missing_coverage_fails_closed(direct_vm, direct_deploy):
    c, _, rid, pid, a, _, sh, ph = setup(direct_vm, direct_deploy)
    mock_edge(direct_vm, 1)
    c.assess_artifact(pid, rid, a)
    snap = c.finalize_package(pid)
    assert c.get_requirement_status(pid, rid)['status'] == 1
    assert c.get_package(pid)['status'] == 3
    assert not c.is_complete(pid, sh, ph, snap)


def test_partial_is_not_full(direct_vm, direct_deploy):
    c, _, rid, pid, a, _, _, _ = setup(direct_vm, direct_deploy)
    mock_edge(direct_vm, 2, TEXT_A)
    c.assess_artifact(pid, rid, a)
    assert c.get_requirement_status(pid, rid)['status'] == 2
    c.finalize_package(pid)
    assert c.get_package(pid)['status'] == 3


def test_unassessed_package_cannot_finalize(direct_vm, direct_deploy):
    c, _, rid, pid, a, _, _, _ = setup(direct_vm, direct_deploy)
    assert c.get_requirement_status(pid, rid)['status'] == 5
    with direct_vm.expect_revert('unresolved coverage'):
        c.finalize_package(pid)


def test_ungrounded_quote_is_ambiguous(direct_vm, direct_deploy):
    c, _, rid, pid, a, _, _, _ = setup(direct_vm, direct_deploy)
    mock_edge(direct_vm, 3, 'The unicorn controls every company')
    assert c.assess_artifact(pid, rid, a) == 4
    with direct_vm.expect_revert('unresolved coverage'):
        c.finalize_package(pid)


def test_source_digest_mismatch_is_unavailable(direct_vm, direct_deploy):
    c, _, rid, pid, a, _, _, _ = setup(direct_vm, direct_deploy)
    direct_vm.mock_web(r'ownership\.txt', {'status': 200, 'body': 'Tampered body'})
    assert c.assess_artifact(pid, rid, a) == 5
    with direct_vm.expect_revert('unresolved coverage'):
        c.finalize_package(pid)


def test_partial_combination_requires_pair_check(direct_vm, direct_deploy):
    c, _, rid, pid, a, b, sh, ph = setup(direct_vm, direct_deploy, 2, 2, True)
    direct_vm.mock_web(r'ownership\.txt', {'status': 200, 'body': TEXT_A})
    direct_vm.mock_web(r'finances\.txt', {'status': 200, 'body': TEXT_B})
    direct_vm.mock_llm('COVERAGESEAL / COVERAGE EDGE', json.dumps({'code': 2, 'quote': TEXT_B, 'reason': 'partial'}))
    # Both artifact edge quotes must be from their own sources. Override per call.
    direct_vm.clear_mocks()
    mock_edge(direct_vm, 2, TEXT_A)
    c.assess_artifact(pid, rid, a)
    direct_vm.clear_mocks()
    mock_edge(direct_vm, 2, TEXT_B, URL_B, TEXT_B)
    c.assess_artifact(pid, rid, b)
    assert c.get_requirement_status(pid, rid)['status'] == 5
    with direct_vm.expect_revert('unresolved coverage'):
        c.finalize_package(pid)
    direct_vm.clear_mocks()
    direct_vm.mock_web(r'ownership\.txt', {'status': 200, 'body': TEXT_A})
    direct_vm.mock_web(r'finances\.txt', {'status': 200, 'body': TEXT_B})
    direct_vm.mock_llm('COVERAGESEAL / REQUIREMENT CONTRADICTION', json.dumps({'code': 1, 'quote_left': '', 'quote_right': '', 'reason': 'not contradictory'}))
    c.assess_pair(pid, rid, a, b)
    assert c.get_requirement_status(pid, rid)['status'] == 3
    snap = c.finalize_package(pid)
    assert c.is_complete(pid, sh, ph, snap)


def test_duplicate_assessment_is_rejected(direct_vm, direct_deploy):
    c, _, rid, pid, a, _, _, _ = setup(direct_vm, direct_deploy)
    mock_edge(direct_vm, 1)
    c.assess_artifact(pid, rid, a)
    with direct_vm.expect_revert('already certified'):
        c.assess_artifact(pid, rid, a)


def test_wrong_schema_hash_prevents_new_package(direct_vm, direct_deploy):
    c = direct_deploy(C, sdk_version="v0.3.0-rc7")
    sid = c.create_schema('S', BASE)
    c.add_requirement(sid, 'R', 'A specific requirement', 1, 0)
    c.seal_schema(sid)
    with direct_vm.expect_revert('schema hash mismatch'):
        c.create_package(sid, 'a' * 64)


def test_private_source_prefix_rejected(direct_vm, direct_deploy):
    c = direct_deploy(C, sdk_version="v0.3.0-rc7")
    for bad in (
        'https://localhost/fixtures/', 'https://127.0.0.1/source/',
        'https://192.168.1.1/source/', 'https://bad.com@localhost/source/',
        'https://2130706433/source/', 'https://0177.0.0.1/source/',
        'https://[::1]/source/', 'https://safe.example/%2e%2e/private/',
        'https://safe.example/a/../private/', 'https://safe.example//private/',
        'https://safe.example:443/source/',
    ):
        print('checking', bad)
        with direct_vm.expect_revert('absolute HTTPS namespace'):
            c.create_schema('Bad namespace', bad)


def test_encoded_or_delimited_source_path_rejected(direct_vm, direct_deploy):
    c = direct_deploy(C, sdk_version="v0.3.0-rc7")
    sid = c.create_schema('Safe namespace', BASE)
    c.add_requirement(sid, 'R1', 'A bounded test requirement', 1, 0)
    sh = c.seal_schema(sid)
    pid = c.create_package(sid, sh)
    for suffix in ('%2e%2e/escape.txt', 'a%2fb.txt', 'a\\b.txt', 'file.txt?x=1', 'file.txt#part', '../escape.txt'):
        with direct_vm.expect_revert('source outside'):
            c.add_artifact(pid, 'bad', BASE + suffix, 'a' * 64)


def test_malformed_semantic_result_fails_closed(direct_vm, direct_deploy):
    c, _, rid, pid, aid, _, _, _ = setup(direct_vm, direct_deploy)
    direct_vm.mock_web(r'ownership\.txt', {'status': 200, 'body': TEXT_A})
    direct_vm.mock_llm('COVERAGESEAL / COVERAGE EDGE', json.dumps({'code': '3', 'quote': TEXT_A, 'reason': 'coerced code'}))
    assert c.assess_artifact(pid, rid, aid) == 4
    assert c.get_assessment(pid, rid, aid)['quote'] == ''
    with direct_vm.expect_revert('unresolved coverage'):
        c.finalize_package(pid)


def test_validator_refetch_rejects_forged_quote_and_disagreement(direct_vm, direct_deploy):
    c, _, rid, pid, aid, _, _, _ = setup(direct_vm, direct_deploy)
    mock_edge(direct_vm, 3, TEXT_A)
    assert c.assess_artifact(pid, rid, aid) == 3
    candidate = {
        'code': 3, 'quote': TEXT_A, 'reason': 'bounded decision',
        'source_digest': digest(TEXT_A),
    }
    # Direct Mode explicitly executes the contract's captured validator.
    assert direct_vm.run_validator(leader_result=candidate) is True
    forged = dict(candidate, quote='This sentence does not exist in the document.')
    assert direct_vm.run_validator(leader_result=forged) is False
    assert direct_vm.run_validator(leader_result=dict(candidate, source_digest='0' * 64)) is False

    # Validator independently re-fetches and classifies; disagreement rejects.
    direct_vm.clear_mocks()
    direct_vm.mock_web(r'ownership\.txt', {'status': 200, 'body': TEXT_A})
    direct_vm.mock_llm('COVERAGESEAL / COVERAGE EDGE', json.dumps({'code': 1, 'quote': '', 'reason': 'validator disagreement'}))
    assert direct_vm.run_validator(leader_result=candidate) is False


def test_contradictory_full_documents_block_completion(direct_vm, direct_deploy):
    contradictory = 'Atlas Labs is owned entirely by Cara (100 percent), with no other shareholders.'
    c, sid, rid, pid, a, b, sh, ph = setup(direct_vm, direct_deploy, two=True, second=contradictory)
    direct_vm.mock_web(r'ownership\.txt', {'status': 200, 'body': TEXT_A})
    direct_vm.mock_web(r'finances\.txt', {'status': 200, 'body': contradictory})
    direct_vm.mock_llm('COVERAGESEAL / COVERAGE EDGE', json.dumps({'code': 3, 'quote': TEXT_A, 'reason': 'full'}))
    c.assess_artifact(pid, rid, a)
    direct_vm.clear_mocks()
    mock_edge(direct_vm, 3, contradictory, URL_B, contradictory)
    c.assess_artifact(pid, rid, b)
    with direct_vm.expect_revert('pair IDs must be ascending'):
        c.assess_pair(pid, rid, b, a)
    direct_vm.clear_mocks()
    direct_vm.mock_web(r'ownership\.txt', {'status': 200, 'body': TEXT_A})
    direct_vm.mock_web(r'finances\.txt', {'status': 200, 'body': contradictory})
    direct_vm.mock_llm('COVERAGESEAL / REQUIREMENT CONTRADICTION', json.dumps({
        'code': 2, 'quote_left': TEXT_A, 'quote_right': contradictory,
        'reason': 'incompatible shares'}))
    assert c.assess_pair(pid, rid, a, b) == 2
    candidate = {
        'code': 2, 'quote_left': TEXT_A, 'quote_right': contradictory,
        'reason': 'incompatible shares', 'left_digest': digest(TEXT_A),
        'right_digest': digest(contradictory),
    }
    assert direct_vm.run_validator(leader_result=candidate) is True
    assert direct_vm.run_validator(leader_result=dict(candidate, quote_right='fabricated excerpt')) is False
    assert direct_vm.run_validator(leader_result=dict(candidate, right_digest='0' * 64)) is False
    assert direct_vm.run_validator(leader_result=dict(candidate, code=1, quote_left='', quote_right='')) is False
    assert c.get_requirement_status(pid, rid)['status'] == 4
    snap = c.finalize_package(pid)
    assert not c.is_complete(pid, sh, ph, snap)


def test_unauthorized_package_cannot_finalize(direct_vm, direct_deploy, direct_bob):
    c, _, rid, pid, a, _, _, _ = setup(direct_vm, direct_deploy)
    mock_edge(direct_vm, 1)
    c.assess_artifact(pid, rid, a)
    with direct_vm.prank(direct_bob):
        with direct_vm.expect_revert('not finalizable'):
            c.finalize_package(pid)


def test_conflict_cannot_hide_unassessed_artifact(direct_vm, direct_deploy):
    c = direct_deploy(C, sdk_version='v0.3.0-rc7')
    sid = c.create_schema('Complete assessment', BASE)
    rid = c.add_requirement(sid, 'OWNERS', 'Identify owners and percentages', 1, 0)
    sh = c.seal_schema(sid)
    pid = c.create_package(sid, sh)
    contrary = 'Cara owns 100 percent of Atlas Labs.'
    a = c.add_artifact(pid, 'first', URL_A, digest(TEXT_A))
    b = c.add_artifact(pid, 'second', URL_B, digest(contrary))
    third_url = BASE + 'third.txt'
    third_text = 'Additional evidence remains unassessed.'
    third = c.add_artifact(pid, 'third', third_url, digest(third_text))
    c.seal_package(pid)
    mock_edge(direct_vm, 3, TEXT_A)
    c.assess_artifact(pid, rid, a)
    direct_vm.clear_mocks()
    mock_edge(direct_vm, 3, contrary, URL_B, contrary)
    c.assess_artifact(pid, rid, b)
    direct_vm.clear_mocks()
    direct_vm.mock_web(r'ownership\.txt', {'status': 200, 'body': TEXT_A})
    direct_vm.mock_web(r'finances\.txt', {'status': 200, 'body': contrary})
    direct_vm.mock_llm('COVERAGESEAL / REQUIREMENT CONTRADICTION', json.dumps({
        'code': 2, 'quote_left': TEXT_A, 'quote_right': contrary, 'reason': 'conflict'}))
    c.assess_pair(pid, rid, a, b)
    detail = c.get_requirement_status(pid, rid)
    assert detail['status'] == 4 and detail['unresolved'] is True
    with direct_vm.expect_revert('unresolved coverage'):
        c.finalize_package(pid)
    assert c.get_package(pid)['status'] == 1
    direct_vm.clear_mocks()
    mock_edge(direct_vm, 1, '', third_url, third_text)
    c.assess_artifact(pid, rid, third)
    c.finalize_package(pid)
    assert c.get_package(pid)['status'] == 3
