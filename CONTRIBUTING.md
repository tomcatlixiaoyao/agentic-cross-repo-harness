# Contributing

Contributions should preserve the project's provider-neutral and least-authority design.

Before opening a pull request:

1. use only synthetic repositories, contracts, and validation results;
2. avoid organisation-specific tools unless implemented as optional adapters;
3. keep the initializer confined to its target directory;
4. keep the checker read-only and do not execute manifest commands;
5. add or update tests for behavioural changes;
6. run the unit tests and public-content scan;
7. explain security-boundary changes explicitly in the pull request.

Use the repository's issue forms for reproducible bugs and provider-neutral feature requests. Security
vulnerabilities must be reported privately through the process in [SECURITY.md](SECURITY.md), not in a
public issue.
