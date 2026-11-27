# Workflow: <name>

<!-- Copy into .orchard/workflows/ of a project and edit. Fields follow docs/workflow-model.md. Never name a tool or a model: name a role and a tier. -->

## Trigger

<What starts this workflow?>

## Inputs

- <Required context, with the profile keys it reads, e.g. `test.unit`, `scheme`, `destination`>

## Roles and isolation

- Default isolation: <Shared | Standard | Strict>. A plan may raise it, or lower it to Shared for a change in one or two files, with a one-line reason; never below a separate reviewer.

| State | Role | Tier | Skill |
| --- | --- | --- | --- |
| <State> | <Coordinator / Planner / Plan verifier / Implementer / Verifier / Reviewer / Documenter> | <strong / light / set by plan> | <skill> |

- Plan verification: <on | off>. On, the default, starts a separate plan verifier before approval (one more agent per plan).

## States

| State | Entry | Action | Exit | Evidence |
| --- | --- | --- | --- | --- |
| <Name> | <What must be true?> | <What happens?> | <What must be observed?> | <Where it is recorded> |

## Transitions

- `<From> → <To>` when <observable condition>.

## Decision points

| When | Person decides | Shown |
| --- | --- | --- |
| <Before / after> | <Decision> | <Evidence> |

## Ends early when

- <Condition that would force a guess> → report both sides and end.

## Recovery

- <Failure or missing input> → <state and next action>.

## Handoffs

- <Action that belongs to a person after Ready, its owner, and the evidence supplied>.
