## Summary

- What problem does this change solve?
- What user-visible behavior changes?

## Safety boundary

- [ ] The change is provider-neutral and uses only synthetic or redacted examples.
- [ ] No credentials, private endpoints, personal data, raw logs, or internal repository content are included.
- [ ] The initializer still writes only below its explicit target.
- [ ] The checker remains read-only and does not execute participant verification commands.
- [ ] Publishing, deployment, permission changes, deletion, and other external effects still require separate confirmation.

## Validation

- [ ] `python -m unittest discover -s tests -p "test_*.py"`
- [ ] `python scripts/scan_public.py --root .`
- [ ] Documentation and generated-structure examples were updated when applicable.

## Rollback

Describe how to revert this change and whether it affects previously generated control repositories.
