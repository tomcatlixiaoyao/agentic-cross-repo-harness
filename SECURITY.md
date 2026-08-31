# Security Policy

Please report suspected vulnerabilities through GitHub private vulnerability reporting when it is enabled. Do not open a public issue containing credentials, private repository names, internal endpoints, customer data, or exploit details that would increase risk.

## Public-content policy

Contributions must use synthetic examples and generic repository names. Do not contribute:

- company source code or proprietary procedures;
- internal domains, registries, service names, or issue identifiers;
- credentials, tokens, cookies, app secrets, private keys, or connection strings;
- private metrics, logs, user data, customer data, or production identifiers;
- machine-specific absolute paths or personal directory names.

Run `python scripts/scan_public.py --root .` before proposing public changes, then perform a human review. The scanner is not a guarantee that content is safe to publish.
