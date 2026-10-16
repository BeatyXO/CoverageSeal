# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
"""A real IC consumer: only a pin-matched COMPLETE snapshot unlocks a one-time action."""
from genlayer import *
from dataclasses import dataclass

@gl.contract_interface
class ICoverageSeal:
    class View:
        def is_complete(self, package_id: u256, schema_hash: str, package_hash: str, snapshot_hash: str) -> bool: ...
    class Write:
        pass

@allow_storage
@dataclass
class Execution:
    executor: Address
    package_id: u256
    schema_hash: str
    package_hash: str
    snapshot_hash: str
    payload_hash: str

class CoverageGate(gl.Contract):
    source: Address
    executions: TreeMap[str, Execution]
    executed_count: u256

    def __init__(self, coverage_seal_address: Address):
        self.source = coverage_seal_address
        self.executed_count = u256(0)

    @gl.public.write
    def execute(self, package_id: u256, schema_hash: str, package_hash: str, snapshot_hash: str,
                action_hash: str, payload_hash: str) -> None:
        values = [schema_hash, package_hash, snapshot_hash, action_hash, payload_hash]
        for value in values:
            if len(value) != 64 or any(char not in '0123456789abcdef' for char in value):
                raise gl.vm.UserError('expected lowercase 64-hex digest')
        if action_hash in self.executions:
            raise gl.vm.UserError('action replay')
        if not ICoverageSeal(self.source).view().is_complete(package_id, schema_hash, package_hash, snapshot_hash):
            raise gl.vm.UserError('coverage certificate missing or mismatched')
        self.executions[action_hash] = Execution(gl.message.sender_address, package_id, schema_hash, package_hash, snapshot_hash, payload_hash)
        self.executed_count = u256(int(self.executed_count) + 1)

    @gl.public.view
    def was_executed(self, action_hash: str) -> bool:
        return action_hash in self.executions

    @gl.public.view
    def get_execution(self, action_hash: str) -> dict:
        if action_hash not in self.executions:
            raise gl.vm.UserError('unknown action')
        a = self.executions[action_hash]
        return {'executor': str(a.executor), 'package_id': int(a.package_id), 'schema_hash': a.schema_hash,
                'package_hash': a.package_hash, 'snapshot_hash': a.snapshot_hash, 'payload_hash': a.payload_hash}
