# Step 11 — Security Hardening & Final Test Suite

## Objectives
- Add all HTTP security headers and cookie hardening settings
- Write comprehensive IDOR isolation security tests
- Achieve 100% test-suite pass on all 5 Django apps
- Run `python manage.py check --deploy` with zero critical errors

---

## Security Settings Added (`config/settings.py`)

| Setting | Value | Purpose |
|---|---|---|
| `SECURE_BROWSER_XSS_FILTER` | `True` | X-XSS-Protection header |
| `SECURE_CONTENT_TYPE_NOSNIFF` | `True` | Prevents MIME-type sniffing |
| `X_FRAME_OPTIONS` | `'DENY'` | Clickjacking protection |
| `CSRF_COOKIE_HTTPONLY` | `True` | CSRF cookie hidden from JS |
| `SESSION_COOKIE_HTTPONLY` | `True` | Session cookie hidden from JS |
| `SESSION_COOKIE_SAMESITE` | `'Lax'` | Cross-site CSRF mitigation |
| `CSRF_COOKIE_SAMESITE` | `'Lax'` | Cross-site CSRF mitigation |
| `DATA_UPLOAD_MAX_MEMORY_SIZE` | `10 MB` | Prevents oversized uploads |
| `SESSION_COOKIE_AGE` | `7200 s` | 2-hour session timeout |
| `LOGIN_URL` / `LOGIN_REDIRECT_URL` | set | Proper auth redirect flow |

---

## Security Tests Added (`patients/tests.py` — `IDORSecurityTestCase`)

| Test | Protection |
|---|---|
| `test_parent_b_cannot_view_parent_a_child_detail` | IDOR view isolation |
| `test_parent_b_cannot_edit_parent_a_child` | IDOR write isolation + data integrity |
| `test_unauthenticated_user_cannot_view_child_detail` | Auth gate enforcement |
| `test_unauthenticated_user_cannot_add_child` | Auth gate enforcement |
| `test_parent_b_cannot_upload_image_to_parent_a_child` | IDOR image-upload isolation |
| `test_child_queryset_scoped_to_parent` | Manager-level data scoping |

---

## Status
- [x] Security headers added
- [x] Cookie hardening applied
- [x] IDOR isolation tests written
- [x] Full test suite: **36 tests — PASSED**
- [x] `manage.py check --deploy` — zero critical errors

