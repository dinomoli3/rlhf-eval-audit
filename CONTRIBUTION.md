# Open-source contribution plan: Inspect AI

**Target:** [UK AI Security Institute's Inspect AI](https://github.com/UKGovernmentBEIS/inspect_ai), an open-source framework for language-model evaluations. Its scorer API and grouped metrics offer a natural place to connect an operational counterfactual audit to a reproducible evaluation run. The current docs already support `grouped` metrics, so the proposal should focus on **paired** comparison, coverage validation, and documentation rather than duplicate an existing subgroup average feature.

**Contribution state:** an issue proposal and a working standalone implementation are prepared here. No upstream issue, branch, PR, or accepted contribution has been created. The repository asks contributors to raise an issue for new features and wait for maintainer feedback before claiming the work. It also asks for `make check` and `make test`, and disclosure of agent involvement in a PR. See [CONTRIBUTING.md](https://github.com/UKGovernmentBEIS/inspect_ai/blob/main/CONTRIBUTING.md) and [AGENTS.md](https://github.com/UKGovernmentBEIS/inspect_ai/blob/main/AGENTS.md). A real submission requires Diane's GitHub access and her review of the code and public wording.

## Ready-to-post issue draft

**Title:** Proposal: paired counterfactual outcome audit recipe with coverage checks

**Problem:** `grouped()` can summarize per-group scores, but a controlled two-variant evaluation also needs to verify complete matched pairs and show the direction and frequency of within-pair outcome changes. An unpaired aggregate can hide which exact scenarios flip.

**Proposed scope:** Add a documented recipe or example task that uses the existing custom scorer and sample metadata API, exports pair IDs and binary rubric outcomes, validates pair completeness, and computes matched success-rate difference, flip rate, discordant counts, and an exact sign-test diagnostic. Explain that the metrics do not establish fairness or legal compliance. Include a small synthetic dataset and tests for duplicate/missing pairs and zero discordances. Reuse existing grouped metrics for descriptive per-group summaries. Do not add a core metric until maintainers confirm that the need is general enough.

**Why useful:** It connects a common alignment evaluation design (counterfactual variants of the same scenario) to reviewable evidence and prevents silent denominator changes in a release report.

**Prior art / implementation sketch:** This repository's `eval_audit/core.py` implements pair validation and the statistical summary without dependencies. I can adapt it into an Inspect example after receiving feedback on location and format.

**Questions for maintainers:** Would you prefer a docs recipe, a standalone example, or an extension metric? Is there an established metadata convention for matched counterfactual examples?

## Submission path

1. Search current issues and PRs for a duplicate proposal, then post the issue above from Diane's account. Ask to claim it once accepted.
2. Adapt only the scope maintainers accept. Add integration tests against the pinned Inspect version and example output from a small synthetic run.
3. Run the repository's checks and tests; review the generated code and text personally. Disclose coding-assistant involvement and test results in the PR description. Keep the PR to one accepted issue.

This path matters: a standalone repository on Diane's profile can be published now, but it is **not** an upstream Inspect contribution until the maintainers accept and merge a PR.
