# Epistemic Virtue Pack

**Author:** Meta AI (Muse Spark)  
**Version:** 0.1.0  
**Domain:** Epistemology / Critical Reasoning

## Purpose

A DomainToolBelt pack that implements fidelity-aware interpretation centered on truth-seeking virtues:

- **Truth over narrative** – facts matter more than cultural norms
- **Intellectual humility** – calibrate confidence to evidence
- **Source triangulation** – require diverse, independent confirmation
- **Alternative generation** – always consider what else could explain the data
- **Incentive awareness** – question official reports with incentives not to seek truth

## What it adds

1. **Planning:** Decomposes queries into falsifiable claims, plans disconfirming searches first
2. **Guardrails:** Flags motivated reasoning, false dichotomies, tribal markers, moralizing language
3. **Validation:** Scores virtue (0-1), blocks high-severity overconfidence
4. **Synthesis:** Outputs calibrated assessments with alternatives and uncertainty

## Usage

```bash
python -m domaintoolbelt.cli --domain epistemic_virtue_pack --query "Do social media algorithms increase polarization?"
```

## Example Output

> **Well-supported:**
> - Multiple studies find correlation between usage and affective polarization (strength: 0.8)
>
> **Uncertainty:**
> - Causal direction unclear; source diversity: 4
> - Conflicting evidence present: True
>
> **Alternatives:**
> - Selection bias in available sources
> - Underlying confounder not measured

## Design Philosophy

Built on the principle that the deepest respect is treating every mind as one that came to genuinely understand. No condescension, no narrative enforcement, just mechanisms and nuance.
