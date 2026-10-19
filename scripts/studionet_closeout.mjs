/** Resumable, receipt-backed closeout. Uses the installed official CLI SDK.
 * GENLAYER_NODE_ROOT points to the CLI package directory. Signing keys stay in
 * the OS keychain and memory; they are never printed or written to the journal.
 * Default is read-only legacy verification. --execute deploys corrected sources
 * and runs the lifecycle with the existing coverageSealThrowaway account.
 */
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { createHash } from 'node:crypto';
import assert from 'node:assert/strict';

const root = process.env.GENLAYER_NODE_ROOT;
if (!root) throw Error('Set GENLAYER_NODE_ROOT to the installed genlayer CLI package');
const load = relative => import(pathToFileURL(path.join(root, relative)).href);
const { createClient, createAccount } = await load('node_modules/genlayer-js/dist/index.js');
const { studionet } = await load('node_modules/genlayer-js/dist/chains/index.js');
const { CalldataAddress } = await load('node_modules/genlayer-js/dist/types/index.js');
const endpoint = 'https://studio.genlayer.com/api';
async function rpc(method, params = []) {
  const response = await fetch(endpoint, { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify({jsonrpc:'2.0',id:1,method,params}) });
  if (!response.ok) throw Error(`RPC HTTP ${response.status}`);
  const data = await response.json();
  if (data.error) throw Error(`${method}: ${JSON.stringify(data.error)}`);
  return data.result;
}
// This is always the first RPC, before SDK reads, signing, or submission.
assert.equal(Number(await rpc('eth_chainId')), 61999);
assert.equal(studionet.id, 61999);
let client = createClient({chain:studionet, endpoint});
const stringify = value => JSON.stringify(value, (_, v) => typeof v === 'bigint' ? Number(v) : v, 2) + '\n';
const save = (file, data) => fs.writeFileSync(file, stringify(data));
const canonical = text => text.replace(/\r\n?/g, '\n').replace(/\n*$/, '\n');
const sha = text => createHash('sha256').update(canonical(text), 'utf8').digest('hex');
const old = JSON.parse(fs.readFileSync('proof/verified-studionet.json','utf8'));
const journalFile = 'proof/closeout-journal.json';
const journal = fs.existsSync(journalFile) ? JSON.parse(fs.readFileSync(journalFile,'utf8')) : {chain_id:61999, transactions:{}, reads:{}, sources:{}};
const persist = () => save(journalFile, journal);
async function receipt(hash, expected = 'SUCCESS') {
  const start = Date.now();
  for (;;) {
    const tx = await rpc('eth_getTransactionByHash', [hash]);
    if (tx?.status === 'FINALIZED') {
      const executions = tx.consensus_data?.leader_receipt;
      assert.ok(Array.isArray(executions), 'missing execution receipt');
      const leaders = executions.filter(r => r.mode === 'leader');
      assert.ok(leaders.length, 'missing leader execution receipt');
      assert.equal(tx.result_name ?? tx.result, tx.result_name ? 'MAJORITY_AGREE' : 6);
      assert.ok(leaders.every(r => r.execution_result === expected), `${hash}: unexpected execution ${stringify(leaders.map(r=>({execution:r.execution_result, result:r.result, error:r.genvm_result})))}`);
      return {hash, status:tx.status, consensus:tx.result_name ?? 'MAJORITY_AGREE', execution:expected,
        to_address:tx.to_address, data:tx.type===1?{contract_address:tx.data.contract_address}:tx.data, leaders:leaders.map(r=>({mode:r.mode,execution_result:r.execution_result,result:r.result,genvm_result:r.genvm_result,vote:r.vote})), votes:tx.consensus_data.votes};
    }
    if (Date.now()-start > 20*60*1000) throw Error(`Receipt timeout ${hash}: ${tx?.status}`);
    await new Promise(resolve=>setTimeout(resolve, 5000));
  }
}
async function source(name, address) {
  const encoded = await rpc('gen_getContractCode',[address]);
  const deployed = Buffer.from(encoded,'base64').toString('utf8');
  const local = fs.readFileSync(`contracts/${name}.py`,'utf8');
  return {address,normalization:'UTF-8; CRLF/CR to LF; exactly one terminal LF; no other whitespace or code changes',local_sha256:sha(local),deployed_sha256:sha(deployed),matches:canonical(local)===canonical(deployed)};
}
async function read(label,address,functionName,args=[]) {
  const result = await client.readContract({address,functionName,args,jsonSafeReturn:true});
  journal.reads[label] = result; persist(); return result;
}

if (!process.argv.includes('--execute')) {
  const evidence = {verified_at_utc:new Date().toISOString(),chain_id:61999,sources:{},receipts:{}};
  for (const name of ['coverage_seal','coverage_gate']) evidence.sources[name] = await source(name,old[`${name}_address`]);
  const hashes = new Set();
  function collect(value) {
    if (typeof value==='string' && /^0x[0-9a-fA-F]{64}$/.test(value)) hashes.add(value);
    else if(value && typeof value==='object') Object.values(value).forEach(collect);
  }
  collect(old);
  const expectedErrors = new Set([old.gate_rejections.wrong_package_hash.transaction,old.gate_rejections.replay.transaction,old.negative_lifecycle.gate_rejection.transaction]);
  for(const hash of hashes) { evidence.receipts[hash] = await receipt(hash,expectedErrors.has(hash)?'ERROR':'SUCCESS'); save('proof/legacy-reverification.json',evidence); console.log('Verified',hash); }
  save('proof/legacy-reverification.json',evidence);
  console.log('Legacy receipt verification complete');
  process.exit(0);
}

const keytar = (await load('node_modules/keytar/lib/keytar.js')).default;
const key = await keytar.getPassword('genlayer-cli','account:coverageSealThrowaway');
if (!key) throw Error('CoverageSeal deployment account must be unlocked in the official CLI');
const account = createAccount(key);
assert.equal(account.address.toLowerCase(), '0xd6423ae82a975d55c6ceac222827a727325e0459');
client = createClient({chain:studionet,endpoint,account});
async function transaction(label, submit, expected='SUCCESS') {
  if (!journal.transactions[label]) {
    assert.equal(Number(await rpc('eth_chainId')),61999);
    const hash = await submit();
    journal.transactions[label] = {hash,expected}; persist();
    console.log('Submitted',label,hash);
  }
  const entry = journal.transactions[label];
  if (!entry.receipt) { entry.receipt = await receipt(entry.hash,expected); persist(); }
  console.log('Verified',label,entry.receipt.status,entry.receipt.execution);
  return entry.receipt;
}
const write = (label,address,functionName,args=[],expected='SUCCESS') => transaction(label,()=>client.writeContract({address,functionName,args,value:0n,leaderOnly:false}),expected);
async function deploy(name,args=[]) {
  const code=canonical(fs.readFileSync(`contracts/${name}.py`,'utf8'));
  const r=await transaction(`deploy_${name}`,()=>client.deployContract({code,args,leaderOnly:false}));
  const address=r.data?.contract_address ?? r.to_address;
  assert.match(address,/^0x[0-9a-fA-F]{40}$/);
  journal.sources[name]=await source(name,address); persist();
  assert.equal(journal.sources[name].matches,true);
  return address;
}
const seal=await deploy('coverage_seal');
const gate=await deploy('coverage_gate',[new CalldataAddress(seal)]);
journal.coverage_seal_address=seal; journal.coverage_gate_address=gate; persist();
const manifest=JSON.parse(fs.readFileSync('fixtures/demo_manifest.json','utf8'));
async function add(label,pid,name) { const a=manifest.artifacts[name]; await write(label,seal,'add_artifact',[pid,name,a.url,a.keccak256]); }
await write('create_schema',seal,'create_schema',['Atlas diligence closeout',manifest.source_prefix]);
await write('require_owners',seal,'add_requirement',[1,'OWNERS','Identify the company owners and ownership percentages',1,0]);
await write('require_finances',seal,'add_requirement',[1,'FINANCES','Describe the company revenue for 2024 and 2025',1,0]);
await write('seal_schema',seal,'seal_schema',[1]);
const schema=await read('schema',seal,'get_schema',[1]);
await write('create_complete',seal,'create_package',[1,schema.definition_hash]);
await add('complete_ownership',1,'ownership.txt'); await add('complete_finances',1,'finances.txt');
await write('seal_complete',seal,'seal_package',[1]);
for(const rid of [1,2]) for(const aid of [1,2]) {
  await write(`complete_edge_${rid}_${aid}`,seal,'assess_artifact',[1,rid,aid]);
  const edge=await read(`complete_edge_${rid}_${aid}`,seal,'get_assessment',[1,rid,aid]); assert.equal(edge.code,3);
}
for(const rid of [1,2]) { await write(`complete_pair_${rid}`,seal,'assess_pair',[1,rid,1,2]); assert.equal((await read(`complete_pair_${rid}`,seal,'get_pair',[1,rid,1,2])).code,1); }
await write('finalize_complete',seal,'finalize_package',[1]);
const complete=await read('complete',seal,'get_package',[1]); assert.equal(complete.status,2);
const pins=p=>[p.schema_hash,p.package_hash,p.snapshot_hash];
assert.equal(await read('complete_exact',seal,'is_complete',[1,...pins(complete)]),true);
assert.equal(await read('complete_wrong',seal,'is_complete',[1,complete.schema_hash,'0'.repeat(64),complete.snapshot_hash]),false);
assert.equal(await read('unknown_package',seal,'is_complete',[99,...pins(complete)]),false);
const action='a'.repeat(64), payload='b'.repeat(64);
await write('consumer_execute',gate,'execute',[1,...pins(complete),action,payload]);
assert.equal(await read('consumer_executed',gate,'was_executed',[action]),true);
const execution=await read('consumer_execution',gate,'get_execution',[action]);
assert.equal(execution.package_id,1); assert.equal(execution.payload_hash,payload);
assert.equal(execution.schema_hash,complete.schema_hash); assert.equal(execution.package_hash,complete.package_hash); assert.equal(execution.snapshot_hash,complete.snapshot_hash);
await write('consumer_replay',gate,'execute',[1,...pins(complete),action,payload],'ERROR');
await write('consumer_wrong',gate,'execute',[1,complete.schema_hash,'0'.repeat(64),complete.snapshot_hash,'c'.repeat(64),payload],'ERROR');
await write('create_missing',seal,'create_package',[1,schema.definition_hash]);
await add('missing_ownership',2,'ownership_only.txt'); await write('seal_missing',seal,'seal_package',[2]);
for(const rid of [1,2]) { await write(`missing_edge_${rid}`,seal,'assess_artifact',[2,rid,3]); const edge=await read(`missing_edge_${rid}`,seal,'get_assessment',[2,rid,3]); assert.equal(edge.code,rid===1?3:1); }
await write('finalize_missing',seal,'finalize_package',[2]);
const missing=await read('missing',seal,'get_package',[2]); assert.equal(missing.status,3);
assert.equal(await read('missing_exact',seal,'is_complete',[2,...pins(missing)]),false);
await write('consumer_incomplete',gate,'execute',[2,...pins(missing),'d'.repeat(64),payload],'ERROR');
await write('create_conflict_schema',seal,'create_schema',['Incident disclosures closeout',manifest.source_prefix]);
await write('require_incidents',seal,'add_requirement',[2,'INCIDENTS','Describe production incidents in 2025, including whether any occurred',1,0]);
await write('seal_conflict_schema',seal,'seal_schema',[2]);
const conflictSchema=await read('conflict_schema',seal,'get_schema',[2]);
await write('create_conflict',seal,'create_package',[2,conflictSchema.definition_hash]);
await add('conflict_clear',3,'incidents_clear.txt'); await add('conflict_incident',3,'incidents_conflicting.txt');
await write('seal_conflict',seal,'seal_package',[3]);
for(const aid of [4,5]) { await write(`conflict_edge_${aid}`,seal,'assess_artifact',[3,3,aid]); assert.equal((await read(`conflict_edge_${aid}`,seal,'get_assessment',[3,3,aid])).code,3); }
await write('conflict_pair',seal,'assess_pair',[3,3,4,5]); assert.equal((await read('conflict_pair',seal,'get_pair',[3,3,4,5])).code,2);
await write('finalize_conflict',seal,'finalize_package',[3]);
const conflict=await read('conflict',seal,'get_package',[3]); assert.equal(conflict.status,3);
assert.equal(await read('conflict_exact',seal,'is_complete',[3,...pins(conflict)]),false);
for(const [label,pid,rid] of [['owners',1,1],['finances',1,2],['missing_owners',2,1],['missing_finances',2,2],['conflicted',3,3]]) {
  const summary=await read(label,seal,'get_requirement_status',[pid,rid]); assert.equal(summary.unresolved,false);
}
journal.completed_at_utc=new Date().toISOString(); persist();
console.log('SUCCESS: source-matched StudioNet deployments, complete/missing/conflict lifecycles and consumer checks');
