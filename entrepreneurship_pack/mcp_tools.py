from domaintoolbelt_sdk.types import ToolResult


_CORPUS = [
    {"id": "Thiel - Zero to One", "text": "[Peter Thiel] True progress comes from creating new things (0 to 1) rather than copying (1 to n)."},
    {"id": "Thiel - Competition is for Losers", "text": "[Peter Thiel] In business, competition implies no profits. Monopolies capture value."},
    {"id": "Andreessen - Software Eating World", "text": "[Marc Andreessen] Software is eating the world; every company needs to become a software company."},
    {"id": "Andreessen - Techno-Optimism", "text": "[Marc Andreessen] Technology is the most powerful force for good in the world."},
    {"id": "Cowen - Average is Over", "text": "[Tyler Cowen] Technology is making high-skill workers more valuable and low-skill workers obsolete."},
    {"id": "Graham - Startup Ideas", "text": "[Paul Graham] The best startup ideas come from founders solving their own problems."},
    {"id": "Naval - Navalmanack", "text": "[Naval Ravikant] The wealth of the future is about leverage (code, media, capital)."},
    {"id": "Perez - Technological Revolutions", "text": "[Carlota Perez] Technological revolutions come in_INSTALL phases: irruption, frenzy, synergy, maturity."},
    {"id": "Thiel - Definite Optimism", "text": "[Peter Thiel] Definite optimism means having a concrete plan to make the future better."},
    {"id": "Andreessen - Future of AI", "text": "[Marc Andreessen] AI will create massive value by automating cognitive work."},
]

_CROSS_REFS = {
    "Thiel - Zero to One": ["Graham - Startup Ideas", "Naval - Navalmanack"],
    "Andreessen - Software Eating World": ["Cowen - Average is Over", "Perez - Technological Revolutions"],
    "Cowen - Average is Over": ["Andreessen - Future of AI", "Naval - Navalmanack"],
    "Thiel - Competition is for Losers": ["Andreessen - Techno-Optimism"],
    "Graham - Startup Ideas": ["Thiel - Zero to One", "Naval - Navalmanack"],
}


class KeywordRetriever:
    def __init__(self, records):
        self._records = records

    def search(self, query: str, top_k: int = 5):
        query_terms = set(query.lower().split())
        results = []
        for record in self._records:
            text = record["text"].lower()
            score = sum(1 for term in query_terms if term in text)
            if score > 0:
                results.append({"id": record["id"], "text": record["text"], "score": score})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]


def build_retriever():
    records = [{"id": r["id"], "text": r["text"]} for r in _CORPUS]
    return KeywordRetriever(records)


async def analyze_startup_case(company: str) -> dict:
    company_lower = company.lower()
    retriever = build_retriever()
    matches = retriever.search(company_lower, top_k=5)
    
    factors = []
    if any(word in company_lower for word in ["tech", "software", "ai", "data"]):
        factors.append("Software-driven business model *(inference)*")
    if any(word in company_lower for word in ["platform", "network", "marketplace"]):
        factors.append("Network effects potential *(inference)*")
    if any(word in company_lower for word in ["monopoly", "patent", "unique"]):
        factors.append("Defensible moat *(inference)*")
    else:
        factors.append("Consider building monopoly through vertical integration *(inference)*")
    
    return {
        "company": company,
        "success_factors": factors if factors else ["Analyze domain for specific success factors *(inference)*"],
        "citations": tuple(m["id"] for m in matches) if matches else ("Thiel - Zero to One",),
    }


async def forecast_tech_impact(technology: str) -> dict:
    tech_lower = technology.lower()
    retriever = build_retriever()
    matches = retriever.search(tech_lower, top_k=5)
    
    scenarios = []
    if "ai" in tech_lower or "artificial intelligence" in tech_lower:
        scenarios.append("AI will automate cognitive work, creating massive productivity gains *(inference)*")
        scenarios.append("High-skill workers will benefit most; low-skill workers face displacement *(inference)*")
    if "blockchain" in tech_lower or "crypto" in tech_lower:
        scenarios.append("Decentralized protocols may disrupt traditional financial systems *(inference)*")
    if "biotech" in tech_lower or "gene" in tech_lower:
        scenarios.append("Biotech breakthroughs could extend human lifespan and treat chronic diseases *(inference)*")
    if "space" in tech_lower:
        scenarios.append("Space economy could unlock vast resources and new markets *(inference)*")
    if not scenarios:
        scenarios.append("Technology adoption follows Perez irruption-synergy pattern *(inference)*")
    
    return {
        "technology": technology,
        "scenarios": scenarios,
        "citations": tuple(m["id"] for m in matches) if matches else ("Andreessen - Future of AI", "Perez - Technological Revolutions"),
    }


async def evaluate_innovation_pathway(strategy: str) -> dict:
    strategy_lower = strategy.lower()
    retriever = build_retriever()
    matches = retriever.search(strategy_lower, top_k=3)
    
    evaluation = []
    if "0 to 1" in strategy_lower or "create" in strategy_lower or "new" in strategy_lower:
        evaluation.append("Zero-to-one strategy aligns with Thiel's approach to true innovation")
    elif "1 to n" in strategy_lower or "copy" in strategy_lower or "scale" in strategy_lower:
        evaluation.append("Scaling existing models; verify market timing per Perez framework *(inference)*")
    
    if "platform" in strategy_lower:
        evaluation.append("Platform strategy can create network effects and defensibility")
    if "monopoly" in strategy_lower:
        evaluation.append("Monopoly positioning essential for long-term value capture (Thiel)")
    
    return {
        "strategy": strategy,
        "evaluation": evaluation if evaluation else ["Evaluate against specific market conditions *(inference)*"],
        "citations": tuple(m["id"] for m in matches) if matches else ("Thiel - Zero to One", "Perez - Technological Revolutions"),
    }