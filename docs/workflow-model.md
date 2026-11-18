# Workflow model

A workflow is a directed graph. Nodes are **states**; edges are **transitions** guarded by observable conditions.

## Required fields

| Field | Meaning |
| --- | --- |
| Trigger | Event that starts the workflow |
| Inputs | Task context and required project details |
| States | Work stages with explicit exit criteria |
| Transitions | Conditions that move work between states |
| Evidence | Files, command results, or reviews supporting a transition |
| Handoffs | Decisions or actions assigned to a person |
| Recovery | Route after failure, missing input, or interruption |

## State contract

For each state, specify:

1. **Entry:** what must already be true.
2. **Action:** what the agent does.
3. **Exit:** what result must be observed.
4. **Evidence:** where that result is recorded.

A transition should never depend only on an agent's assertion. For example, `Verify → Ready` requires a passing build or test result for the selected Xcode scheme and destination, or an explicit record of what could not run.

## Common states

`Intake → Plan → Implement → Verify → Review → Ready`

Failure paths return to the state that can resolve the issue. Missing requirements return to `Intake`; failing tests return to `Implement`; a review finding returns to `Plan` or `Implement` depending on scope.

`Ready` means work is prepared for its next handoff. It does not itself publish an app, merge code, or submit a build.
