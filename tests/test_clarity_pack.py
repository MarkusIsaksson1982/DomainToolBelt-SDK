import unittest, sys
sys.path.insert(0, '.')
from clarity_pack.pack import ClarityPack

class TestClarity(unittest.TestCase):
    def setUp(self): self.pack = ClarityPack()
    def test_interface(self): self.assertEqual(self.pack.name, "clarity_pack")
    def test_validate(self): r = self.pack.validate({"synthesis": "simply obvious"}); self.assertTrue(len(r["issues"])>0)
