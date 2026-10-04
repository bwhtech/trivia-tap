# Phase 25: Continue with Google

## Goal

A host can sign up or log in with their Google account from the SPA login
page, with one tap and no password or email code.

## Approach

Frappe already ships Google login: the `Social Login Key` doctype holds the
client ID and secret, `frappe.utils.oauth` builds the authorize URL and
`frappe.integrations.oauth2_logins.login_via_google` handles the callback. It
checks that Google verified the email, creates the user when sign ups are
allowed, links an existing user with the same email, and logs them in. This
phase reuses all of it.

```
Login page -> GET trivia_tap.auth.login_with_google?redirect_to=/host
           -> 302 to Google consent
           -> 302 to frappe login_via_google (creates or links user, logs in)
           -> 302 to /trivia-tap/host
```

## Changes

1. **`login_with_google(redirect_to)`**: guest, GET, rate limited. Redirects
   to frappe's Google authorize URL. `redirect_to` must be a path inside the
   SPA, so the link cannot send a fresh login off site. Fails when Google login
   is not set up.
2. **Boot flag `google_login`**: true when the `google` Social Login Key is
   enabled and has a client ID and secret. The button only shows then.
3. **Role**: frappe gives new social users the Portal Settings default role.
   The `brand_site` patch sets it to Quiz Host when unset, so a Google sign up
   lands as a host like an email sign up.
4. **Login page**: a "Continue with Google" button under the tabs, on the log
   in and sign up screens, not on code or reset screens.

## Setup (per site)

1. Google Cloud Console > APIs & Services > Credentials > OAuth client ID,
   type Web application.
2. Authorized redirect URI:
   `<site url>/api/method/frappe.integrations.oauth2_logins.login_via_google`.
3. Desk > Social Login Key > New > Social Login Provider: Google. Paste the
   client ID and secret, tick Enable Social Login. Leave Sign ups blank: "Allow" would let Google sign ups through even when Website Settings disables sign up.

Google refuses a plain `http` redirect URI unless the host is `localhost`, so
`http://trivia-tap.localhost:8000` fails with "doesn't comply with Google's
OAuth 2.0 policy". Locally, make the site the bench default and use
`http://localhost:8000`.

## Tracer bullet

1. Backend method, boot flag, role patch, tests. **Feedback: the method
   redirects to accounts.google.com with the right redirect_uri and state.**
2. Login page button. **Feedback: the button shows only when the key is set,
   and a real Google account lands on /trivia-tap/host as a Quiz Host.**

## Out of scope

Other providers. Unlinking Google from the profile page. One Tap / the Google
Identity Services popup.
