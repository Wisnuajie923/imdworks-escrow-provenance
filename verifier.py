"""Strict full-runtime comparison; no masks or metadata stripping."""
import re


def patch_immutables(runtime, refs, token, ast_id):
    if not isinstance(token, str) or not re.fullmatch(r'0x[0-9a-fA-F]{40}', token) or int(token[2:], 16) == 0:
        raise ValueError('token must be a nonzero 20-byte hexadecimal address')
    if set(refs) != {str(ast_id)} or not refs[str(ast_id)]:
        raise ValueError('expected exactly the validated paymentToken AST id')
    word = bytes(12) + bytes.fromhex(token[2:])
    out = bytearray(runtime)
    used = set()
    substitutions = []
    for ref in refs[str(ast_id)]:
        start, length = ref['start'], ref['length']
        if type(start) is not int or type(length) is not int or length != 32 or start < 0 or start + length > len(runtime):
            raise ValueError('immutable must be an in-bounds 32-byte address word')
        region = set(range(start, start + length))
        if used & region or runtime[start:start + length] != bytes(32):
            raise ValueError('overlap or nonzero immutable placeholder')
        used |= region
        out[start:start + length] = word
        substitutions.append({'ast_id': str(ast_id), 'start': start, 'length': length,
                              'before': bytes(32).hex(), 'after': word.hex()})
    return bytes(out), substitutions

def metadata_tail(runtime):
    if len(runtime) < 12:
        raise ValueError('missing CBOR trailer')
    length = int.from_bytes(runtime[-2:], 'big')
    start = len(runtime) - 2 - length
    # Under the pinned settings the entire CBOR is a one-entry map:
    # {text(4) "solc": bytes(3) [0,8,29]}. Not a heuristic trim.
    expected = bytes.fromhex('a164736f6c634300081d')
    if length != len(expected) or start < 0 or runtime[start:-2] != expected:
        raise ValueError('unexpected CBOR length/schema/version')
    return {'start': start, 'cbor_length': length, 'length_suffix': runtime[-2:].hex(),
            'cbor_hex': expected.hex(), 'solc_version': '0.8.29',
            'whole_trailer_length': length + 2}


def compare(expected, observed):
    offsets = [i for i in range(max(len(expected), len(observed)))
               if i >= len(expected) or i >= len(observed) or expected[i] != observed[i]]
    return {'equal': not offsets, 'expected_length': len(expected),
            'observed_length': len(observed), 'mismatch_count': len(offsets),
            'mismatch_offsets': offsets}
