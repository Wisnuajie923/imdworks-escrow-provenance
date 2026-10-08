# TDD record

The existing evidence records the helper-verifier implementation in red/green steps:

1. `evidence/tdd-01-red.log`: the comparison helper was absent (`ModuleNotFoundError`); 1 test failed.
2. `evidence/tdd-01-green.log`: the byte comparison helper was implemented; 1 test passed.
3. `evidence/tdd-02-red.log`: immutable patching was absent; 1 of 2 tests failed.
4. `evidence/tdd-02-green.log`: immutable patching and validation were implemented; 2 tests passed.
5. `evidence/tdd-03-red.log`: the metadata parser was absent; 1 of 3 tests failed.
6. The current `verifier.py` includes `compare`, `patch_immutables`, and `metadata_tail`; the current runner verifies all 3 tests pass.

The tests cover strict full-byte comparison, all immutable references plus invalid-input rejection, and exact Solidity 0.8.29 CBOR trailer validation. They are local unit tests; they do not prove a compiler rebuild or a deployed-runtime match.
