# Open-source contribution path

This repository is an MIT-licensed, standalone audit utility for scored human-in-the-loop evaluations. It supports CSV and an optional [Inspect AI](https://github.com/UKGovernmentBEIS/inspect_ai) log adapter. Issues and pull requests to improve it are welcome.

The original plan was to propose paired counterfactual metrics in Inspect core. Research into existing issues changed that plan: [Inspect issue #4206](https://github.com/UKGovernmentBEIS/inspect_ai/issues/4206) covers paired statistics and was closed as not planned for core. A maintainer recommended a standalone extension. [Inspect's contribution guide](https://github.com/UKGovernmentBEIS/inspect_ai/blob/main/CONTRIBUTING.md) likewise recommends extension packages for specialized scorers and metrics. Posting the earlier issue draft would duplicate that discussion.

## Next upstream contribution

1. The adapter has been smoke-tested against a synthetic Inspect `.eval` log with the mock model (Inspect 0.3.282). Validate a substantive use case using openly licensed or consented data; keep prompts and personal data out of this repository unless permission is explicit.
2. Decide whether an Inspect component or an analysis package is the right integration. The present adapter is a post-run log analyzer, not a registered Inspect scorer or a published PyPI extension.
3. Once the integration has a demonstrated use case, propose a short entry in Inspect's community extensions listing. Follow the repository's current contribution policy and disclose AI assistance in the PR.

**Status:** the standalone project is published; no issue or pull request has been submitted upstream and no upstream acceptance is implied.
