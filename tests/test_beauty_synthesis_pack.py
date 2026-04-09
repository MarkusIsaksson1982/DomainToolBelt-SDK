import unittest, sys
sys.path.insert(0, '.')
from beauty_synthesis_pack.pack import BeautySynthesisPack

class TestBeauty(unittest.TestCase):
    def setUp(self): self.pack = BeautySynthesisPack()
    def test_interface(self): self.assertEqual(self.pack.name, "beauty_synthesis_pack")
    def test_synthesize(self): r = self.pack.synthesize([], "Q"); self.assertIn("Synthesis", r)
