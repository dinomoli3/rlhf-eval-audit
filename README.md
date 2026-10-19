# RLHF Evaluation Audit

An operational audit for human-in-the-loop model evaluations. It checks subgroup coverage, outcome rates, and matched counterfactual differences in a CSV of **already scored** model outputs. It does not call a model, infer protected attributes, decide what is fair, or certify legal compliance.

The companion [case study](CASE_STUDY.md) explains how the audit fits in a preference-data pipeline. The [upstream proposal](CONTRIBUTION.md) describes a scoped contribution to [Inspect AI](https://inspect.aisi.org.uk/) and the maintainer steps required before a pull request.

## Quick start

Python 3.10+; no third-party dependencies.

```bash
python3 -m eval_audit examples/synthetic_counterfactuals.csv --group-a A --group-b B --min-pairs 20 --json report.json
python3 -m unittest discover -s tests -v
```

The included dataset is **synthetic**. Its letters are fictional test variants, not demographic groups or real model responses. It deliberately contains a detectable directional difference for demonstration. The command prints a report and writes machine-readable JSON. Exit code 2 means invalid data or arguments; an observed disparity never changes the exit code.

## Input contract

| Column | Meaning |
| --- | --- |
| `pair_id` | Stable ID of the same underlying scenario for the two counterfactual variants. |
| `group` | Variant label, such as a controlled name or dialect substitution. |
| `outcome` | Human-approved binary rubric score: `1` for satisfactory, `0` for unsatisfactory. |

Exactly one row per `(pair_id, group)` is allowed. The two requested groups must occur in every pair. Rows for other groups are rejected to avoid silent denominator changes. Empty values, other scores, and repeated IDs fail validation. Only pair IDs, group labels, and aggregate counts appear in output; do not put personal information in identifiers. Keep the raw prompts, outputs, annotator data, and any sensitive attributes in an appropriately governed evaluation store.

**Scoring policy is external:** define the rubric before analysis, use blinded reviewers where practical, preserve refusal and abstention as distinct raw labels, and map those to 0/1 only for a specific task with a documented rule. If an abstention has no defensible binary mapping, keep it out of this input and report its rate separately. The tool cannot reveal unequal refusal rates or rater disagreement from collapsed labels alone.

## Measures and interpretation

- Each group's success rate and Wilson 95% interval describe observed scores. They are not intervals for a causal effect.
- `paired_difference` is mean(outcome A − outcome B) across complete pairs. `flip_rate` is the fraction of pairs whose scores differ. A paired design controls the scenario text that is held fixed; it does not control for other changes in the model, prompt, scorer, or run conditions.
- `a_only` and `b_only` count discordant pairs. The exact two-sided binomial sign test conditions on discordant pairs and tests symmetry. A small p-value is a review trigger, not a fairness verdict. The bootstrap 95% interval resamples **pairs**, with a fixed seed for reproducibility.
- `min_pairs` sets a coverage gate (default 20). If it fails, the report says `INSUFFICIENT_COVERAGE`. Passing it does not guarantee statistical power or representativeness. Inspect pair construction, rubric consistency, multiple comparisons, and impact before a decision.

## Portfolio scope

This is an original, public demonstration using synthetic data. It draws on operational patterns in evaluation and compliance work but contains no employer datasets, rubrics, internal tooling, or unverified claims about those employers. Run it on a real model only after generating and scoring consented, appropriately handled counterfactual examples. The output is evidence for investigation, not a regulator-facing conformity assessment.
