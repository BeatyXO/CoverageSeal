"""Portable checks that run without GenVM packages or network access."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def parse(name):
    return ast.parse((ROOT / 'contracts' / name).read_text())


def test_both_contracts_compile():
    for name in ('coverage_seal.py', 'coverage_gate.py'):
        ast.parse((ROOT / 'contracts' / name).read_text())


def test_nondeterminism_is_consensus_wrapped():
    source = (ROOT / 'contracts/coverage_seal.py').read_text()
    assert 'run_nondet_unsafe(leader_fn, validator_fn)' in source
    assert source.count('run_nondet_unsafe(') == 2
    assert 'independent = _edge_once(' in source
    assert 'independent = _pair_once(' in source
    assert '_quote_in(candidate[' in source
    assert 'Keccak256(content)' in source


def test_gate_uses_typed_read_and_replay_protection():
    source = (ROOT / 'contracts/coverage_gate.py').read_text()
    assert '@gl.contract_interface' in source
    assert '.view().is_complete(' in source
    assert 'if action_hash in self.executions:' in source


def test_deterministic_completeness_not_llm_final_decision():
    tree = parse('coverage_seal.py')
    methods = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    for name in ('finalize_package', '_requirement_summary', 'seal_schema', 'seal_package'):
        fn = next(x for x in methods if x.name == name)
        calls = [x for x in ast.walk(fn) if isinstance(x, ast.Call)]
        assert not any(isinstance(c.func, ast.Attribute) and c.func.attr == 'exec_prompt' for c in calls)
