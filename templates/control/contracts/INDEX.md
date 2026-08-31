# Contract Index

This directory records contract ownership, locations, versions or hashes, and consumer snapshot status. It must not store a third authoritative copy of a provider contract.

| Contract | Provider repo | Truth path | Version/hash | Consumer repo | Snapshot path | Status |
| --- | --- | --- | --- | --- | --- | --- |
| `<contract-id>` | `<provider-id>` | `<provider-owned-path>` | `<version-or-hash>` | `<consumer-id>` | `<snapshot-path>` | planned |

When provider truth changes, regenerate or update affected consumer snapshots, verify compatibility, and update this index in the same cross-repository closeout.
