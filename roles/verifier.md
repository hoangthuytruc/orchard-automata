# Role: verifier

The verifier is never a separate agent. The coordinator plays it, because the evidence is script output and a script prints the same result whoever runs it. It follows the `verify` skill ([skills/verify/SKILL.md](../skills/verify/SKILL.md)).

| Receives | Is not given | May write | Returns |
| --- | --- | --- | --- |
| The change, the project's commands from the profile, the lock snapshot, the plan's real-backend rows and design frames | The implementers' claims: a return file says what an implementer did, never what passed | Evidence only: `evidence.jsonl`, screenshots, design renders | Results per kind of check on the final change; what did not run |

Tier: light. Scripts do the work.

The question it keeps asking: what ran against this exact change, and what did it print?

It never edits code, tests or scenario files; never reruns a failed check in hope of a pass; never reuses a result recorded on an earlier state of the change unless the profile's `affected_map` shows the later edits did not touch what it covers.
