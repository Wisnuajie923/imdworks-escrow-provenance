# Sign-off

- `python3 run_tests.py`: local solc rebuild and full runtime comparison PASS.
- `python3 -m unittest -v test_helpers.py`: 3/3 PASS.
- Compiler binary integrity is recorded in `tools/download-integrity.json`.
- Runtime length is 6,258 bytes; patched hash equals the pinned onchain bytecode hash with zero mismatches.
- Nine immutable references are substituted only after bounds, AST id, zero-placeholder, overlap, and address validation.
- Wrong-token and source-byte negative controls fail.

## Explicit boundary

The observed runtime is the pinned Sourcify artifact, not a fresh RPC fetch. This does not claim live-chain freshness or formal contract correctness. No wallet, secret, signing, or production write was used.

Sign-off: enueex — https://x.com/AjaPawang
