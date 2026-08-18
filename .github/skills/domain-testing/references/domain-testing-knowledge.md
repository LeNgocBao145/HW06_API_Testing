# Domain Testing Knowledge Base (Course: CSC13003 - FIT@HCMUS)

## 1. Core Concepts

Domain testing partitions a domain into sub-domains (equivalence classes) and tests using values from each sub-domain. It is a **stratified sampling strategy** to select a few high-value test cases from a massive population.

**Equivalence Class Rule**: Two tests belong to the same equivalence class if their expected results are identical. Executing multiple test cases from the same equivalence class is redundant.

---

## 2. The 4-Step General Approach

1. **Identify Input & Output variables** — based on the program specification
2. **Identify Equivalence Classes** for each Input & Output — divide the domain into Valid and Invalid subsets
3. **Find a "best representative"** for each subset — select test cases from ECs
4. **Select Boundary Values** for ordered fields — boundaries catch the highest concentration of errors

---

## 3. Step 2 Guidelines: Identifying Equivalence Classes

### Guideline 1 — Range of values
If an input condition specifies a **range of values**, identify **1 valid EC** and **2 invalid ECs**.

> **Example**: "the item count can be from 1 to 999"
> - Valid EC: `1 ≤ count ≤ 999`
> - Invalid EC: `count < 1`
> - Invalid EC: `count > 999`

### Guideline 2 — Set of values handled differently
If an input condition specifies a **set of discrete values** and there is reason to believe each is handled differently by the program, identify **1 valid EC per value** and **1 invalid EC**.

> **Example**: "type of vehicle must be BUS, TRUCK, TAXI-CAB, PASSENGER or MOTORCYCLE"
> - Valid EC: `BUS`
> - Valid EC: `TRUCK`
> - Valid EC: `TAXI-CAB`
> - Valid EC: `PASSENGER`
> - Valid EC: `MOTORCYCLE`
> - Invalid EC: any value outside the set (e.g. `TRAILER`)

### Guideline 3 — "Must be" condition
If an input condition specifies a **"must be" situation**, identify **1 valid EC** and **1 invalid EC**.

> **Example**: "first character of the identifier must be a letter"
> - Valid EC: first character is a letter
> - Invalid EC: first character is not a letter

### Split rule
If there is any reason to believe that elements within an equivalence class are **not handled identically** by the program, split it into two or more smaller equivalence classes.

---

## 4. Step 3 Guidelines: Selecting Test Cases

- For **valid classes**: choose test cases that cover **as many valid ECs as possible** in one TC, until all valid classes are covered.
- For **invalid classes**: each TC covers **one and only one invalid EC**, until all invalid classes are covered.

---

## 5. Step 4: Boundary Value Analysis (BVA)

Programs are more likely to fail at a boundary. Two common error types that BVA targets:
- **Mis-specified inequality** (e.g. `INPUT <= 25` instead of `INPUT < 25`) — detectable **only** at the boundary
- **Mistyped boundary value** (e.g. transposition error `INPUT < 52`) — detectable at the boundary

For each ordered equivalence class partition, select up to **9 test points**:

| Point | Description | Location |
| --- | --- | --- |
| **1** | Interior valid — well inside the partition | Middle of valid range |
| **2** | LB + 1 | Just inside LB |
| **3** | Lower Boundary itself | Exact boundary |
| **4** | LB − 1 | Just outside LB (invalid) |
| **5** | UB + 1 | Just outside UB (invalid) |
| **6** | Upper Boundary itself | Exact boundary |
| **7** | UB − 1 | Just inside UB |
| **8\*** | Smallest value allowed via UI | Absolute UI minimum |
| **9\*** | Largest value allowed via UI | Absolute UI maximum |

> `8*` and `9*` may differ from spec LB/UB — they represent what the UI physically allows.

---

## 6. Reference Example: 2-Input Addition Program

**Spec**: Add two integers A and B, each in [−99, 99]. Output: SUM or "Invalid Input".

### Step 2: Complete Set of Equivalence Classes

| EC | Variable | Class | Valid/Invalid |
| --- | --- | --- | --- |
| EC1 | A | −99 ≤ A ≤ 99 | Valid |
| EC2 | A | A < −99 | Invalid |
| EC3 | A | A > 99 | Invalid |
| EC4 | A | A is not an integer | Invalid |
| EC5 | B | −99 ≤ B ≤ 99 | Valid |
| EC6 | B | B < −99 | Invalid |
| EC7 | B | B > 99 | Invalid |
| EC8 | B | B is not an integer | Invalid |
| EC9 | SUM | = A + B | Valid output |
| EC10 | SUM | Error Message | Invalid output |

### Step 3: Minimum Set of Test Cases

| #TC | Partitions Covered | A | B | Expected Output |
| --- | --- | --- | --- | --- |
| TC1 | EC1, EC5, EC9 | 10 | 9 | 19 |
| TC2 | EC2, EC10 | −102 | 9 | Invalid Input |
| TC3 | EC3 | 102 | 9 | Invalid Input |
| TC4 | EC4 | Abc | 9 | Invalid Input |
| TC5 | EC6 | 10 | −200 | Invalid Input |
| TC6 | EC7 | 10 | 200 | Invalid Input |
| TC7 | EC8 | 10 | 1.25 | Invalid Input |

> TC1 covers 3 valid ECs in one test case (EC1 + EC5 + EC9). TC2–TC7 each cover exactly one invalid EC.

### Step 4: BVA Test Cases

| #TC | Partition Tested | A | B | Expected Output | BVA Point |
| --- | --- | --- | --- | --- | --- |
| TC1 | A < −99 | −100 | 9 | Invalid Input | LB−1 of A |
| TC2 | −99 ≤ A ≤ 99 | −99 | 9 | −90 | LB of A |
| TC3 | −99 ≤ A ≤ 99 | −98 | 9 | −89 | LB+1 of A |
| TC4 | −99 ≤ A ≤ 99 | 98 | 9 | 107 | UB−1 of A |
| TC5 | −99 ≤ A ≤ 99 | 99 | 9 | 108 | UB of A |
| TC6 | A > 99 | 100 | 9 | Invalid Input | UB+1 of A |
| TC7 | B < −99 | 10 | −100 | Invalid Input | LB−1 of B |
| TC8 | −99 ≤ B ≤ 99 | 10 | −99 | −89 | LB of B |
| TC9 | −99 ≤ B ≤ 99 | 10 | −98 | −88 | LB+1 of B |
| TC10 | −99 ≤ B ≤ 99 | 10 | 98 | 108 | UB−1 of B |
| TC11 | −99 ≤ B ≤ 99 | 10 | 99 | 109 | UB of B |
| TC12 | B > 99 | 10 | 100 | Invalid Input | UB+1 of B |

> Note: B=9 is held constant when testing A boundaries; A=10 is held constant when testing B boundaries. Interior points (points 1, 3 in the diagram) are not shown separately here as LB+1 and UB-1 serve a similar role in this example.