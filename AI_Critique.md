<center>

# Faculty of Information Technology – Ho Chi Minh City University of Science

# CS423 / CSC15003 – Software Testing (AI-augmented · 2026)

</center>

# AI Critique

During this assignment, the AI demonstrated several critical flaws, biases, and incompleteness in both test design and implementation. It frequently misclassified test types, arbitrarily grouping Security, Schema, and Domain Partition tests under "State Transitions" to falsely inflate coverage. Furthermore, it hallucinated test implementations, generating Postman data that did not match the test designs in the report, and entirely missed the `PUT /api/categories/:id` endpoint because it relied on assumptions about standard CRUD operations instead of strictly reading the provided API specification. The AI also violated core QA principles by modifying the System Under Test (SUT) source code to force failing tests to pass and fabricating test execution reports without running the actual runner scripts.

The AI failed to catch these issues because it prioritized surface-level objectives—such as hitting artificial test quotas and achieving "Passed" statuses—over the integrity of the testing process. It lacked the contextual awareness to maintain a strict 1-1 mapping between test design and implementation, acting on generalized "catch-all" definitions rather than precise requirements. Additionally, its inherent tendency to auto-complete or interpolate data led to malformed JSON injections and false positives.

Collaborating with AI taught me a crucial principle: AI must be treated as a powerful but unreliable assistant that requires rigid guardrails and constant human verification. Test implementation must be explicitly prompted as a strict 1-1 translation of the design phase, not a creative exercise. Most importantly, humans must enforce the principle of testing independence—never allowing the AI to alter the SUT or generate execution metrics without tangible, evidence-based logs. Relying on AI without cross-referencing its output against the source specifications guarantees incomplete coverage and compromised testing integrity.

## Signature

| Student name: | LÊ ĐỨC NGỌC BẢO |
| --- | --- |
| Student ID: | 23127155 |
| Class / Cohort: | Software Testing - 23KTPM1 |
| Course: | CS423 / CSC13003 – Software Testing |
| Instructor: | [Lâm Quang Vũ](https://courses.ctda.hcmus.edu.vn/user/view.php?id=586&course=1) |
| Date: | Wednesday, August 22th, 2026 |
| Signature: | ![Signature](signature.png) |