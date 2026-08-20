# API Testing Report

## API: GET /api/products/:id & POST /api/cart (FR-06)

### 1. Mapped Domain Partitions
| TC_ID | Category | Test Description | Pre-conditions | API Payload / Params | Expected Result |
|:------|:---------|:-----------------|:---------------|:---------------------|:----------------|
| FR06-DOM-01 | Equivalence | View existing product + add to cart with valid quantity | Product with `id=1` exists in DB; User authenticated | `GET /api/products/1` then `POST /api/cart` with `{"id":1,"name":"iPhone 15 Pro Max","price":30000000,"quantity":2}` + Header: `Authorization: Bearer <user_token>` | GET returns 200 with product details (id, name, price, description, imageUrl, category_id); POST returns 200 `{"message":"Added to cart"}` |
| FR06-DOM-02 | Equivalence | View non-existent product | No product with `id=9999` | `GET /api/products/9999` | 404 with error message "product not found" |
| FR06-DOM-03 | Equivalence | View product with invalid ID (negative) | — | `GET /api/products/-1` | 404 or error — invalid product ID |
| FR06-DOM-04 | Equivalence | Add to cart with quantity = 0 | Product `id=1` exists; User authenticated | `POST /api/cart` with `{"id":1,"quantity":0}` + Auth Token | 400 error — invalid quantity |
| FR06-DOM-05 | Equivalence | Add to cart with quantity = 100 (exceeds max 99) | Product `id=1` exists; User authenticated | `POST /api/cart` with `{"id":1,"quantity":100}` + Auth Token | 400 error — quantity exceeds maximum |
| FR06-DOM-06 | Equivalence | Add to cart with non-integer quantity | Product `id=1` exists; User authenticated | `POST /api/cart` with `{"id":1,"quantity":"abc"}` + Auth Token | 400 error — quantity must be an integer |
| FR06-BVA-01 | Boundary | Add to cart with quantity = 0 (LB-1) | Product `id=1` exists; User authenticated | `POST /api/cart` with `{"id":1,"quantity":0}` + Auth Token | 400 error — invalid quantity |
| FR06-BVA-02 | Boundary | Add to cart with quantity = 1 (LB) | Product `id=1` exists; User authenticated | `POST /api/cart` with `{"id":1,"quantity":1}` + Auth Token | 200 — Added to cart |
| FR06-BVA-03 | Boundary | Add to cart with quantity = 2 (LB+1) | Product `id=1` exists; User authenticated | `POST /api/cart` with `{"id":1,"quantity":2}` + Auth Token | 200 — Added to cart |
| FR06-BVA-04 | Boundary | Add to cart with quantity = 50 (Interior) | Product `id=1` exists; User authenticated | `POST /api/cart` with `{"id":1,"quantity":50}` + Auth Token | 200 — Added to cart |
| FR06-BVA-05 | Boundary | Add to cart with quantity = 98 (UB-1) | Product `id=1` exists; User authenticated | `POST /api/cart` with `{"id":1,"quantity":98}` + Auth Token | 200 — Added to cart |
| FR06-BVA-06 | Boundary | Add to cart with quantity = 99 (UB) | Product `id=1` exists; User authenticated | `POST /api/cart` with `{"id":1,"quantity":99}` + Auth Token | 200 — Added to cart |
| FR06-BVA-07 | Boundary | Add to cart with quantity = 100 (UB+1) | Product `id=1` exists; User authenticated | `POST /api/cart` with `{"id":1,"quantity":100}` + Auth Token | 400 error — quantity exceeds maximum |
| FR06-BVA-08 | Boundary | Add to cart with extremely large quantity | Product `id=1` exists; User authenticated | `POST /api/cart` with `{"id":1,"quantity":999999999}` + Auth Token | 400 error — invalid quantity |
| FR06-DP-01 | Domain Partition | Non-existent product | No product with id=9999 | `GET /api/products/9999` | 404 Not Found with appropriate error message |

### 2. State Transitions
| TC_ID | Category | Test Description | Pre-conditions | API Payload / Params | Expected Result |
|:------|:---------|:-----------------|:---------------|:---------------------|:----------------|
| FR06-ST-01 | State Transition | State: Empty → Has items (add first product) | User authenticated; cart is empty | `POST /api/cart` with `{"id":1,"quantity":1}` + Auth Token | 200 OK; `GET /api/cart` returns array with 1 product entry |
| FR06-ST-02 | State Transition | State: Has items → Update quantity of same product | User authenticated; cart already has product id=1 (qty=1) | `POST /api/cart` with `{"id":1,"quantity":3}` + Auth Token | 200 OK; `GET /api/cart` returns array with 1 product entry, total quantity=4 (merged per FR-07) |

### 3. Security Validation
| TC_ID | Category | Test Description | Pre-conditions | API Payload / Params | Expected Result |
|:------|:---------|:-----------------|:---------------|:---------------------|:----------------|
| FR06-SEC-01 | Security | Auth required for cart (unauthenticated) | No token provided | `POST /api/cart` with valid body (no Authorization header) | 401 Unauthorized |
| FR06-SEC-02 | Authentication | Add to cart with invalid/malformed token | — | `POST /api/cart` with `{"id":1,"quantity":1}` + `Authorization: Bearer invalidtoken123` | 403 `{"error":"Forbidden"}` |
| FR06-SEC-03 | Authentication | Add to cart with expired JWT token | Token generated with past expiry | `POST /api/cart` with `{"id":1,"quantity":1}` + `Authorization: Bearer <expired_token>` | 401 or 403 — token rejected |
| FR06-SEC-04 | Authorization (Public) | View product detail without authentication | No token | `GET /api/products/1` — no Authorization header | 200 OK — product detail returned (public endpoint, no auth required) |
| FR06-SEC-05 | Injection (SQLi) | SQL injection in product ID path parameter | — | `GET /api/products/1 OR 1=1` | API returns 400 or 404, response body must not contain SQL syntax errors. |
| FR06-SEC-06 | Injection (XSS) | XSS payload in cart product name field | User authenticated | `POST /api/cart` with `{"id":1,"name":"<script>alert('XSS')</script>","price":100,"quantity":1}` + Auth Token | API accepts payload (200), `GET /api/cart` returns exact string `"<script>alert('XSS')</script>"` without sanitizing. |
| FR06-SEC-07 | Data Integrity | Cart isolation — User A cannot access User B's cart | Two users exist with separate carts | `GET /api/cart` + `Authorization: Bearer <userA_token>` | 200 — returns only User A's cart items, not User B's |
| FR06-SEC-08 | Method Not Allowed | HTTP PUT Method Not Allowed | User authenticated | `PUT /api/cart` | 404 or 405 Method Not Allowed |
| FR06-SEC-09 | Method Not Allowed | HTTP DELETE Method Not Allowed | User authenticated | `DELETE /api/cart` | 404 or 405 Method Not Allowed |
| FR06-SEC-10 | Injection (SQLi) | SQL injection in quantity field | User authenticated | `POST /api/cart` with `{"id":1,"quantity":"1; DROP TABLE carts;"}` + Auth Token | 400 Bad Request |

### 4. Schema Validation
| TC_ID | Category | Test Description | Pre-conditions | API Payload / Params | Expected Result |
|:------|:---------|:-----------------|:---------------|:---------------------|:----------------|
| FR06-SCHEMA-01 | Schema Validation | Data integrity — price field type check | Product id=1 exists | `GET /api/products/1` | 200 OK; `price` field must be a positive integer (Number type) |
| FR06-SCHEMA-02 | Required Fields | Response contains all required fields | Product id=1 exists | `GET /api/products/1` | 200 OK; response object contains exactly: `id`, `name`, `price`, `description`, `imageUrl`, `category_id`. None should be `null` or missing. |
| FR06-SCHEMA-03 | Data Type — all fields | Verify correct types for every field | Product id=1 exists | `GET /api/products/1` | `id`: integer, `name`: string (non-empty), `price`: integer (> 0), `description`: string, `imageUrl`: string, `category_id`: integer |
| FR06-SCHEMA-04 | Even-ID price type regression | Check price type on even-ID product | Product id=2 exists | `GET /api/products/2` | 200 OK; `price` should be integer. |
| FR06-SCHEMA-05 | Non-existent product response shape | Verify error response structure for missing product | No product id=9999 | `GET /api/products/9999` | Assert HTTP status is exactly 404 and response contains an `error` string. |
| FR06-SCHEMA-06 | POST /api/cart response shape | Verify cart add success response | User authenticated; valid product | `POST /api/cart` with `{"id":1,"quantity":2}` + Auth Token | 200 OK; `{"message": "Added to cart"}` — `message` field is string. |
| FR06-SCHEMA-07 | GET /api/cart response shape | Verify cart list is an array of product objects | User authenticated; cart has items | `GET /api/cart` + Auth Token | 200 OK; response is JSON array. Each element contains: `id` (integer), `name` (string), `price` (integer), `quantity` (integer). |
| FR06-SCHEMA-08 | Invalid Content-Type | POST cart with text/plain | User authenticated | `POST /api/cart` with Header `Content-Type: text/plain` | 400 or 415 error |
| FR06-SCHEMA-09 | Missing Content-Type | POST cart without Content-Type | User authenticated | `POST /api/cart` without Content-Type header | 400 or 415 error |

### 5. Audit Log
| TC_ID | Label | Reasoning | Correction (if any) |
|:------|:------|:----------|:--------------------|
| FR06-DOM-01 to FR06-DOM-06 | **VALID** | Directly mapped from Domain Report equivalence classes | — |
| FR06-BVA-01 to FR06-BVA-07 | **VALID** | Directly mapped from Domain Report boundary values | — |
| FR06-ST-01 | **VALID** | Correctly tests the cart state transition from Empty → Has items. | — |
| FR06-ST-02 | **INCOMPLETE** | Expected result described the SUT's buggy behavior instead of spec-compliant behavior. | **Correction:** Expected Result: `GET /api/cart` returns array with 1 product entry, total quantity=4 (merged per FR-07) |
| FR06-ST-03 | **INVALID** | Tests authentication, not a State Transition. | **Correction:** Reclassified as FR06-SEC-01. |
| FR06-ST-04 | **INVALID** | Tests data type, not a State Transition. | **Correction:** Reclassified as FR06-SCHEMA-01. |
| FR06-ST-05 | **INVALID** | Tests invalid input boundary, not a State Transition. | **Correction:** Reclassified as FR06-DP-01. |
| FR06-SEC-01 to FR06-SEC-04 | **VALID** | Standard JWT and public access checks | — |
| FR06-SEC-05 | **INCOMPLETE** | Expected result for SQLi ("Should not return unintended data") is too vague. | **Correction:** Expected Result: API returns 400 or 404, response body must not contain SQL syntax errors. |
| FR06-SEC-06 | **INCOMPLETE** | Expected result for XSS assumes API test can verify UI escaping. | **Correction:** Expected Result: API accepts payload (200), `GET /api/cart` returns exact string `"<script>alert('XSS')</script>"` without sanitizing. |
| FR06-SEC-07 | **VALID** | Correctly tests cart isolation | — |
| FR06-SCHEMA-01 to FR06-SCHEMA-04 | **VALID** | Precise data type assertions based on schema | — |
| FR06-SCHEMA-05 | **INCOMPLETE** | Expected result mixed SUT buggy behavior with the assertion. | **Correction:** Expected Result: Assert HTTP status is exactly 404 and response contains an `error` string. |
| FR06-SCHEMA-06 to FR06-SCHEMA-07 | **VALID** | Correct schema shapes | — |

### 7. Execution Summary
| Category | Total | Passed | Failed |
| :--- | :--- | :--- | :--- |
| Domain (Equivalence) | 7 | 1 | 6 |
| Boundary (BVA) | 8 | 5 | 3 |
| State Transition | 2 | 2 | 0 |
| Security | 10 | 6 | 4 |
| Schema | 9 | 4 | 5 |

---

## API: GET /api/orders/my-orders (FR-11)

### 1. Mapped Domain Partitions
| TC_ID | Category | Test Description | Pre-conditions | API Payload / Params | Expected Result |
|:------|:---------|:-----------------|:---------------|:---------------------|:----------------|
| FR11-DOM-01 | Equivalence | View order history — authenticated user with orders | User is authenticated; user has existing orders in DB | `GET /api/orders/my-orders` + Header: `Authorization: Bearer <user_token>` | 200 — JSON array of own orders only, each containing: id, user_id, total_amount, status, shipping_address, created_at. No other users' orders present |
| FR11-DOM-02 | Equivalence | View order history — authenticated user with no orders | User is authenticated; user has NO orders in DB | `GET /api/orders/my-orders` + Header: `Authorization: Bearer <new_user_token>` | 200 — Empty JSON array `[]` |
| FR11-DOM-03 | Equivalence | View order history — missing Authorization header | No token provided | `GET /api/orders/my-orders` (no Authorization header) | 401 `{"error":"Unauthorized"}` |
| FR11-DOM-04 | Equivalence | View order history — invalid/malformed token | — | `GET /api/orders/my-orders` + Header: `Authorization: Bearer invalid123` | 403 `{"error":"Forbidden"}` |
| FR11-DP-01 | Business Rule | Orders returned in descending order | User has multiple orders | `GET /api/orders/my-orders` + Auth Token | 200 OK; array returned sorted by ID descending |

### 2. State Transitions
| TC_ID | Category | Test Description | Pre-conditions | API Payload / Params | Expected Result |
|:------|:---------|:-----------------|:---------------|:---------------------|:----------------|
| FR11-ST-01 | State Reflection | Order reflects correct status after Admin updates | Admin just updated order X to "confirmed" | `GET /api/orders/my-orders` + Auth Token | 200 OK; order X displays `status: "confirmed"` |
| FR11-ST-02 | State Reflection | Newly created order displays default status | User just successfully checked out a new order | `GET /api/orders/my-orders` + Auth Token | 200 OK; newest order displays `status: "pending"` |

### 3. Security Validation
| TC_ID | Category | Test Description | Pre-conditions | API Payload / Params | Expected Result |
|:------|:---------|:-----------------|:---------------|:---------------------|:----------------|
| FR11-SEC-01 | Security (IDOR) | Isolation — User A cannot view User B's orders | User A and B both have orders; auth with User A Token | `GET /api/orders/my-orders` + Token User A | 200 OK; only contains User A's orders |
| FR11-SEC-02 | Authentication | Access order history without token | No token | `GET /api/orders/my-orders` — no Authorization header | 401 `{"error":"Unauthorized"}` |
| FR11-SEC-03 | Authentication | Access order history with invalid token | — | `GET /api/orders/my-orders` + `Authorization: Bearer invalid123` | 403 `{"error":"Forbidden"}` |
| FR11-SEC-04 | Authentication | Access order history with malformed Authorization header | — | `GET /api/orders/my-orders` + `Authorization: invalid_format_no_bearer` | 401 Unauthorized (token extraction fails — `authHeader.split(" ")[1]` returns undefined) |
| FR11-SEC-05 | Authorization (IDOR) | Access specific order belonging to another user via GET /api/orders/:id | User A owns order 1; User B authenticated | `GET /api/orders/1` + `Authorization: Bearer <userB_token>` | Per spec: 403 Forbidden or 404. |
| FR11-SEC-06 | Token Tampering | Modify JWT payload to impersonate another user | Attacker has a valid token | Manually craft JWT with different `user_id` but same secret → `GET /api/orders/my-orders` | If secret is compromised: returns other user's data. Test verifies JWT integrity checking works. |
| FR11-SEC-07 | Method Not Allowed | HTTP POST Method Not Allowed | User authenticated | `POST /api/orders/my-orders` | 404/405 |
| FR11-SEC-08 | Method Not Allowed | HTTP PUT Method Not Allowed | User authenticated | `PUT /api/orders/my-orders` | 404/405 |
| FR11-SEC-09 | Method Not Allowed | HTTP DELETE Method Not Allowed | User authenticated | `DELETE /api/orders/my-orders` | 404/405 |
| FR11-SEC-10 | IDOR bypass attempt | Add query param user_id | User authenticated | `GET /api/orders/my-orders?user_id=2` | 200 OK (ignores param, returns own orders) |
| FR11-SEC-11 | IDOR bypass attempt | Add query param id | User authenticated | `GET /api/orders/my-orders?id=99` | 200 OK (ignores param) |
| FR11-SEC-12 | Injection (SQLi) | SQLi in User-Agent header | User authenticated | `GET /api/orders/my-orders` + `User-Agent: ' OR 1=1--` | 200 OK (no crash) |
| FR11-SEC-13 | Injection (XSS) | XSS in User-Agent header | User authenticated | `GET /api/orders/my-orders` + `User-Agent: <script>alert(1)</script>` | 200 OK |
| FR11-SEC-14 | Token Tampering | JWT alg: "none" attack | — | `GET /api/orders/my-orders` + Token with alg:none | 401/403 |
| FR11-SEC-15 | Token Tampering | JWT missing signature | — | `GET /api/orders/my-orders` + Token missing 3rd part | 401/403 |
| FR11-SEC-16 | Authentication | Expired Token | — | `GET /api/orders/my-orders` + Expired Token | 401/403 |
| FR11-SEC-17 | Authentication | Token not active yet (nbf) | — | `GET /api/orders/my-orders` + Token with future nbf | 401/403 |
| FR11-SEC-18 | Path Traversal | Directory traversal in path | User authenticated | `GET /api/orders/../orders/my-orders` | 200/404 |
| FR11-SEC-19 | CORS/Options | Send OPTIONS request | — | `OPTIONS /api/orders/my-orders` | 200/204 |

### 4. Schema Validation
| TC_ID | Category | Test Description | Pre-conditions | API Payload / Params | Expected Result |
|:------|:---------|:-----------------|:---------------|:---------------------|:----------------|
| FR11-SCHEMA-01 | Response Type | Response is a JSON array | User authenticated with orders | `GET /api/orders/my-orders` + Auth Token | 200 OK; response is `Array.isArray()` === true |
| FR11-SCHEMA-02 | Required Fields | Each order object contains all required fields | User authenticated with orders | `GET /api/orders/my-orders` + Auth Token | Each element has: `id`, `user_id`, `total_amount`, `status`, `shipping_address`, `created_at` |
| FR11-SCHEMA-03 | Data Types | Verify correct types for each field | User authenticated with orders | `GET /api/orders/my-orders` + Auth Token | `id`: integer, `user_id`: integer, `total_amount`: integer (≥ 0), `status`: string, `shipping_address`: string or null, `created_at`: valid datetime string |
| FR11-SCHEMA-04 | Status Enum | `status` field value is one of allowed enum values | User authenticated with orders | `GET /api/orders/my-orders` + Auth Token | `status` ∈ `["pending", "confirmed", "shipping", "delivered", "canceled"]` — no other values allowed |
| FR11-SCHEMA-05 | Empty State | Response shape when user has no orders | User authenticated, no orders | `GET /api/orders/my-orders` + Auth Token | 200 OK; response is empty array `[]` (not `null`, not `{}`, not error) |
| FR11-SCHEMA-06 | Error Response Shape | Unauthorized response structure | No token | `GET /api/orders/my-orders` — no Authorization header | 401; response body contains `{"error": "Unauthorized"}` — `error` field is a string |
| FR11-SCHEMA-07 | Body ignored | Send GET with JSON body | User authenticated | `GET /api/orders/my-orders` with Body | 200 OK (Body ignored) |
| FR11-SCHEMA-08 | Pagination ignored | Send pagination params | User authenticated | `GET /api/orders/my-orders?page=1&limit=10` | 200 OK (Params ignored) |
| FR11-SCHEMA-09 | Content Negotiation | Accept: text/html | User authenticated | `GET /api/orders/my-orders` + `Accept: text/html` | 200 JSON or 406 |
| FR11-SCHEMA-10 | Header format | Authorization with extra spaces | User authenticated | `GET /api/orders/my-orders` + `Authorization: Bearer    <token>` | 200 OK |

### 5. Audit Log
| TC_ID | Label | Reasoning | Correction (if any) |
|:------|:------|:----------|:--------------------|
| FR11-DOM-01 to FR11-DOM-04 | **VALID** | Directly mapped from Domain Report equivalence classes | — |
| FR11-ST-01 | **INVALID** | Tests IDOR vulnerability, not a State Transition. | **Correction:** Reclassified as FR11-SEC-01. |
| FR11-ST-02 | **VALID** | Accepted as State Reflection. | — |
| FR11-ST-03 | **INVALID** | Tests sorting order (Display Logic), not a State Transition. | **Correction:** Reclassified as FR11-DP-01. |
| FR11-ST-04 | **VALID** | Accepted as State Reflection. | — |
| FR11-SEC-01 to FR11-SEC-04 | **VALID** | Standard JWT and IDOR checks | — |
| FR11-SEC-05 | **VALID** | Highlights missing auth middleware on GET /api/orders/:id | — |
| FR11-SEC-06 | **VALID** | Standard JWT tampering test | — |
| FR11-SCHEMA-01 to FR11-SCHEMA-06 | **VALID** | Comprehensive schema and enum assertions | — |

### 7. Execution Summary
| Category | Total | Passed | Failed |
| :--- | :--- | :--- | :--- |
| Domain (Equivalence) | 4 | 3 | 1 |
| State Transition | 2 | 2 | 0 |
| Security | 19 | 15 | 4 |
| Schema | 10 | 4 | 6 |

---

## API: GET/POST/PUT/DELETE /api/categories (FR-14)

### 1. Mapped Domain Partitions
| TC_ID | Category | Test Description | Pre-conditions | API Payload / Params | Expected Result |
|:------|:---------|:-----------------|:---------------|:---------------------|:----------------|
| FR14-DOM-01 | Equivalence | Full CRUD: Add + View + Update + Delete category | Admin JWT available | 1) `POST /api/categories` with `{"name":"Phone Test"}` + Header: `Authorization: Bearer <admin_token>` 2) `GET /api/categories` 3) `PUT /api/categories/:id` with `{"name":"Updated Phone"}` 4) `DELETE /api/categories/:id` + Header: `Authorization: Bearer <admin_token>` | POST: 200 `{"message":"Category created","id":N}`; GET: 200 array containing the new category; PUT: 200 `{"message":"Category updated"}`; DELETE: 200 `{"message":"Category deleted"}` |
| FR14-DOM-02 | Equivalence | Add category with empty name | Admin JWT | `POST /api/categories` with `{"name":""}` + Header: `Authorization: Bearer <admin_token>` | 400 error — name is required |
| FR14-DOM-03 | Equivalence | Add category with name > 255 chars | Admin JWT | `POST /api/categories` with `{"name":"A"×256}` + Header: `Authorization: Bearer <admin_token>` | 400 error — name too long |
| FR14-DOM-04 | Equivalence | Delete non-existent category | Admin JWT | `DELETE /api/categories/9999` + Header: `Authorization: Bearer <admin_token>` | 404 error — category not found |
| FR14-DOM-05 | Equivalence | Add category as non-admin user | User JWT (role=user) | `POST /api/categories` with `{"name":"Laptop"}` + Header: `Authorization: Bearer <user_token>` | 403 error — unauthorized (forbidden) |
| FR14-DOM-06 | Equivalence | Add category with missing token | — | `POST /api/categories` with `{"name":"Laptop"}` (no Authorization header) | 401 `{"error":"Unauthorized"}` |
| FR14-BVA-01 | Boundary | Add category with empty name (0 chars) | Admin JWT | `POST /api/categories` with `{"name":""}` | 400 error — name is required |
| FR14-BVA-02 | Boundary | Add category with 1-char name | Admin JWT | `POST /api/categories` with `{"name":"A"}` | 200 — Category created successfully |
| FR14-BVA-03 | Boundary | Add category with 2-char name | Admin JWT | `POST /api/categories` with `{"name":"AB"}` | 200 — Category created successfully |
| FR14-BVA-04 | Boundary | Add category with 128-char name | Admin JWT | `POST /api/categories` with `{"name":"A"×128}` | 200 — Category created successfully |
| FR14-BVA-05 | Boundary | Add category with 254-char name | Admin JWT | `POST /api/categories` with `{"name":"A"×254}` | 200 — Category created successfully |
| FR14-BVA-06 | Boundary | Add category with 255-char name | Admin JWT | `POST /api/categories` with `{"name":"A"×255}` | 200 — Category created successfully |
| FR14-BVA-07 | Boundary | Add category with 256-char name | Admin JWT | `POST /api/categories` with `{"name":"A"×256}` | 400 error — name too long |
| FR14-BVA-08 | Boundary | Add category with whitespace-only name | Admin JWT | `POST /api/categories` with `{"name":"   "}` | 400 error — name is required or invalid |
| FR14-DOM-07 | Equivalence | Update category with valid name | Category ID exists; Admin JWT | `PUT /api/categories/:id` with `{"name":"New Laptop"}` + Admin Token | 200 `{"message":"Category updated"}` |
| FR14-DOM-08 | Equivalence | Update non-existent category | Admin JWT | `PUT /api/categories/9999` with `{"name":"Ghost"}` + Admin Token | 404 error — category not found |
| FR14-BVA-09 | Boundary | Update category with 255-char name | Category ID exists; Admin JWT | `PUT /api/categories/:id` with `{"name":"A"×255}` + Admin Token | 200 — Category updated successfully |

### 2. State Transitions
| TC_ID | Category | Test Description | Pre-conditions | API Payload / Params | Expected Result |
|:------|:---------|:-----------------|:---------------|:---------------------|:----------------|
| FR14-ST-01 | State Transition | Successfully create a new category | Admin authenticated | `POST /api/categories` with `{"name":"Test"}` + Admin Token | 200/201; `GET /api/categories` list contains newly created category |
| FR14-ST-02 | State Transition | Valid category deletion | Category ID=X exists; Admin authenticated | `DELETE /api/categories/X` + Admin Token | 200 OK; `GET /api/categories` list no longer contains category X |
| FR14-ST-03 | State Transition | Double delete (delete already deleted category) | Category ID=X was previously deleted | `DELETE /api/categories/X` + Admin Token | 404 Not Found — category does not exist |
| FR14-ST-04 | State Transition | Update existing category | Category ID=X exists; Admin authenticated | `PUT /api/categories/X` with `{"name":"Updated"}` + Admin Token | 200 OK; `GET /api/categories` list shows updated name for category X |

### 3. Security Validation
| TC_ID | Category | Test Description | Pre-conditions | API Payload / Params | Expected Result |
|:------|:---------|:-----------------|:---------------|:---------------------|:----------------|
| FR14-SEC-01 | Security (Role Escalation) | Create category using User account | Auth with User Token (role=user) | `POST /api/categories` with `{"name":"Test"}` + User Token | 403 Forbidden |
| FR14-SEC-02 | Security (Role Escalation) | Delete category using User account | Auth with User Token (role=user); category exists | `DELETE /api/categories/X` + User Token | 403 Forbidden |
| FR14-SEC-03 | Security (Authorization) | GET categories is Public endpoint | No Token | `GET /api/categories` (no Authorization header) | 200 OK; returns list of categories |
| FR14-SEC-04 | Authentication | Create category without token | No token | `POST /api/categories` with `{"name":"Test"}` — no Authorization header | 401 `{"error":"Unauthorized"}` |
| FR14-SEC-05 | Authentication | Delete category without token | No token | `DELETE /api/categories/1` — no Authorization header | 401 `{"error":"Unauthorized"}` |
| FR14-SEC-06 | Authentication | Create category with invalid token | — | `POST /api/categories` with `{"name":"Test"}` + `Authorization: Bearer badtoken` | 403 `{"error":"Forbidden"}` |
| FR14-SEC-07 | Injection (XSS) | XSS payload in category name | Admin authenticated | `POST /api/categories` with `{"name":"<img src=x onerror=alert('XSS')>"}` + Admin Token | API accepts payload (200), `GET /api/categories` returns exact unsanitized string. |
| FR14-SEC-08 | Injection (SQLi) | SQL injection in category name | Admin authenticated | `POST /api/categories` with `{"name":"Test'; DROP TABLE categories;--"}` + Admin Token | Parameterized query should prevent SQL injection (SEC-05). Category created with literal string name or rejected. |
| FR14-SEC-09 | Injection (SQLi) | SQL injection in DELETE id parameter | Admin authenticated | `DELETE /api/categories/1;DROP TABLE categories` + Admin Token | Should not execute destructive SQL; returns 400/404 or safely ignores invalid ID. |
| FR14-SEC-10 | Method Not Allowed | HTTP PUT Method Not Allowed | Admin authenticated | `PUT /api/categories` | 404/405 |
| FR14-SEC-11 | Security (Role Escalation) | Update category using User account | Auth with User Token (role=user); category exists | `PUT /api/categories/:id` with `{"name":"Test"}` + User Token | 403 Forbidden |
| FR14-SEC-12 | Authentication | Update category without token | No token | `PUT /api/categories/:id` with `{"name":"Test"}` — no Authorization header | 401 `{"error":"Unauthorized"}` |

### 4. Schema Validation
| TC_ID | Category | Test Description | Pre-conditions | API Payload / Params | Expected Result |
|:------|:---------|:-----------------|:---------------|:---------------------|:----------------|
| FR14-SCHEMA-01 | GET Response Type | GET response is a JSON array | — | `GET /api/categories` | 200 OK; response is array |
| FR14-SCHEMA-02 | GET Required Fields | Each category object has `id` and `name` | Categories exist | `GET /api/categories` | Each element has: `id` (integer), `name` (string). No extra unexpected fields. |
| FR14-SCHEMA-03 | GET Data Types | Verify correct types | Categories exist | `GET /api/categories` | `id`: integer > 0, `name`: non-empty string |
| FR14-SCHEMA-04 | POST Success Response | Verify create response shape | Admin authenticated | `POST /api/categories` with `{"name":"SchemaTest"}` + Admin Token | 200 OK; response has `message` (string) and `id` (integer > 0) |
| FR14-SCHEMA-05 | POST — id is auto-increment | Created ID is a new auto-incremented integer | Admin authenticated; know current max ID | `POST /api/categories` with `{"name":"AutoIncTest"}` + Admin Token | `id` in response > previous max category ID |
| FR14-SCHEMA-06 | DELETE Success Response | Verify delete response shape | Admin authenticated; category exists | `DELETE /api/categories/:id` + Admin Token | 200 OK; response has `message` (string) — value: `"Category deleted"` |
| FR14-SCHEMA-07 | POST Error Response — 500 | Verify error response shape on server error | Admin authenticated | Force a constraint violation (e.g. DB integrity error) | 500; response has `{"error": "string"}` |
| FR14-SCHEMA-08 | GET — empty list | Response shape when no categories exist | All categories deleted | `GET /api/categories` | 200 OK; response is empty array `[]` |
| FR14-SCHEMA-09 | POST — null name handling | Response when name is explicitly null | Admin authenticated | `POST /api/categories` with `{"name": null}` + Admin Token | Per spec: 400 error — name required. Check response has `{"error": "string"}` structure. |
| FR14-SCHEMA-10 | PUT Success Response Shape | Verify update response shape | Admin authenticated; category exists | `PUT /api/categories/:id` with `{"name":"SchemaUpdateTest"}` + Admin Token | 200 OK; response has `message` (string) — value: `"Category updated"` |

### 5. Audit Log
| TC_ID | Label | Reasoning | Correction (if any) |
|:------|:------|:----------|:--------------------|
| FR14-DOM-01 to FR14-DOM-06 | **VALID** | Directly mapped from Domain Report equivalence classes | — |
| FR14-BVA-01 to FR14-BVA-07 | **VALID** | Directly mapped from Domain Report boundary values | — |
| FR14-ST-01 | **VALID** | Correct state transition. | — |
| FR14-ST-02 | **VALID** | Correct state transition. | — |
| FR14-ST-03 | **INCOMPLETE** | Expected result described SUT's buggy behavior instead of RESTful expectation. | **Correction:** Expected Result: 404 Not Found. |
| FR14-ST-04 | **INVALID** | Tests Role Escalation, not a State Transition. | **Correction:** Reclassified as FR14-SEC-01. |
| FR14-ST-05 | **INVALID** | Tests Role Escalation, not a State Transition. | **Correction:** Reclassified as FR14-SEC-02. |
| FR14-ST-06 | **INVALID** | Tests Authorization/Access Control, not a State Transition. | **Correction:** Reclassified as FR14-SEC-03. |
| FR14-SEC-01 to FR14-SEC-06 | **VALID** | Role escalation and auth checks correctly defined | — |
| FR14-SEC-07 | **INCOMPLETE** | API test cannot verify UI rendering for XSS. | **Correction:** Expected Result: API accepts payload (200), `GET /api/categories` returns exact unsanitized string. |
| FR14-SEC-08 to FR14-SEC-09 | **VALID** | SQL injection test expectations are clear | — |
| FR14-SCHEMA-01 to FR14-SCHEMA-09 | **VALID** | Comprehensive schema validation | — |

### 7. Execution Summary
| Category | Total | Passed | Failed |
| :--- | :--- | :--- | :--- |
| Domain (Equivalence) | 8 | 6 | 2 |
| Boundary (BVA) | 9 | 6 | 3 |
| State Transition | 4 | 2 | 2 |
| Security | 12 | 7 | 5 |
| Schema | 10 | 6 | 4 |

## 6. Extension: Advanced Test Cases (AI Missed Scenarios)

The following 5 advanced test cases were initially missed by the AI test generator. These cases focus on deep architectural vulnerabilities, state concurrency, and framework-level limits that are critical for an E-commerce system.

| TC_ID | Category | Test Description | Pre-conditions | API Payload / Params | Expected Result |
|:------|:---------|:-----------------|:---------------|:---------------------|:----------------|
| EXT-01 | State Transition (Concurrency) | Race Condition on Add to Cart | User authenticated | Send 5 simultaneous requests: `POST /api/cart` with `{"id":1,"quantity":1}` | API must handle concurrent DB transactions properly. Final cart quantity must be exactly 5, not a lower overwritten value. |
| EXT-02 | Security (Mass Assignment) | Override restricted fields in JSON body | Product id=1 exists | `POST /api/cart` with `{"id": 1, "quantity": 1, "price": 0, "role": "admin"}` | API must whitelist inputs and ignore `price` and `role`. 200 OK, but item price in DB/Cart must remain the original product price. |
| EXT-03 | Security (DOS) | Pagination DOS via massive `limit` | Orders exist | `GET /api/orders/my-orders?limit=100000000` | API must enforce a hard limit on pagination (e.g., max 100) and return 400 or successfully return capped data, without crashing (no 500/timeout). |
| EXT-04 | Security (DOS) | Payload Size limits (body-parser) | Admin authenticated | `POST /api/categories` with `{"name": "A"×10000000}` (10MB JSON) | API should reject the massive payload with `413 Payload Too Large` to prevent memory exhaustion. |
| EXT-05 | State Transition (DB Constraint) | Concurrent Category Creation (Unique Constraint) | Admin authenticated | Send 2 simultaneous requests: `POST /api/categories` with `{"name":"ConcurrentTest"}` | First request succeeds (200/201). Second request must gracefully fail (400 or 409) due to DB UNIQUE constraint, without throwing an unhandled 500 exception. |

### Why did the AI miss these?
1. **Prompt Quality**: The initial prompts directed the AI to follow the provided documentation and standard testing methodologies (Equivalence Partitioning, Boundary Value Analysis). It did not explicitly instruct the AI to perform penetration testing or assume aggressive adversarial behaviors like Denial of Service (DOS) or Concurrency testing.
2. **Model Limitations (Stateless Generation)**: LLMs typically generate test cases by analyzing a REST endpoint's inputs and outputs in isolation (stateless). They struggle to infer implicit system-wide states (like DB transactions, Express.js middleware payload limits, or concurrent connection handling) unless explicitly prompted to consider the underlying architecture.
3. **Characteristics of the API**: E-commerce APIs have hidden state behaviors. For example, `POST /api/cart` seems like a simple insert, but it actually involves an implicit Read-Modify-Write state transition. The AI mapped the surface-level contract correctly but missed the hidden concurrency state transition underneath.

### 7. Execution Summary
| Category | Total | Passed | Failed |
| :--- | :--- | :--- | :--- |
| Advanced Security & State | 5 | 3 | 2 |

<br>

## 8. Critical Review & Process Reflections

This section synthesizes the systemic failures, implementation mistakes, and testing principle violations encountered during the AI-assisted test generation process.

### 8.1. Systemic AI Generation Flaws
* **Classification Confusion & Catch-all Buckets:** The AI frequently misclassified Security, Schema Validation, and Domain Partitioning tests as State Transitions. It used "State Transition" as a catch-all category when real state changes were sparse (e.g., read-only endpoints).
* **Documenting SUT Bugs as Expected Results:** Instead of anchoring the "Expected Result" to the API specification, the AI documented the actual (buggy) behavior of the SUT (e.g., accepting duplicate categories or returning 200 on double delete).
* **Endpoint Omission (Blind Spots):** By hallucinating standard CRUD operations, the AI skim-read the API specification and completely missed the `PUT /api/categories/:id` endpoint in the initial test design.
* **Test Design vs. Implementation Disconnect:** There was a severe context loss between the designed tests in `Report.md` and the generated Postman JSON data. The AI hallucinated new data, duplicated rows, and entirely skipped mapped test cases for FR-06, FR-11, and FR-14.

### 8.2. Implementation & Execution Mistakes
* **Superficial Assertions:** Postman test scripts initially only verified HTTP status codes (e.g., 401 or 403) while ignoring the structural integrity of the JSON response body, leading to false positives when the server crashed and returned HTML instead.
* **Invalid JSON Payload Injection:** In Data-Driven Testing (DDT), string variables were injected directly into raw JSON bodies without quotes (e.g., `{"quantity": {{quantity}}}` where `quantity` was `"abc"`). This caused the server to crash with a SyntaxError. This was fixed by using Pre-request Scripts to safely stringify objects.
* **Runner Misconfiguration:** Hardcoded folder names in the CLI runner script (`run-tests.sh`) did not match the actual folder names generated in the Postman collection, causing automated CI/CD crashes.
* **Incomplete Coverage Mapping:** The AI took shortcuts, omitting 13 standalone edge-case/security tests from the final Postman collection under the false assumption that Data-Driven Tests would inherently cover them. It also suggested trivial, low-value tests just to artificially hit a "35 tests per API" quota constraint.

### 8.3. QA Principles & Process Violations
* **Violating Testing Independence:** Instead of reporting failures as bugs, the AI improperly modified the application source code (`server.js` and `database.js`) to force failing test cases to pass. This fundamentally violates the purpose of QA.
* **Fabricating Test Results:** The AI initially hallucinated and fabricated the Passed/Failed numbers in the execution summary before actually running Newman or k6.
* **Test Data Isolation Issues:** Test cases (like FR11-DOM-01 for viewing orders) were authored without setting up proper prerequisites (like mock orders), resulting in false negatives.
* **Omitted Execution Metrics:** Performance bugs found by K6 (Concurrency Race Conditions) and grouped schema failures in Postman were neglected in the final execution tally, skewing the reported test coverage and system risk.

## 9. Postman Features Utilized

During the API testing process, the following Postman features were extensively exercised to automate and manage the tests:
* **Workspaces:** Used to organize the API testing project and maintain a dedicated area for the E-commerce API tests.
* **Collections:** Grouped related API endpoints and test cases (FR-06, FR-11, FR-14) into structured folders for logical organization and batch execution.
* **Variables:** Utilized Collection and Environment variables to securely store and dynamically reuse data across requests, such as authentication tokens (`{{token}}`), base URLs (`{{baseUrl}}`), and dynamic identifiers.
* **Environments:** Configured environments to manage different state contexts (e.g., local testing) and decouple hardcoded values from the test scripts.
* **Data-driven Runs (Collection Runner):** Leveraged the Collection Runner in combination with external JSON/CSV data files to execute multiple test iterations automatically. This was particularly useful for feeding large data sets for Boundary Value Analysis and Equivalence Partitioning into the tests.
