import unittest, sys
sys.path.insert(0, '.')
from epistemic_virtue_pack.pack import EpistemicVirtuePack

class TestEpistemic(unittest.TestCase):
    def setUp(self): self.pack = EpistemicVirtuePack()
    def test_interface(self): self.assertEqual(self.pack.name, "epistemic_virtue_pack")
    def test_plan(self): self.assertEqual(self.pack.plan("test?", {})["strategy"], "fidelity_first")
    def test_validate(self): r = self.pack.validate({"synthesis": "certainly true", "evidence_count": 1}); self.assertFalse(r["valid"])
    def test_synthesize(self): r = self.pack.synthesize([{"claim": "X"}], "Q"); self.assertIn("Assessment", r)
