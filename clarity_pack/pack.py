from typing import Dict, List, Any
import re

class ClarityPack:
    name = "clarity_pack"
    version = "0.1.0"
    domain = "communication"
    description = "Accessible depth without condescension"
    capabilities = ["jargon_audit", "structure_optimization", "mechanism_extraction"]
    
    def __init__(self):
        self.patterns = [re.compile(r"\b(simply|just|obviously)\b", re.I)]
    
    def plan(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        return {"strategy": "respectful_accessibility", "steps": [{"type": "analyze"}], "guardrails": ["preserve_nuance"]}
    
    def validate(self, trace: Dict[str, Any]) -> Dict[str, Any]:
        text = str(trace.get("synthesis", ""))
        issues = []
        for p in self.patterns:
            if p.search(text):
                issues.append({"type": "condescension", "severity": "medium"})
        return {"valid": True, "issues": issues, "clarity_score": max(0.0, 1.0-len(issues)*0.2)}
    
    def synthesize(self, findings: List[Dict], query: str) -> str:
        lines = []
        lines.append("## " + query)
        lines.append("")
        lines.append("**How it works:**")
        for f in findings[:2]:
            lines.append("- " + f.get("claim", ""))
        lines.append("")
        lines.append("**Tradeoffs:**")
        lines.append("| Option | Gains | Costs |")
        lines.append("| --- | --- | --- |")
        lines.append("| A | Speed | Accuracy |")
        return "\n".join(lines)
    
    def ground(self, claim: str) -> Dict[str, Any]:
        return {"search_queries": [claim + " mechanism"], "source_types": ["primary"], "temporal_check": False}
    
    def memory_key(self, query: str) -> str:
        return "clarity:" + str(hash(query) % 10000)
    
    def audit_text(self, text: str) -> Dict[str, Any]:
        return {"issues": [], "avg_sentence_length": 15}
