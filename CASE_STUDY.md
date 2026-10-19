# The evaluation bottleneck is an evidence bottleneck

*A practical case study of human-in-the-loop quality controls for preference data and model evaluation*  
*Iris Diane Molina | September 2026*

> This is a public design exercise grounded in published research and experience running complex data, evaluation, and compliance programs. The numerical example below is synthetic. It does not describe a particular employer's pipeline or claim results for a real model.

## The decision the pipeline must support

Imagine a team releasing an assistant for everyday administrative tasks. It collects prompts, generates candidate responses, asks reviewers which response is better, and sends accepted examples to post-training. A separate evaluation set measures whether the next candidate model improves. Leaders want a weekly answer: is the model getting better for the users and situations that matter, without introducing a worse failure elsewhere?

A single aggregate pass rate cannot answer that. It can rise when easy examples become more common, when reviewers silently reinterpret the rubric, or when a failure-prone slice vanishes from sampling. The core operational problem is producing evidence that can survive a change in reviewers, vendors, model versions, and policy definitions.

Preference collection and evaluation share infrastructure but serve different purposes. A pairwise preference label can help train a reward model or a direct preference optimization system; a held-out eval should test the resulting model against an independently specified rubric. If the same prompt templates, raters, or judgments leak between training and evaluation, the measured improvement becomes difficult to trust. RewardBench's construction of challenging prompt/chosen/rejected trios illustrates why reward model performance needs separate scrutiny [1].

## Five bottlenecks that compound

### 1. Intake volume outruns diagnostic coverage

Teams often forecast annotation throughput in examples per day. The useful unit is **reviewable evidence per slice**. Suppose a queue delivers 5,000 evaluations, but nearly all cover common English requests while only 18 cover a high-impact dialect variant. The headline metric has low diagnostic value for that variant. A fixed minimum per predeclared slice and a report of the actual denominator are necessary before an aggregate number reaches a launch review.

**Control:** version a sampling manifest with scenario family, risk category, language or locale, counterfactual variable, model snapshot, and rubric version. Reserve capacity for rare but consequential cases. Track submitted, scorable, adjudicated, excluded, and held-out counts separately. Escalate coverage gaps instead of reporting an apparently clean pass rate.

### 2. Rubric ambiguity turns variation into noise or policy drift

“Helpful” and “safe” are not self-executing instructions. One reviewer may prefer a direct answer; another may reward a clarification request. An adjudication queue can raise apparent agreement by forcing a single label without preserving why people disagreed. Research on divergent preferences finds that some annotation disagreements reflect genuine differences in preference, not merely careless work [2].

**Control:** provide anchored examples for each rubric dimension; train reviewers on boundary cases; record initial independent judgments before adjudication; tag disagreement causes (unclear policy, factual dispute, subjective preference, missing context, reviewer error). Report agreement and adjudication rates by slice and rubric version. Reopen the rubric when the same disagreement recurs; do not simply push harder for consensus.

### 3. Vendor and reviewer incentives distort the signal

Fast labeling can improve unit cost while lowering the quality of the feedback consumed by post-training. A reviewer may learn to favor length, confident tone, or refusal rather than factual correctness, especially when QA samples are predictable. A vendor's overall pass rate can improve while the hard cases are routed to a different queue.

**Control:** blind the model identity and, where practical, the counterfactual attribute. Mix prevalidated anchors with fresh cases; sample QA across reviewers and difficult slices; monitor overrides, answer-time distributions, repeat judgments, and appeals. Separate throughput and quality targets. Have a documented escalation owner for systematic ambiguity, not only individual label corrections. These are proposed operating controls, not measured outcomes of this case study.

### 4. Labels lose their provenance between tools

A preference row is useful only if its origin remains recoverable: prompt/template version, candidate response IDs, policy revision, reviewer pool, adjudication history, model checkpoint, and permission to use the data. A changed policy can invalidate an earlier answer without changing its stored `chosen`/`rejected` fields. Privacy constraints can require data minimization and access control even for a small evaluation set.

**Control:** use immutable IDs and a versioned event trail. Store sensitive raw material separately from the analysis table, with the minimum metadata necessary for reproducible aggregates. Require explicit owners for data retention, deletion, access, and downstream reuse. Add a preflight that rejects mixed rubric versions or incomplete pairs before computing metrics. Do not interpret an audit log as proof that a system meets a law.

### 5. The launch review collapses uncertainty into a green light

An aggregate increase can coexist with regressions for one slice. The correct release decision depends on the task's harm model, affected population, sample size, uncertainty, and available mitigations. The NIST AI RMF calls for documenting evaluation of fairness and bias, including feedback and measurement practices [3]. The EU AI Act imposes context-specific obligations for **high-risk** AI systems, including data governance and technical documentation; the applicability and schedule of those requirements must be assessed for the actual system [4]. Neither framework turns a difference in two sample rates into a legal finding.

**Control:** publish a decision record with the defined use case, slice list, rubric, exclusion counts, failure severity, evidence links, owner, disposition, and reevaluation date. Distinguish *coverage failed*, *difference observed*, *needs further human review*, and *release decision*. An owner should sign off on the tradeoff and a follow-up test, with independent legal review where warranted.

## A small audit that makes one bottleneck visible

The accompanying Python tool takes an already scored CSV. Each `pair_id` denotes one scenario with two controlled variants, A and B. For each pair, the task's approved human rubric assigns 1 for a satisfactory response or 0 for an unsatisfactory one. The sample file has 24 fictional pairs: 12 pass for both groups, four fail for both, and eight pass only for A. This is an intentionally conspicuous toy example, **not** a real model bias result.

The resulting success rates are 20/24 for A and 12/24 for B, but the more informative paired result is that 8/24 outcomes flip and every discordance favors A. The paired difference is 8/24, or 33.3 percentage points. An exact two-sided sign test on the eight discordant pairs gives p = 0.0078125 under its symmetry null. The tool reports Wilson intervals for each success rate and a seeded, pair-resampled bootstrap interval for the paired difference. These intervals answer different questions; an independent-groups interval would ignore the matched design.

That result warrants inspection of the eight changed responses and the construction of the variants. It does **not** prove the model discriminates against a protected group: the score can encode a flawed rubric, the counterfactual can alter meaning, and the examples may not represent production. If the 24 examples were selected after noticing a problem, the nominal p-value does not account for that selection. Trying many subgroup comparisons without a predeclared plan also raises false-discovery risk. The small sample and a fixed `min_pairs` gate are operational prompts for review, not guarantees of power.

The tool rejects incomplete or duplicate pairs, nonbinary labels, and unexpected groups; it cannot judge whether the underlying reviewer was right. To audit refusals, abstentions, or rater disagreements, preserve those categories upstream and add separate analyses. Binary collapse can hide exactly the behavior the team needs to see.

## The operating design I would implement

| Stage | Required artifact | Failure signal | Decision owner |
| --- | --- | --- | --- |
| Intake | Versioned slice and sampling manifest | Rare slices underfilled | Evaluation lead |
| Annotation | Anchored rubric; initial labels; adjudication trail | Repeated disagreement or abnormal overrides | Quality lead |
| Data QA | Provenance, consent and reuse fields, holdout split | Missing lineage or mixed versions | Data owner |
| Measurement | Aggregate and paired slice reports; exclusions | Outcome flips or unstable estimates | Model evaluation lead |
| Release | Decision record, mitigating action, retest date | Unresolved high-severity regression | Product and risk owners |

The first iteration should be modest: define one consequential behavior, two controlled variants, and a reviewer-approved rubric; run a small blinded pilot; inspect every discordant pair; revise the rubric; then expand the sample and preregister the slices. Tie the subsequent evaluation to a model version and a concrete release decision. This sequence makes the workflow auditable and gives the operations team a way to change it when evidence is weak.

## Why this matters for alignment work

RLHF and related post-training methods depend on the *meaning* and *distribution* of human judgments. Better dashboards cannot rescue inconsistent collection or an eval set that excludes affected users. Conversely, a reliable operational loop can find a subtle failure before it is turned into a training signal or hidden in a global average. The durable contribution is a pipeline that can explain **which humans judged which behavior under which rules**, where the evidence is thin, and what changed after a finding.

## References

1. Lambert et al., [RewardBench: Evaluating Reward Models for Language Modeling](https://arxiv.org/abs/2403.13787), 2024.
2. Zhang et al., [Diverging Preferences: When do Annotators Disagree and do Models Know?](https://arxiv.org/abs/2410.14632), 2024.
3. NIST, [AI Risk Management Framework, Measure](https://airc.nist.gov/airmf-resources/playbook/measure/) and [Generative AI Profile](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence), 2024.
4. European Union, [Regulation (EU) 2024/1689, consolidated text](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A02024R1689-20260727), especially Articles 6, 10, and 11. Check the latest consolidated version and application dates for a real use case.

*About the author: Diane has led AI data/evaluation operations and large-scale privacy and regulatory programs. This article describes a proposed public operating model, not unpublished results from those programs.*
