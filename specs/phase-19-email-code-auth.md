# Phase 19: Email codes for sign up, reset and log in

## Goal

Every account belongs to an inbox its owner can read. Sign up proves the email
with a 6-digit code before the account exists. A host who forgets the password
resets it with a code, inside the SPA. A host can also log in with a code
instead of a password. Mail goes out through the site's default outgoing Email
Account (TriviaTap, Mailpit in dev).

## Flows

```
Sign up:  name + email + password + confirm -> send_code(email, "sign_up")
          code -> sign_up(name, email, password, code) -> logged in, reload
Forgot:   email -> send_code(email, "reset_password")
          code + new password + confirm -> reset_password(email, code, password) -> logged in, reload
Code log in: email -> send_code(email, "log_in")
          code -> login_with_code(email, code) -> logged in, reload
Log in:   email + password -> frappe /api/method/login (unchanged)
```

The code screen names the address, takes the code with
`autocomplete="one-time-code"`, offers "Send a new code" after 30 seconds, and
has a back link to fix the email.

## The code

- 6 random digits from `secrets`, valid for 10 minutes.
- Stored in `frappe.cache` under `tt:code:{purpose}:{email}` as a SHA-256 hash,
  never the digits.
- 5 wrong tries delete it. The user asks for a new one.
- A new code replaces the old one. A resend within 30 seconds is refused, so a
  script cannot flood an inbox from many IPs.
- The code is used up only when the action it guards succeeds. A sign up that
  fails the password policy keeps the code, so the host fixes the password and
  tries again.

## `send_code(email, purpose)`

Guest, POST, rate limited per IP. It answers the same way whether or not the
email has an account, so the form cannot probe for accounts:

- sign_up: refused when sign up is disabled. An email that has an account gets
  a mail that says so and points to log in, not a code.
- reset_password, log_in: mails a code only to an enabled user who is not
  Administrator. Any other email gets nothing.

The mail goes out from a background job in every case, so the response time
does not tell either.

Sign up checks the password with frappe's `test_password_strength` before it
asks for a code, so a weak password fails before the host opens their inbox.

## Actions

- `sign_up(full_name, email, password, code)`: as phase 14, plus the code check.
- `reset_password(email, code, new_password)`: checks the code, then mints a
  frappe reset key and hands it to frappe's own `update_password`. Frappe's
  password policy, reuse check, session log out setting and login all apply.
- `login_with_code(email, code)`: checks the code and logs the user in.

All three are guest, POST and rate limited per IP.

## Branding

Frappe signs its mails with Website Settings `app_name` and `app_logo`, which
said "Frappe". The `brand_site` patch (also run after install) sets them to
TriviaTap and its logo when they are unset or still "Frappe".

## Tracer bullet

1. Code store, `send_code`, the three actions, tests. **Feedback: a code mailed
   to Mailpit signs up, resets and logs in from a guest session.**
2. Login page: code step for sign up, forgot and code log in. **Feedback: each
   flow runs end to end in the browser with the code read from Mailpit.**

## Out of scope

A welcome mail after sign up. Codes for changing the email of an account.
