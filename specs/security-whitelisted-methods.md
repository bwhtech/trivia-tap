# Security: whitelisted method audit fixes

## Goal

An audit of every whitelisted method found that the methods themselves check
the caller, but two paths around them do not. Close both, plus two small gaps.

## Findings and fixes

### 1. A host can write TT Session through the REST API (high)

Quiz Host had create and write on TT Session (`if_owner`), and the controller
has no validation. `POST /api/resource/TT Session` skipped every check in
`create_session`, so one host could:

- start a game on another host's quiz and read its questions and correct
  answers through `get_host_state`;
- create a session with `host` set to someone else, which then opens on that
  host's screen;
- pick the game PIN and set `status` directly.

Fix: Quiz Host keeps `if_owner` read on TT Session and loses create, write and
delete. The whitelisted methods become the only write path and save with
`ignore_permissions`, since `get_host_session` already checks the caller is the
host and `create_session` checks quiz read access.

### 2. Guests can scan for live game PINs (medium)

`get_state`, `get_result` and `submit_answer` were rate limited per IP plus
`token`. The caller picks the token, so a new token per request removed the
limit. A wrong PIN also raised `DoesNotExistError` while a live PIN with a bad
token raised `PermissionError`, so the response told the caller which PINs are
live.

Fix: rate limit these per IP only, and raise the same `PermissionError` for a
bad PIN and a bad token on the token-gated methods. `join_session` still says
"Invalid game PIN", since a player needs to know they typed it wrong, and it
keeps its 10 per minute per IP limit.

### 3. Player token in GET URLs (low)

`get_state` and `get_result` accepted GET, so the player token could land in
URLs and access logs. The SPA always POSTs. Fix: POST only.

### 4. Code login skips two-factor auth (low)

`login_with_code` used `login_as`, which skips Frappe's 2FA. Fix: refuse code
login for users who must pass 2FA, and point them to password login.

## Non-goals

- Realtime rooms stay joinable with just a PIN. Players are guests by design,
  and no event carries `correct_option` before the question closes.
- `sign_up` logs a brand new user in right after an email code. A site that
  forces 2FA on Quiz Host is not a setup TriviaTap supports today.

## Tests

- A host cannot create or edit a TT Session through the document API.
- Host control methods still work for the host.
- A token-gated guest method gives the same error for a wrong PIN as for a
  wrong token.
- Code login is refused when 2FA applies to the user.
