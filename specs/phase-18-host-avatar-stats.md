# Phase 18: Host avatar and stats

## Goal

The host gets a face and a sense of what they have done. Players pick from 24
avatars when they join, but the host shows only as an initial. The profile page
says nothing about the games a host has run.

## Avatar

The profile page gets an **Avatar** card under the header card: the initial
first, then the active avatar pack as a grid. A click saves at once, as the
player picker does, with no Save button. The current choice carries the mint
ring the join picker uses.

The pick is stored as the avatar's URL in `User.user_image`, through
`frappe.client.set_value` on the host's own User, as the name already is. No new
field: `user_image` is what Desk shows too, so a photo uploaded in Desk shows
here, and an avatar picked here shows in Desk. Picking the initial clears it.

`user_image` comes with the page boot. The bar avatar, the menu and the header
card show the image when there is one and the initial when there is not.

## Stats

The header card shows three numbers:

- **Games hosted**: the host's `TT Session` rows with status Ended. A lobby
  closed before the start is Cancelled and does not count.
- **Players reached**: participants in those sessions, kicked players left out.
- **Quizzes written**: `TT Quiz` rows the host owns.

They come from one call, `trivia_tap.api.get_host_stats()`. It counts for
`frappe.session.user` only and takes no argument, so there is nothing to scope.

## Tracer bullet

1. `get_host_stats` with tests. **Feedback: counts only Ended sessions, leaves
   out kicked players, and another host's games count for nobody else.**
2. Stats on the header card. **Feedback: a host with games sees real numbers,
   a new host sees zeros.**
3. Avatar card and image in the bar. **Feedback: a pick shows at once in the
   bar and survives a reload. Picking the initial brings the letter back.**

## Out of scope

Photo upload in the SPA, "Hosted by" on the lobby screen, and the History page.
