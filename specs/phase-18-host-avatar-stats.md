# Phase 18: Host avatar and stats

## Goal

The host gets a face and a sense of what they have done. Players pick from 24
avatars when they join, but the host shows only as an initial. The profile page
says nothing about the games a host has run.

## Avatar

The avatar in the profile header card is a button. Hover or focus shows a
pencil over it and a "Change profile picture" tooltip. A click opens a dialog
with one large picture between left and right arrows. The arrows, and the
arrow keys, step through the initial and the active avatar pack, wrapping at
both ends. A caption names the choice and its place, such as "Panda · 4 / 25".
Save stores it. Cancel, Escape or a click outside leaves it as it was.

A photo uploaded in Desk is not in the pack. The dialog then offers it first
as "Your photo", so Save cannot drop it by accident.

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
3. Avatar dialog and image in the bar. **Feedback: a saved pick shows at once
   in the bar and survives a reload, stepping alone saves nothing, and an
   uploaded photo is still on offer.**

## Out of scope

Photo upload in the SPA, "Hosted by" on the lobby screen, and the History page.
