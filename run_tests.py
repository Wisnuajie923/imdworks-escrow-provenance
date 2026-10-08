"""Rebuild and compare the published escrow runtime using only local pinned inputs."""
import hashlib, json, subprocess, sys
from pathlib import Path
from verifier import compare, patch_immutables, metadata_tail
ROOT=Path(__file__).parent

def main():
    p=json.loads((ROOT/'published-sourcify.json').read_text())
    inp=p['stdJsonInput']; inp['settings']['outputSelection']={'*':{'*':['evm.deployedBytecode']}}
    proc=subprocess.run([str(ROOT/'tools/solc-linux-amd64-v0.8.29+commit.ab55807c'),'--standard-json'],input=json.dumps(inp),text=True,capture_output=True,check=True)
    out=json.loads(proc.stdout)
    assert not [e for e in out.get('errors',[]) if e.get('severity')=='error']
    compiled=out['contracts']['src/IMDWorksEscrow.sol']['IMDWorksEscrow']['evm']['deployedBytecode']
    runtime=bytes.fromhex(compiled['object']); onchain=bytes.fromhex(p['runtimeBytecode']['onchainBytecode'][2:])
    token=p['deployment']['implementation']['address'] if isinstance(p.get('deployment',{}).get('implementation'),dict) else '0x5fc5360D0400a0Fd4f2af552ADD042D716F1d168'
    token='0x5fc5360D0400a0Fd4f2af552ADD042D716F1d168'
    patched, subs=patch_immutables(runtime, compiled['immutableReferences'], token, '757')
    comparison=compare(patched,onchain); assert comparison['equal']; trailer=metadata_tail(onchain)
    wrong, _=patch_immutables(runtime, compiled['immutableReferences'], '0x'+'11'*20, '757'); negative_token=compare(wrong,onchain); assert not negative_token['equal']
    changed=bytearray(patched); changed[0]^=1; negative_source=compare(bytes(changed),onchain); assert not negative_source['equal']
    report={'status':'PASS','compiler':'0.8.29+commit.ab55807c','optimizer_runs':200,'evm_version':'paris','viaIR':False,'runtime_bytes':len(onchain),'runtime_sha256':hashlib.sha256(onchain).hexdigest(),'compiled_unpatched_sha256':hashlib.sha256(runtime).hexdigest(),'patched_runtime_sha256':hashlib.sha256(patched).hexdigest(),'immutable_substitutions':subs,'comparison':comparison,'metadata':trailer,'negative_controls':{'wrong_token_fails':not negative_token['equal'],'source_byte_change_fails':not negative_source['equal']},'live_rpc_fetch':'not performed; runtime is the pinned public Sourcify onchainBytecode input','limitations':['Local rebuild uses pinned published Sourcify standard-json input and verified compiler binary; no claim of live RPC freshness.','This is bytecode provenance evidence, not a formal Solidity proof.']}
    (ROOT/'report.json').write_text(json.dumps(report,indent=2)+'\n'); print(json.dumps(report)); return 0
if __name__=='__main__': raise SystemExit(main())
