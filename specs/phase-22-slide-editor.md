# Phase 22: Slide quiz editor

## Goal

The quiz editor is one long form. A host with ten questions scrolls past every
field of every question to reach the one they want, and nothing shows them what
the room will see. Edit a quiz the way a host thinks about it: one question at a
time, laid out like the screen the players get.

## Behaviour

- Three panes on a laptop:
  - Left: a rail of question cards. Each card shows its number, the question
    text, a picture thumbnail and which answer is correct. A card with missing
    text or answers is marked. Click a card to edit it.
  - Middle: the selected question as a slide. Big centred question, the picture,
    and the four answer tiles with their shapes. Click the tick on a tile to
    make it the correct answer.
  - Right: settings for the selected question: time limit, points, and the
    explanation with its picture when explanations are on. Duplicate and delete
    sit here too.
- Rail cards reorder by drag and drop, and by Alt+Up / Alt+Down on a focused
  card. Each card has duplicate and delete on hover.
- "Add question" at the bottom of the rail inserts after the selected question
  and selects it.
- The title stays editable in the editor header. Description, seconds per
  question, explanations and host controls move into a Settings dialog.
- Save checks the questions first. If one is incomplete it is selected and the
  error names it, without a round trip.
- Ctrl+S / Cmd+S saves. Leaving the editor with unsaved changes asks first,
  inside the app and on tab close.
- Below a laptop width the settings pane drops under the slide. On a phone the
  rail becomes a horizontal strip above the slide.

## Out of scope

- Autosave.
- Question types other than four-option multiple choice.
- Undo.
