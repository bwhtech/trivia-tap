# Phase 21: One quiz list

## Goal

A first-time host sees two tabs, Play and Library, that both list the same
quizzes. That is confusing. Merge them into one list on `/host`.

## Behaviour

- `/host` shows "Your quizzes": one row per quiz with its title and question
  count.
- Clicking a row opens the quiz editor.
- Each row has a Play button on the right. It starts a session for that quiz,
  the same as clicking a quiz on the old Play tab.
- Each row keeps a quiet delete button. A played quiz still cannot be deleted.
- The Play and Library tabs are gone from the host bar. The logo still leads
  to `/host`.
- `/host/quizzes` redirects to `/host`, so old links keep working. The editor
  stays at `/host/quizzes/:name`.

## Out of scope

- Search, sorting or folders for the list.
