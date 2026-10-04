# Phase 24: Join Screen Polish

## Goal

The join screen works but asks the player to do more reading than tapping:

- The PIN is one wide field. The PIN on the big screen is six digits, and the
  email code step already shows six boxes. The two should look the same.
- The chosen face is a 40px circle in a strip of 25px ones. A player cannot see
  who they will be on the big screen until they are in the lobby.
- The "More" chip wraps to its own line on a phone.
- "Join game" is live with an empty form, so the first feedback is a server
  error.

All changes are on `Join.vue`. No backend, no new dependency.

## Changes

1. **PIN boxes.** Six boxes from reka-ui's `PinInput`, styled like `CodeStep`.
   Paste of a full PIN fills every box. A PIN from the QR link is pre-filled.
   Finishing the PIN moves focus to the nickname.
2. **Player card.** The chosen face shows at 56px beside the nickname input, so
   face and name read as one identity.
3. **Suggestions on one line.** "More" becomes an icon button with an
   `aria-label`.
4. **Bigger faces.** The carousel faces grow and the strip edges fade out
   instead of being cut off.
5. **Ready state.** "Join game" stays disabled until the PIN has six digits and
   the nickname is not blank.

## Non-goals

- No change to the carousel's centre-snap selection.
- No PIN validation round trip before submit.
