# Terms

The one home for the vocabulary of Orchard Automata. Every other file uses these words in these senses and links here rather than redefining them.

Every entity the skill set relies on is defined here once. Each row gives what the word means here, when an instance of it is well formed, and the official definition it rests on, paraphrased, with its source. Where no standard defines a word, the row says so and names the nearest defined term; the plan does not invent authority. A source marked "not checked" is cited from memory and was not read against the current text.

Sources used: ISO/IEC/IEEE 12207 and 15288 (life cycle processes), 15026-1 (assurance), 29148 (requirements), 24748-10 and 24765 (vocabulary), ISO/IEC 25010 and 25019 (quality), ISO/IEC 22989 (AI concepts), ISO/IEC 33001 and ISO 9000 (evidence), ISO/IEC 2382 and IEEE 7000 and IEEE 828, the ISTQB glossary, NIST SP 800-207 and SP 800-192, the PMBOK Guide, the Scrum Guide, and the Workflow Management Coalition glossary.

### Trust and evidence

| Term | Meaning here | Well formed when | Official definition, paraphrased | Source |
| --- | --- | --- | --- | --- |
| Claim | Any statement by an agent that something is so: "the tests pass", "the screen matches" | It can be true or false, names what it is about, and names the evidence that would settle it | A true-or-false statement about the limits on a property's values, under stated conditions | ISO/IEC/IEEE 15026-1 |
| Evidence | A test or command record, a network log, a screenshot or screen recording, a code reference or a file hash, produced in this run on the final change; every claim needs at least one (see principles, "What counts as evidence") | It records what ran, on which version, with what result, and anyone can produce it again | Objective evidence: data supporting the existence or truth of something, obtained by observation, measurement or test | ISO/IEC 33001; ISO 9000 |
| Fact | A statement about a project that can be checked against a named source: a command, a path, a rule | It has a value, the file it was read from, and that file's hash; or it is marked as stated by the developer | No standard defines "fact". Nearest: data, a representation of facts in a form suitable for processing; and objective evidence | ISO/IEC/IEEE 24765 for data |
| Zero trust | No claim from an agent is accepted without evidence. Used by analogy: the standard is about access to network resources | Every transition names the evidence it needs | No implicit trust is granted because of location or ownership; each request is authenticated and authorised | NIST SP 800-207 |
| Verification | Checking the result against the approved plan and its scenarios | Every scenario has a test and a result on the final change | Confirmation, through objective evidence, that specified requirements have been fulfilled | ISO/IEC/IEEE 12207 |
| Validation | Deciding that this is the right thing to build. It happens at plan approval and at acceptance, by a person | The developer decided it from one screen | Confirmation, through objective evidence, that the requirements for a specific intended use have been fulfilled | ISO/IEC/IEEE 12207 |
| Oracle | What decides that a test failed: an example, an approved snapshot, a property, a person | The plan names it for every test whose oracle is not a plain example | Test oracle: a source to determine an expected result | ISTQB |
| Change detector | A test whose expected value has the same standing as the code: a constant copied from it, the calculation repeated, output recorded and never reviewed, a tuned configuration value. It fails on any change and cannot say which side is wrong | Reported as a change detector, never counted as proof of a scenario | No standard defines it. The name is the industry's (Google Testing Blog, "Change-Detector Tests Considered Harmful", 2015) | Wording not checked |
| Undecided behaviour | Something the code does that a person can observe and no source asks for | Named for the owner to decide or remove; not tested until decided | No standard defines it | None |
| Traceability | The chain from scenario to work package to test to evidence to acceptance | Each link can be followed in both directions | The degree to which a relationship can be established among two or more logical entities | ISO/IEC/IEEE 12207 |

### Requirements and scope

| Term | Meaning here | Well formed when | Official definition, paraphrased | Source |
| --- | --- | --- | --- | --- |
| Requirement | One thing a source says the app must do | It is one statement, carries the quote it comes from, and can be observed | A statement that translates or expresses a need and its associated constraints and conditions | ISO/IEC/IEEE 29148 |
| Source | A spec, a design or a recorded decision that may state requirements. Code is never a source | It has a link, an id, and a version or a date | Part of the test basis | ISTQB |
| Basis | The source that justifies one scenario | It points to the clause, not only to the document | Test basis: the body of knowledge used as the basis for test analysis and design | ISTQB |
| Scenario | One acceptance criterion written as an example: given, when, then, in the words a person sees | It has an id, a basis, one behaviour, and a test bound to it | Industry practice, not a standard: a scenario in behaviour-driven development, or an example in specification by example | Not checked |
| Approved scenario | A scenario in the project's knowledge base (the files the profile's `knowledge_base` names). Only `update-docs` writes there, and only after the developer's acceptance, so being in the knowledge base is the approval. A scenario tagged blocked or pending is still approved, but not yet proved | Its id matches the profile's `scenario_id_pattern` and is in a file of the knowledge base; no separate approval mark is needed or read | No standard defines it. Nearest: requirements baseline, the set of requirements agreed and placed under change control; and test basis, the body of knowledge tests are designed from | ISO/IEC/IEEE 29148 for requirements baseline; ISTQB for test basis; wording not checked |
| Acceptance criteria | What the result must satisfy for the developer to accept it. Here: the scenarios | Each is covered by at least one scenario | Criteria a work product must satisfy to be accepted by the stakeholders | ISTQB |
| Scope of a change | What one plan will and will not change | It lists what is in, what is out, the files each package owns, and who may change it: the developer | Product scope: the features and functions of a product, service or result. Project scope: the work performed to deliver it | PMBOK Guide |
| Scope level | Where a rule, a fact or an output lives: Model, Core, Sample, Project, Task, Personal or External | Each level says what it holds, what it must not hold, and who writes it; every item has exactly one level | No standard defines this use. It is by analogy with the scope of a name in a programming language | None |
| Boundary | A line between two layers or two roles that a given writer may not cross: product and technical, code and test, author and reviewer | It names both sides, who may write on each, what may cross and in what form, and the script or rule that detects a crossing | Interface: a shared boundary between two functional units. System boundary: the conceptual interface between a system and its environment | ISO/IEC 2382; IEEE 7000 |
| Conflict | Two sources, or a source and the plan, that cannot both be followed | Both readings are written down with their sources, and the row says who settles it | No standard defines it as an entity. Requirements are required to be consistent with one another | ISO/IEC/IEEE 29148, not checked |

### Work and flow

| Term | Meaning here | Well formed when | Official definition, paraphrased | Source |
| --- | --- | --- | --- | --- |
| Workflow | A file that defines states, transitions, the evidence each transition needs, and recovery | Every state has an exit condition someone can observe | The automation of a process, in whole or part, in which documents, information or tasks pass between participants according to rules | Workflow Management Coalition |
| State, transition | A stage of the work, and a move between two stages | A transition is written as: from, to, when an observable condition holds | State machine: states, and transitions fired by events and guarded by conditions | UML, not checked |
| Gate | A check that must pass before the work moves to the next state | It is a script or a recorded decision, never an agent's statement | Quality gate: a milestone where the decision to proceed is taken against predefined quality criteria | ISTQB |
| Plan | The approved file that says what will be built, the scenarios, the split and the proof | Its top fits one screen; every decision is in it; it has a status | No single standard defines a plan of this kind. Nearest: a baseline of requirements and work breakdown | See Baseline |
| Baseline | The approved plan together with the lock snapshot | It is fixed at approval and changes only by the developer's decision | A formally approved version of a configuration item, fixed at a specific time in its life cycle | ISO/IEC/IEEE 12207 |
| Locked file | A file no agent may change during a run, verified by hash | It is matched by a pattern in the profile and its hash is in the snapshot | Configuration item: work products designated for configuration management and treated as a single entity | IEEE 828 |
| Held test | A test file whose content hash was recorded by the red run that saw it fail; it is not edited afterwards unless it is seen failing again | `evidence.py held` lists no change since the latest red run that named the file | No standard defines it. Related: red, green, refactor in test-driven development (Beck, "Test-Driven Development: By Example", 2002) | Wording not checked |
| Plan seal | The hash of the plan's approved text, recorded at approval. The status line, the Result and the Change note are outside it | `plan_seal.py check` says it holds before a run starts and before its report | No standard defines it. Related: configuration baseline, a formally reviewed and agreed version that changes only through change control (ISO/IEC/IEEE 24765) | Wording not checked |
| Failure cause | Why a loop or a required check ended failing: plan gap, executor, test defect, flaky, environment or blocked | Every `loop_failed` record in the run log carries exactly one | No standard defines these six. Related: root cause, the source of a defect (ISTQB) | Wording not checked |
| Caller | Code, a stored or wire format, a command or a person that uses what a change alters, and relies on its behaviour | The plan lists each with what it relies on and whether the change keeps it | No standard defines it here. Related: impact analysis, identifying what a change affects (ISO/IEC/IEEE 24765) | Wording not checked |
| Work package | A part of the plan with its own files and its own done criteria | It owns its files alone, names its scenarios and its tier, and can be finished on its own | The work defined at the lowest level of the work breakdown structure, for which effort and duration are estimated and managed | PMBOK Guide |
| Run | One execution of a workflow, from an approved plan to a test report | It has one plan, one final change and one report | No standard defines it | None |
| Round | One pass of implement, verify and review inside a run | It ends with recorded results | Iteration | Not checked |
| Ready | The state in which the result is prepared for the developer and nothing has been published | The report exists and every claim in it links to evidence | Definition of Done: a formal description of the state of the increment when it meets the required quality measures | Scrum Guide |
| Acceptance | The developer's decision that the result of a run is done | It is given in the developer's words, after the report | Acceptance against acceptance criteria | ISTQB |
| Handoff | Passing a result to the person who decides, with the evidence | The person can decide without asking what happened | No standard defines it | None |

### People, agents and roles

| Term | Meaning here | Well formed when | Official definition, paraphrased | Source |
| --- | --- | --- | --- | --- |
| Developer | The person who runs the workflow, approves the plan and accepts the result. Also called the owner of a task |  | No standard defines it for this use | None |
| Product owner | The person who decides what the app should do |  | The person accountable for the value of the product and for its backlog | Scrum Guide, not checked |
| Person | The developer or the product owner, as opposed to an agent |  |  |  |
| Agent | A model-driven program that is handed a brief, acts with tools and returns one result | Its brief is its whole world: it names what it may read, what it may write and what it returns | AI agent: an automated entity that senses and responds to its environment and takes actions to achieve its goals | ISO/IEC 22989 |
| Role | A function in a workflow: coordinator, planner, implementer, verifier, reviewer, documenter | It says what it receives, what it is not given, what it may write and what it returns | No standard checked | Not checked |
| Separation of duties | The author of a change never reviews it; the reviewer never edits | No role can both produce a result and approve it | No single user should hold enough privilege to misuse a system alone | NIST SP 800-192 |
| Isolation level | How many roles run as separate agents: Shared, Standard or Strict | The isolation table in [workflow model](workflow-model.md#isolation-levels) gives its agents; its cost is not measured | No standard defines it | None |
| Tier | The capability class of model a role or a package needs: strong or light | The plan gives it with a one-line reason | No standard defines it | None |
| Skill | A packaged procedure an agent follows for one kind of task | It states what it reads, writes, never does, stops for, and leaves as evidence | No standard defines it. It follows the agent-skill file format | None |

### Quality and defects

| Term | Meaning here | Well formed when | Official definition, paraphrased | Source |
| --- | --- | --- | --- | --- |
| Functional suitability | The app does what its scenarios say: its functions are complete, correct and appropriate. How a screen looks is checked on the same side, although the standard files appearance under interaction capability | Every scenario has a passing test or a stated reason | Functional suitability: the degree to which a product provides functions that meet stated and implied needs under specified conditions. One of the nine characteristics of product quality. Wording not checked against the 2023 text | ISO/IEC 25010:2023 |
| Structural quality | The code is sound, bounded and maintainable | Lint, boundary checks and review pass, and debt is measured | Structural quality: quality measured from the internal structure of the source code, as weaknesses in security, reliability, performance efficiency and maintainability. Those four are characteristics of product quality in ISO/IEC 25010 | ISO/IEC 5055:2021; ISO/IEC 25010:2023 |
| Error | A wrong step by the author of a change |  | A human action that results in a defect | ISTQB |
| Defect | Something wrong in the code, a test or a document | It has a place, and a case that shows it | An imperfection or deficiency in a work product where it does not meet its requirements or specifications, or impairs its intended use | ISTQB |
| Failure | The app behaving wrongly when it runs | It can be reproduced | An event in which a component or system does not meet its requirements within specified limits during execution | ISTQB |
| Finding | One result of a review, anchored to a line, with type, severity, evidence and fix | It names the input, state or ordering that breaks the code, or the evidence that is missing | A result of an evaluation that identifies an anomaly, a defect or an opportunity | ISTQB |
| Technical debt | Work on internal quality that was put off and now costs more | It has evidence, a score and a first step | The deferred cost of work not performed earlier in the product life cycle | ISO/IEC/IEEE 24748-10 |

### Tests and checks

| Term | Meaning here | Official definition, paraphrased | Source |
| --- | --- | --- | --- |
| Static analysis | Checks that read code without running it | The automated evaluation of a component or system without executing it | ISTQB |
| Unit tests | Tests of one unit alone, including data-layer tests on fixtures | Component testing: a test level that focuses on individual components | ISTQB |
| Visual tests | Tests of how a screen looks. Not Apple's "UI tests" (XCUITest): those drive the app through the UI and count here as behaviour tests | Industry practice: visual, snapshot, screenshot or visual regression testing | Not checked |
| Behaviour tests | Tests of how the app reacts to input | Functional testing; when run through the UI, end-to-end testing | ISTQB, not checked |
| Integration tests | Tests of the app's calls to the real backend | Integration testing: a test level that focuses on interactions between components or systems | ISTQB |
| Full regression run | A re-run of all existing automated tests | Regression testing: change-related testing to detect defects introduced or uncovered in unchanged areas | ISTQB |
| Manual checks | Checks a person does on a device | Manual and exploratory testing | ISTQB, not checked |
| Test double | A stand-in for a real dependency: a stub, a fake or a mock | A replacement component invoked by a test object to perform testing | ISTQB; Meszaros, xUnit Test Patterns |
| Fixture | Fixed test data, such as a recorded server reply | Test fixture | Not checked |
| In-process | A test that runs inside the test process, without launching the app's UI | No standard defines it | None |
| Affected tests | Tests selected because the change touches the code they cover | Test impact analysis; regression test selection | Not checked |
| Flaky test | A test that passes and fails on the same code | Industry term | Not checked |
| Coverage threshold | The minimum code coverage a check enforces | Coverage: the degree to which specified items have been exercised by a test suite | ISTQB, not checked |
| Property | A rule that must hold for every input, such as a round trip, idempotency or an invariant | Property-based testing | Not checked |
| Fault injection | Making a test double return an error, nothing, or a slow reply on purpose | Fault injection; at system scale, chaos testing | Not checked |

### This skill set's own terms

No standard defines these. They are this plan's names, and each is defined here and nowhere else.

| Term | Meaning here | Well formed when |
| --- | --- | --- |
| Core | The rules, skills, references, scripts, roles and evals that hold for every iOS project | The leak check finds nothing project-specific in it |
| Sample | The small generic project every skill and workflow is proved on | It has its own project folder and seeded defects |
| Project profile | The file of project facts: commands, paths, locked patterns, base branch, source ranking | Every required key has a value with a source, or is marked missing |
| Leak | A project fact found inside core | The leak check names the file and the line |
| Knowledge base | The project's Gherkin feature files (`*.feature`) and their register: the single source of truth shared by product and tech. Every project has one; at adoption it may be an empty folder, filled from the first plan's scenarios. No standard defines it; Gherkin is the Cucumber project's language, an industry practice, not a standard | Every scenario in it has an id, a passing test or a stated reason |
| Register | The table that links each scenario to its basis and its test. A requirements traceability matrix | No id is reused; every row has all three |
| Eval | A repeatable test of a skill on the sample, scored by graders | It fails without the skill's rule and passes with it |
| Run log | The record each run leaves, written by scripts | It has the fields listed in section 11 |
