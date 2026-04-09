from domaintoolbelt_sdk.types import ToolResult


_CORPUS = [
    {"id": "Thiel - Definite Optimism", "text": "[Peter Thiel] Definite optimism means having a concrete plan to make the future better."},
    {"id": "Andreessen - Techno-Optimism", "text": "[Marc Andreessen] Technology is the most powerful force for good in the world."},
    {"id": "Cowen - Great Stagnation", "text": "[Tyler Cowen] Future prosperity depends on high-hanging fruit and continued innovation."},
    {"id": "Cowen - Average is Over", "text": "[Tyler Cowen] Technology is making high-skill workers more valuable and low-skill workers obsolete."},
    {"id": "Perez - Technological Revolutions", "text": "[Carlota Perez] Technological revolutions follow irruption → frenzy → synergy → maturity phases."},
    {"id": "Andreessen - Future of AI", "text": "[Marc Andreessen] AI will create massive value by automating cognitive work."},
    {"id": "Andreessen - Software Eating World", "text": "[Marc Andreessen] Software is eating the world; every company needs to become a software company."},
    {"id": "Doomer Caution", "text": "[Cautionary view] Rapid AI scaling carries existential risks that must be mitigated."},
    {"id": "EA Caution", "text": "[Effective Altruism] Focus on mitigating catastrophic risks from advanced AI systems."},
    {"id": "Thiel - Zero to One", "text": "[Peter Thiel] True progress comes from creating new things (0 to 1) rather than copying (1 to n)."},
    {"id": "Space Economy - Launch Costs", "text": "[Space economy] Falling launch costs enable trillion-dollar space economy by 2040s *(inference)*"},
    {"id": "Energy Abundance", "text": "[Energy] Fusion and advanced nuclear promise abundant clean energy *(inference)*"},
    {"id": "Biotech Longevity", "text": "[Biotech] Advances in biotechnology could extend healthy human lifespan significantly *(inference)*"},
]

_CROSS_REFS = {
    "Thiel - Definite Optimism": ["Andreessen - Techno-Optimism", "Doomer Caution", "EA Caution"],
    "Andreessen - Techno-Optimism": ["Thiel - Definite Optimism", "Perez - Technological Revolutions"],
    "Cowen - Great Stagnation": ["Thiel - Zero to One", "Andreessen - Future of AI"],
    "Andreessen - Future of AI": ["Doomer Caution", "EA Caution", "Cowen - Average is Over"],
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


async def forecast_scenario(trend: str) -> dict:
    trend_lower = trend.lower()
    retriever = build_retriever()
    matches = retriever.search(trend_lower, top_k=5)
    
    scenario = []
    if "ai" in trend_lower or "artificial intelligence" in trend_lower:
        scenario.append("AI will automate cognitive work, creating massive productivity gains *(inference)*")
        scenario.append("Per Perez framework, AI is likely in irruption-to-frenzy phase with rapid growth ahead *(inference)*")
        scenario.append("Counter-view: Doomer caution suggests existential risks require governance *(inference)*")
    elif "energy" in trend_lower or "fusion" in trend_lower or "nuclear" in trend_lower:
        scenario.append("Abundant clean energy could enable economic growth acceleration *(inference)*")
        scenario.append("Energy abundance aligns with techno-optimist prosperity scenarios *(inference)*")
    elif "biotech" in trend_lower or "longevity" in trend_lower or "health" in trend_lower:
        scenario.append("Biotech advances could significantly extend healthy human lifespan *(inference)*")
    elif "space" in trend_lower:
        scenario.append("Falling launch costs enable trillion-dollar space economy by 2040s *(inference)*")
    else:
        scenario.append(f"Apply Perez technological revolution framework to assess {trend} trajectory *(inference)*")
    
    return {
        "trend": trend,
        "scenario": scenario,
        "citations": tuple(m["id"] for m in matches) if matches else ("Perez - Technological Revolutions",),
    }


async def map_risk_opportunity(scenario: str) -> dict:
    scenario_lower = scenario.lower()
    retriever = build_retriever()
    matches = retriever.search(scenario_lower, top_k=3)
    
    risks = []
    opportunities = []
    
    if "ai" in scenario_lower or "artificial intelligence" in scenario_lower:
        risks.append("Existential risk from misaligned AI *(inference)*")
        risks.append("Economic disruption from automation displacement *(inference)*")
        opportunities.append("Massive productivity gains from cognitive automation *(inference)*")
        opportunities.append("New industries and job categories will emerge *(inference)*")
    elif "energy" in scenario_lower or "fusion" in scenario_lower:
        risks.append("Technology scaling challenges and timeline uncertainty *(inference)*")
        opportunities.append("Abundant clean energy enables economic growth *(inference)*")
    elif "biotech" in scenario_lower:
        risks.append("Regulatory hurdles and ethical concerns *(inference)*")
        opportunities.append("Extended healthy lifespan transforms society *(inference)*")
    else:
        risks.append("Assess specific risks for this scenario *(inference)*")
        opportunities.append("Identify sector-specific opportunities *(inference)*")
    
    return {
        "scenario": scenario,
        "risks": risks,
        "opportunities": opportunities,
        "citations": tuple(m["id"] for m in matches) if matches else ("Doomer Caution", "EA Caution", "Andreessen - Techno-Optimism"),
    }


async def evaluate_optimism_pathway(pathway: str) -> dict:
    pathway_lower = pathway.lower()
    retriever = build_retriever()
    matches = retriever.search(pathway_lower, top_k=3)
    
    evaluation = []
    
    if "definite" in pathway_lower:
        evaluation.append("Definite optimism (Thiel) requires concrete plan and belief the future can be shaped *(inference)*")
        evaluation.append("This pathway aligns with zero-to-one innovation strategy")
        evaluation.append("Contrast: Doomer caution and EA caution warn of unchecked risks")
    elif "indefinite" in pathway_lower:
        evaluation.append("Indefinite optimism assumes future will be better but without specific plan *(inference)*")
        evaluation.append("Per Thiel, indefinite optimism often leads to misplaced complacency")
    elif "techno" in pathway_lower or "optimist" in pathway_lower:
        evaluation.append("Techno-optimism (Andreessen) believes technology is force for good *(inference)*")
        evaluation.append("Requires acknowledging and mitigating risks while pursuing progress")
    else:
        evaluation.append("Evaluate against definite vs indefinite framework *(inference)*")
    
    return {
        "pathway": pathway,
        "evaluation": evaluation,
        "citations": tuple(m["id"] for m in matches) if matches else ("Thiel - Definite Optimism", "Andreessen - Techno-Optimism", "Doomer Caution"),
    }


TOOLS = {
    "forecast_scenario": forecast_scenario,
    "map_risk_opportunity": map_risk_opportunity,
    "evaluate_optimism_pathway": evaluate_optimism_pathway,
}