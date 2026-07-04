# LOG

## 2026-07-04

### Initial Project Scan

**Files:**
- `app.py` — Entry point, creates and runs the Flask app
- `app/__init__.py` — Flask app factory, DB init, login manager setup
- `app/auth.py` — Blueprint: login, setup (first-time user creation), logout
- `app/pages.py` — Blueprint: home (inbox/browse), send, settings, delete, move, reload, status
- `app/models.py` — SQLAlchemy models: User, Connection, Settings
- `app/imap_functions.py` — IMAP helper functions (sort folders, message list, get body, move/delete)
- `app/templates/` — 8 HTML templates (base, home, login, setup, send, settings, pagination, reload)
- `app/static/css/main.css` — Minimal CSS (black bg, top button, invisible container)
- `app/static/img/favicon.ico` — Favicon
- `tests/test_web_pages.py` — Unit tests with mocked IMAP/SMTP
- `Dockerfile` — Python 3.14-slim + pi agent + rtk + gh CLI
- `etc/` — models.json, pre-commit, rtk-installer.sh
- `.env` — DEEPSEEK_API_KEY, PASS=''

**Current State:**
- Single-user only (no multi-account support)
- Basic IMAP folder browsing with pagination
- Send/reply/forward/draft via SMTP
- Delete (trash or permanent) configurable in settings
- Move message between folders via dropdown
- JS polling for new messages (every 10s)
- Settings: General (msgs per page, delete behavior), Connection (SMTP/IMAP host/port), User (email/password)
- Password stored in .env file, app reloads on password change via signal

**From Todos.txt — Missing:**
- Testing (basic tests exist but minimal coverage)
- Richly formatted messages / attachments in view
- Multi-user accounts
- Logging (imap/smtp, db, exceptions, errors)
- Input validation / proper HTTP response codes
- CC and BCC on outgoing messages
- File attachments on send
- SMTP auth — PASS is loaded once at import from .env, not refreshed if changed by settings page (only reload endpoint triggers hard restart)

**Notable Issues:**
- `pages.py` imports `PASS` at module level from `.env`, meaning password changes only take effect after a full app reload via `/reload`
- `use_imap()` ignores `imap_port` from Connection model — always uses default 143
- No error handling for missing query params in several routes (can cause 500s)
- Folder listing may crash on some IMAP servers (the `.split('"')[-1]` approach is fragile)
- `get_msg_body_string()` doesn't fall back nicely if content is not text/plain
- Settings page renders only the requested page tab but passes all variables regardless
- `trash()` route references undefined `folders` variable in error path
- JS polling URL in home.html hardcodes the folder from request args without URL encoding

---

### Fix: Missing `return redirect` in IMAP Auth Failed error paths

**Problem:** In `trash()`, `msg_move()`, and `status()` routes, when `use_imap()` returned `"Auth Failed"`, the code set `full_url` but never returned the redirect. Execution fell through to the next IMAP operation, using the string `"Auth Failed"` as an IMAP connection object — causing a crash.

**Routes fixed:**
- `trash()` (line 466)
- `msg_move()` (line 523)
- `status()` (line 570)

**Changes in `app/pages.py`:**
- Added `return redirect(full_url)` after setting the redirect URL in each `"Auth Failed"` block, matching the pattern already present in `home()` and `send()`.

---

### Fix: Sidebar/content overlap in home.html

**Problem:** Long folder names (e.g. `INBOX.Sent.Personal.Family.2024`) stretched the sidebar table beyond `col-xl-3`, pushing into the message content area. Also `col-xl-*` only works at ≥1200px — below that both columns were full-width in the same flex row, causing overlap.

**Changes to `app/templates/home.html`:**
- Removed `justify-content-end` from the row (not needed with proper columns)
- Sidebar: `col-xl-3` → `col-lg-4 col-xl-3` (stacks below lg, side-by-side above)
- Content: `col-xl-9` → `col-lg-8 col-xl-9` (matches sidebar breakpoints)
- Sidebar table: added `table-layout: fixed; width: 100%` to constrain column widths
- Folder name `<td>`: added `class="text-truncate" style="max-width: 0;"`
- Folder name `<a>`: added `class="text-truncate d-inline-block" style="max-width: 100%;"`
- Folder header `<th>`: set explicit widths (85%/15%)

Long folder names are now truncated with ellipsis instead of overflowing the grid.

---

## Work In Progress

- [x] Project scanned and documented
- [x] Fixed sidebar/content overlap in home.html
- [x] Fixed missing `return redirect(full_url)` in error paths (trash, msg_move, status)
- [ ] Write and run tests
- [ ] Fix known bugs (imap_port ignored, PASS refresh)
- [ ] Rich message viewing (HTML, attachments)
- [ ] Multi-user support
- [ ] Logging system
- [ ] Input validation and proper HTTP codes
- [ ] CC/BCC on send
- [ ] File attachments
- [ ] General refactor (clean up imap_functions.py, rename vars, add comments)
