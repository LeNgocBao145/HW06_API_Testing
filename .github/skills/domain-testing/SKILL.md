---
name: domain-testing
description: Apply domain testing and boundary value analysis (BVA) to generate structured test cases for any software feature. Use this skill whenever the user provides a feature name or ID (e.g. "FR-01", "Checkout", "Login") and wants to run through the 4-step domain testing procedure. The skill walks step-by-step with a human review checkpoint after each step before proceeding.
---

# Domain Testing Skill

Executes the **4-step domain testing procedure** from CSC13003, one step at a time. After each step, pause and wait for the user to review and confirm before continuing.

Read `references/domain-testing-knowledge.md` for the full theory, guidelines, and reference example before starting.

---

## Workflow

### How to run

When the user provides a feature to test, execute the steps below **in order**. After completing each step, output the result and end with:

> **Step N complete.** Please review and type `continue` (or provide corrections) to proceed to Step N+1.

Do not proceed to the next step until the user explicitly confirms. Do not write a step's output into `Report.md` until the user confirms that step — keep it in the conversation only until then.
 
**On confirmation, "write to Report.md" and "git commit" are a single atomic action — never do one without the other, in this order:**
1. Write the step's output into `Report.md` at the location specified for that step.
2. Immediately run the corresponding `git add` + `git commit` command for that step (commit message given per-step below).
3. Only after both 1 and 2 are done, output the "Step N complete... type `continue`" prompt for the *next* step.
If step 2 (the actual `git commit` shell command) is skipped, the step is **not** considered complete — do not present it to the user as done, and do not move on. Treat "user confirmed" as triggering a checklist of exactly these two file-system actions, not just a chat reply.

**Ask, don't assume.** If the feature spec is missing, ambiguous, or incomplete at any step — unclear input ranges, unspecified error messages, undefined data types, missing business rules, unknown tech stack, etc. — **stop and ask the user** for clarification before producing output for that step. Never invent constraints, ranges, error messages, or behavior that were not stated in the spec or confirmed by the user.

---

Correcting an already-confirmed step
If the user corrects an earlier, already-committed step M while reviewing a later step N:

Patch step M with the minimum edit (not a full rewrite); commit: test(FR-XX): Step M - fix/amend <desc>.
Walk forward M+1..N in order. For each: if unaffected, say "unchanged" and skip it; if affected, append/edit only the new delta (e.g. +1 EC, +1 TC) instead of regenerating the table. Full regeneration of a step only if the fix is foundational — ask first.
Re-present step N (with delta noted) and stop at the normal confirm prompt — never auto-advance to N+1.
Report.md: only steps already confirmed get overwritten; anything still pending stays out of Report.md.

---

### Step 1 — Identify Input & Output Variables

**Spec source priority:**
1. **Markdown specs in the project** — `README.md` (System Requirements Specification) and `api_specification.md` (or similarly named API spec file) are the primary source of truth. Read these first and use them as-is; this is black-box testing, so the spec — not the implementation — defines expected behavior.
2. Other API docs if present (Swagger/OpenAPI, Postman collection) — same tier as #1, use to fill in any detail the markdown specs don't cover.
3. **Only if the above sources are missing or genuinely incomplete** for the feature being tested (e.g. a constraint or error case isn't documented anywhere) — fall back to reading **backend source code only** (route/controller/handler) to fill that specific gap. Don't read backend code if the docs already cover the feature; note any gap to the user rather than silently switching to code-reading by default.
4. **Never read frontend code** to infer input/output behavior, under any circumstance — frontend validation/regex can be buggy or out of sync with the backend (e.g. a flawed regex that rejects valid input), so it is not a reliable source of truth for the spec. If the docs are incomplete and there's no backend access either, stop and ask the user for the spec instead of inferring from frontend code.

**What to do:**
- Read the feature spec (from the SUT repo, docs, or user description)
- List all **input variables**: name, type, constraints, and whether optional
- List all **output variables**: success cases and all error/failure cases

**Where it goes in Report.md:** Directly under the feature heading (e.g. `**FR-08: Checkout**`)

**Git commit after user accepts:**
```
test(FR-XX): Step 1 - identify input & output variables
```

---

### Step 2 — Identify Equivalence Classes

**What to do:**
- For each input and output variable, identify all equivalence classes
- Apply the guidelines from `references/domain-testing-knowledge.md` §3:
  - Range → 1 valid EC + 2 invalid ECs
  - Set of distinct values → 1 valid EC per value + 1 invalid EC
  - "Must be" condition → 1 valid EC + 1 invalid EC
- Apply the split rule when elements in an EC may behave differently
- Label each EC (EC1, EC2, ...) and mark Valid / Invalid

**Output format:** Table with columns `EC | Variable | Class | Valid/Invalid`

**Where it goes in Report.md:** Under `**Domain Testing**`

**Git commit after user accepts:**
```
test(FR-XX): Step 2 - identify equivalence classes
```

---

### Step 3 — Select Test Cases (Best Representatives)

**What to do:**
- Apply the selection rules from `references/domain-testing-knowledge.md` §4:
  - Valid ECs: combine as many valid ECs as possible into one TC
  - Invalid ECs: each TC covers **exactly one** invalid EC
- Assign concrete, executable representative values
- Produce the **minimum set of test cases** that covers all ECs

**Output format:** Table with columns `#TC | Partitions Covered | [Input cols...] | Expected Output`

**Where it goes in Report.md:** Under `**Domain Testing**` (continuation of Step 2)

**Git commit after user accepts:**
```
test(FR-XX): Step 3 - select representative test cases
```

---

### Step 4 — Boundary Value Analysis

**What to do:**
- Identify all **ordered** input variables (numeric ranges, string lengths, list sizes, dates)
- For each ordered variable, define LB and UB
- Select up to **9 BVA test points** per partition (see `references/domain-testing-knowledge.md` §5):
  LB−1, LB, LB+1, interior, UB−1, UB, UB+1, UI-min*, UI-max*
- Produce the BVA test case table

**Output format:** Table with columns `#TC | Partition | [Input cols...] | Expected Output | BVA Point`

**Where it goes in Report.md:** Under `**Boundary Value Analysis**`

**Git commit after user accepts:**
```
test(FR-XX): Step 4 - boundary value analysis
```

---

### Step 5 — Generate Executable Test Cases

**This step is optional and is not run automatically.** After Step 4 is confirmed and committed, do **not** proceed into Step 5 on your own. Instead, ask the user explicitly, e.g.:
 
> Step 4 complete and committed. Step 5 (generating executable test code in the SUT repo) is optional — would you like me to proceed with it now, or stop here?
 
Only begin Step 5 once the user explicitly confirms (e.g. "yes", "continue to step 5", "generate the tests"). If the user declines or doesn't ask for it, stop after Step 4 — the domain testing procedure is considered complete with Steps 1-4.

**What to do:**
- Inspect the SUT repository to determine: language, test framework, existing test structure, and available fixtures/factories
- Combine all test cases from Step 3 (EC representatives) and Step 4 (BVA) into a single executable test file
- Use real data that matches the SUT's test environment (existing test accounts, product IDs, database seeds, etc.)
- Follow the project's existing test conventions (naming, folder structure, setup/teardown patterns)

**Tech stack detection — check in order:**
1. Look for `package.json` → Jest, Mocha, Vitest, Playwright, Cypress
2. Look for `requirements.txt` / `pyproject.toml` → pytest, unittest
3. Look for `pom.xml` / `build.gradle` → JUnit
4. Look for `pubspec.yaml` → Flutter test
5. Look for existing test files to confirm framework and copy their structure

**Output:** A ready-to-run test file placed in the correct test directory of the SUT, covering:
- All EC test cases from Step 3 (labeled with EC ID in test name)
- All BVA test cases from Step 4 (labeled with BVA point in test name)

**Test naming convention:**
```
[FR-XX]_[TC-ID]_[EC or BVA point]_[brief description]
```
Example: `FR08_TC2_EC2_cart_empty`

**Note:** This step only produces test code in the SUT's test directory. Do not add a section to Report.md for this step.

**Git commit after user accepts:**
```
test(FR-XX): Step 5 - generate executable test cases ([framework])

- X EC test cases (Step 3 coverage)
- Y BVA test cases (Step 4 coverage)
- Total: Z test cases
```

---

## Report.md Placement Summary

```
### FR-XX: Feature Name

[Step 1 output — inputs & outputs]

### Domain Testing

[Step 2 output — equivalence classes]
[Step 3 output — representative test cases]

### Boundary Value Analysis

[Step 4 output — BVA test cases]
```

> Step 5 does not write to Report.md — it only produces the executable test file in the SUT's codebase.

---

## Notes

- Keep all test values **realistic and executable** against the actual SUT.
- If the feature spec is ambiguous or incomplete, **stop and ask the user** — do not assume or invent details (see "Ask, don't assume" above).
- Adapt input/output column names to match the actual feature under test — do not use generic placeholder names.
- The user may correct any step before proceeding; incorporate corrections before committing.
- For Step 5, the SUT project may live in a different directory than this skill. Ask the user for the project path if it is not already known, then work directly in that path — no need to copy the project elsewhere.