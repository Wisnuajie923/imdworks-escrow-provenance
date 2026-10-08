# Escrow provenance verifier

This is a local, reproducible bytecode provenance check for the pinned Sourcify standard-json source bundle and verified Solidity 0.8.29 compiler binary.

## Run

```sh
python3 run_tests.py
python3 -m unittest -v test_helpers.py
```

The runner compiles the pinned sources with optimizer 200, Paris EVM, `viaIR=false`, and compares the complete 6,258-byte deployed runtime. It patches exactly nine validated 32-byte immutable references for AST id 757, validates the complete 0.8.29 CBOR trailer, and reports hashes in `report.json`.

Observed result: patched runtime equals the pinned public `onchainBytecode` with zero mismatch offsets. Wrong-token and source-byte negative controls fail as expected.

## Boundary

The compared runtime is the `onchainBytecode` field in the pinned `published-sourcify.json`; this run does not fetch a fresh RPC response. Therefore the result is reproducible provenance evidence for the pinned artifact, not proof of live-chain freshness or formal Solidity correctness. No wallet, credential, signing, or production write is used.

See `TDD.md`, `SIGNOFF.md`, and `report.json` for the exact evidence boundary.
