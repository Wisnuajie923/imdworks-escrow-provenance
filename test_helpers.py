import importlib
import unittest

class ComparisonTests(unittest.TestCase):
    def test_full_bytes_no_mask(self):
        try:
            helper = importlib.import_module('verifier')
        except ModuleNotFoundError:
            self.fail('comparison helper not implemented')
        result = helper.compare(b'\x01\x02\x03', b'\x01\x04\x03\x00')
        self.assertFalse(result['equal'])
        self.assertEqual(result['mismatch_offsets'], [1, 3])
        self.assertTrue(helper.compare(b'\x01\x02', b'\x01\x02')['equal'])
        self.assertFalse(helper.compare(b'\x01\x02', b'\x01\x03')['equal'])

    def test_patch_every_reference_and_reject_invalid(self):
        import verifier as h
        self.assertTrue(hasattr(h, 'patch_immutables'), 'immutable patch helper missing')
        runtime = b'\x60' + bytes(32) + b'\x61' + bytes(32) + b'\xa1'
        refs = {'7': [{'start': 1, 'length': 32}, {'start': 34, 'length': 32}]}
        token = '0x' + '12' * 20
        patched, substitutions = h.patch_immutables(runtime, refs, token, '7')
        word = bytes(12) + bytes.fromhex('12' * 20)
        self.assertEqual(patched, b'\x60' + word + b'\x61' + word + b'\xa1')
        self.assertEqual(len(substitutions), 2)
        for bad in ['0x12', '0x'+'zz'*20, '0x'+'00'*20, 7]:
            with self.assertRaises(ValueError):
                h.patch_immutables(runtime, refs, bad, '7')
        for badrefs in [{}, {'8': refs['7']}, {'7': [{'start': -1, 'length':32}]},
                        {'7':[{'start':60,'length':32}]}, {'7':[{'start':1,'length':20}]},
                        {'7':[{'start':True,'length':32}]},
                        {'7':[{'start':1,'length':32},{'start':2,'length':32}]}]:
            with self.assertRaises(ValueError):
                h.patch_immutables(runtime, badrefs, token, '7')
        with self.assertRaises(ValueError):
            h.patch_immutables(b'\xff' * len(runtime), refs, token, '7')
        corrupted = bytes([patched[0] ^ 1]) + patched[1:]
        self.assertEqual(h.compare(patched, corrupted)['mismatch_offsets'], [0])
        self.assertFalse(h.compare(patched, patched[:-1] + b'\xa2')['equal'])

    def test_cbor_exact_version_and_length(self):
        import verifier as h
        self.assertTrue(hasattr(h, 'metadata_tail'), 'metadata parser missing')
        tail = bytes.fromhex('a164736f6c634300081d000a')
        result = h.metadata_tail(b'\x60\x00' + tail)
        self.assertEqual(result['cbor_length'], 10)
        self.assertEqual(result['start'], 2)
        self.assertEqual(result['solc_version'], '0.8.29')
        for bad in [b'', tail[:-1], tail[:-2]+b'\x00\x0b',
                    bytes.fromhex('a164736f6c634300081c000a')]:
            with self.assertRaises(ValueError):
                h.metadata_tail(bad)

if __name__ == '__main__':
    unittest.main(verbosity=2)
