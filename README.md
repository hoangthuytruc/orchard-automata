# Orchard Automata

State-driven agent workflows for Apple development.

Orchard Automata describes how an agent moves a development task from request to verified result. Each workflow defines its inputs, states, transitions, evidence, and handoff points. The repo starts with a feature-development workflow; implementation tools can be added as the design matures.

## Start here

1. Read [workflow model](docs/workflow-model.md).
2. Follow the [feature-development workflow](workflows/feature-development.md) for a first task.
3. Copy the [workflow template](templates/workflow.md) when defining another workflow.

## Repository map

```text
docs/          Shared concepts and conventions
workflows/     Task-specific agent workflows
templates/     Reusable workflow definitions
```

## Design principles

- Define observable completion criteria for every state.
- Record evidence for build, test, and review claims.
- Make failure and retry paths explicit.
- Keep Apple-specific details, such as Xcode schemes and simulator destinations, in each workflow's inputs.
- Require a clear handoff before actions that publish or distribute software.

## Status

Initial design scaffold. No executable agent runtime or Apple developer tooling is included yet.
