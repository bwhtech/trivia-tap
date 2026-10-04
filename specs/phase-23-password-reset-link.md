# Phase 23: Reset password with an email link

## Goal

A host on the profile page who forgot their current password cannot change it.
Let them ask for a reset link by email, open it, and set a new password on a
TriviaTap page, not on Frappe's `/update-password` page.

## Flow

```
Profile: Change -> "Forgot?" next to Current password -> send_reset_link()
         -> mail to the host's own inbox with /trivia-tap/reset-password?key=...
Link:    new password + confirm -> reset_password_with_link(key, new_password)
         -> logged in, reload to /trivia-tap/host
```

## `send_reset_link()`

Logged-in, POST, rate limited. Takes no email: it mails the caller's own
address, so it cannot be pointed at someone else's inbox. It mints the key with
Frappe's `User._reset_password`, so the key, its hash on the User and its
expiry (System Settings `reset_password_link_expiry_duration`) are Frappe's.
Administrator is refused, as in Frappe's own reset.

The mail uses the TriviaTap auth wrapper and names how long the link works.

## `reset_password_with_link(key, new_password)`

Guest, POST, rate limited per IP. Hands the key to Frappe's `update_password`,
which owns the password policy, reuse check, session log out and login. Frappe
answers a used, unknown or expired key with a 410 and a message instead of an
error, so this turns that into a `ValidationError` with the same message.

## Reset page

`/trivia-tap/reset-password` is open to guests and logged-in users, since the
link may open in another browser. It looks like the login page: new password,
confirm, one button. A missing key says the link is broken and points to log
in. On success it reloads to `/trivia-tap/host`.

## Tracer bullet

1. `send_reset_link`, `reset_password_with_link`, mail template, tests.
   **Feedback: tests pass; a link mailed to Mailpit carries a key that resets.**
2. Profile "Forgot?" and the reset page. **Feedback: in the browser, a host
   asks for a link, opens it from Mailpit, sets a password and lands on /host.**

## Out of scope

A link from the login page's "Forgot?", which keeps its email code.
