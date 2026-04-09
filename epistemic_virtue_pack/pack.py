from typing import Dict, List, Any
import re

class EpistemicVirtuePack:
    name = "epistemic_virtue_pack"
    version = "0.1.0"
    domain = "epistemology"
    description = "Fidelity-aware reasoning with intellectual humility"
    capabilities = ["claim_decomposition", "evidence_weighting", "bias_detection", "uncertainty_calibration", "source_triangulation", "alternative_generation"]
    
    def __init__(self):
        self.bias_patterns = {
            "motivated_reasoning": re.compile(r"\b(obviously|clearly|everyone knows)\b", re.I),
            "false_dichotomy": re.compile(r"\b(either.*or|only two options)\b", re.I),
        }
    
    def plan(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        claims = [c.strip() for c in query.split('.') if len(c.strip()) > 10][:5]
        return {
            "strategy": "fidelity_first",
            "steps": [{"type": "decompose", "claim": c} for c in claims],
            "guardrails": ["require_multiple_sources", "calibrate_confidence"]
        }
    
    def validate(self, trace: Dict[str, Any]) -> Dict[str, Any]:
        text = str(trace.get("synthesis", ""))
        issues = []
        for name, pattern in self.bias_patterns.items():
            if pattern.search(text):
                issues.append({"type": "bias_flag", "bias": name, "severity": "medium"})
        if "certainly" in text.lower() and trace.get("evidence_count", 0) < 3:
            issues.append({"type": "overconfidence", "severity": "high"})
        return {"valid": len([i for i in issues if i["severity"]=="high"])==0, "issues": issues, "virtue_score": max(0.0, 1.0-len(issues)*0.15)}
    
    def synthesize(self, findings: List[Dict], query: str) -> str:
        lines = []
        lines.append("## Assessment: " + query)
        lines.append("")
        lines.append("**Well-supported:**")
        for f in findings[:3]:
            lines.append("- " + f.get("claim", "No claim"))
        lines.append("")
        lines.append("**Uncertainty and limits:**")
        lines.append("- Source diversity: " + str(len(set(f.get("source","") for f in findings))))
        lines.append("")
        lines.append("**Alternative interpretations:**")
        lines.append("- Selection bias in sources")
        lines.append("- Confounding variables")
        return "\n".join(lines)
    
    def ground(self, claim: str) -> Dict[str, Any]:
        return {"search_queries": [claim + " evidence", claim + " criticism"], "source_types": ["primary"], "temporal_check": True}
    
    def memory_key(self, query: str) -> str:
        return "epistemic:" + str(hash(query) % 10000)
