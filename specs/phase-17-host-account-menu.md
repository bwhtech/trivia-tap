# Phase 17: Host account menu

## Goal

The host bar reads as navigation, and account things live in one place.

Today the nav links wear the same bordered pill as Edit and Delete, so the bar
reads as a row of buttons. "Hi, Administrator" truncates on a phone. The theme
button floats over page content, and on the phone profile page it covers
Change password. Log out sits on the profile page, half way down the header.

Kahoot, Wayground and Mentimeter all put an avatar in the top right corner that
opens an account menu with profile, settings and log out. This phase does the
same.

## Host bar

Left to right:

- Logo, links to `/host`. The wordmark hides on a phone, as now.
- **Play** (`/host`) and **Library** (`/host/quizzes`, and the editor under it).
  Plain text tabs: muted text, the current one in `paper` with a mint underline.
  "Host" named the role, not the page.
- **New quiz** on the right, the `ctl-go` link to `/host/quizzes/new` that used
  to sit on the quiz list. On a phone it shrinks to a plus icon with an
  `aria-label`.
- **Avatar**: a round button with the host's first initial on the brand
  gradient. It opens the account menu.

The bar still hides while a game is live.

## Account menu

A native `popover` element. It gives light dismiss, Escape to close, focus
return and `aria-expanded` on the button with no script. It sits fixed under
the right end of the bar, so it needs no anchor positioning.

frappe-ui's `Dropdown` is not used: it paints frappe-ui's own surfaces, which do
not follow this app's mint and ink tokens or the `auto` theme.

Contents:

- First name and email (`session_user`).
- **Profile**, links to `/host/profile`.
- **Theme**: Auto, Light and Dark as a three way choice that sets `theme`
  directly. The floating theme button goes from host screens. Join, Log in,
  Play and the live host controls keep `ThemeButton`.
- **Log out**, the same call the profile page made.

## Profile page

- A header card replaces the "Host" eyebrow and the stray Log out button: the
  avatar, full name and email.
- **Save name** stays disabled until the name differs from what was loaded or
  last saved.
- The Name and Password cards stay as they are.

The "Host" eyebrow also goes from the quiz picker and the quiz list. The bar
now says where you are.

## Tracer bullet

1. Bar with tabs, New quiz and the avatar menu, theme button gone.
   **Feedback: on desktop and a 390px phone the bar fits one row, the menu
   opens, switches theme, links to profile and logs out.**
2. Profile header card and dirty Save name.
   **Feedback: Save name is disabled on load, enabled after an edit, disabled
   again after saving.**

## Tests

Frontend only, no backend change. Verified in the browser with
`/agent-browser`, both themes, desktop and phone.

## Out of scope

Host avatar picker, host stats and the History tab.
