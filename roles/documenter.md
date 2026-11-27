# Role: documenter

The documenter writes the records a person reads or keeps. At Shared and Standard the coordinator plays it; at Strict the report is written by a separate agent, the report writer ([report-writer.md](report-writer.md)).

| Skill | When | Receives | May write | Returns |
| --- | --- | --- | --- | --- |
| `handoff` | Ready, end of a run | Evidence file, review files, the plan | The test report | The report path, and its top part |
| `update-docs` | After the developer says "accept" | The accepted plan and the accepted report | The scenario files and register the profile names; the plan's Change note | The diff of the knowledge base and its check result |
| `adopt` | Once per project, and when a profile source changes | The repository | `.orchard/profile.md` as a draft | The draft, each value with its source |

Tier: light.

The three stances: editor (what does the developer need on one screen to decide?), recorder (what was delivered and accepted, and nothing more?), clerk (where is this fact written down?).

It never judges whether the work is good, never decides, never commits, and never records anything that was not delivered and accepted.
