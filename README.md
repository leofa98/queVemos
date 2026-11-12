# QuéVemos

QuéVemos ("what do we watch?") is a web app that helps a group of friends decide what movie or series to watch together.

Each user keeps a personal library of titles and marks each one as pending, seen (with a rating from 1 to 10) or dropped. When the group wants to watch something, one user creates a room and shares a six character code, and the others join with it. In the room, the app compares the libraries of all the members and suggests the titles that most of them want to see. Members can also propose titles by hand. Then everybody votes, and the host closes the room and chooses the winner.

The interface is in Spanish because the app is made for my own group of friends. The code and this document are in English.

## Distinctiveness and Complexity

### Distinctiveness

QuéVemos is a tool for making a group decision. Each user manages only their own library, and nobody can see the library of another user. When several users join a room, the app combines their libraries and creates a result that none of them wrote: a list of titles that fit the whole group, each with a reason. Using data from several users to calculate something shared is the core of the project.

The room works as a process with a start and an end. A host creates it, members join, candidates are added, people vote and finally the host closes it with a winner. After that the room is read only and shows what the group decided.

The library is the input of that process. The status of each title changes what the app suggests. For example, a title that one member has already seen is not suggested to a room where that member is present, unless the room was created to allow seen titles.

This makes the project different from the course projects. In those projects, what a user creates (a wiki page, a listing, an email, a post) is shown to other users as it is. In QuéVemos the data of each user is private and is only used to calculate a group result. There is no feed, no public profiles, no followers and nothing to buy or sell.

### Complexity

The main challenge is the suggestion feature. When a member presses "Sugerir títulos", the server:

1. Gets the ids of all the members of the room.
2. Annotates every title with the number of members that have it as pending, using `Count` with a `filter=Q(...)` condition. This is one query, and each title appears only once.
3. If the room does not allow seen titles, gets the ids of the titles that any member has seen and removes them with `exclude(pk__in=...)`. A direct `exclude` across a many relation can match conditions from different rows and give wrong results, so I used a list of ids instead.
4. Orders the titles by that number and keeps the first five.
5. Creates a candidate for each one with `get_or_create`, so titles that are already in the room are not duplicated. Each candidate saves a score and a reason, for example "Lo tenéis pendiente todos" ("all of you have it pending").

If nothing can be suggested, the server returns a 409 status with a message that explains why: nobody has pending titles, all pending titles were already seen by someone, or all possible suggestions are already in the room.

Votes are not stored as totals. Every time the candidate list is loaded, the votes up and down are counted with annotations, and a second annotation with `F` expressions calculates the difference. The same query uses `Exists` and `OuterRef` to know how the current user voted on each candidate, so the page shows the pressed button without extra queries. Each user has one vote per candidate. Pressing a different option changes the vote and pressing the same option again removes it. The candidate with the best result is marked as favourite and is preselected when the host closes the room. Closing the room saves the status, the winner and the date inside a transaction.

Rooms have permission rules that are checked on the server. Only members can see a room and use it, only the host can close it, the host cannot leave it, and nobody can join a closed room. When the host closes the room, the server also checks that the chosen candidate belongs to that room. The database also has unique constraints, so a user cannot add the same title twice to their library, join a room twice or vote twice for the same candidate, and a room cannot have the same title twice.

On the front end, the library, the room list and the room work without reloading the page. In the library the user can search, filter by status, change page and add, edit or delete titles. In the room list the user can filter open and closed rooms, change page and create rooms. In the room, members can propose, get suggestions and vote. In all cases the server renders small HTML fragments with the same templates used on the first load, and JavaScript replaces them in the page. Because these fragments change all the time, clicks are handled with event delegation on a parent element.

The app is mobile responsive. Some cards change their layout on small screens so the buttons are easy to press.

## Files

These are the files that contain my code.

### config/

- `settings.py`: project settings. I added the five apps, the project `templates` and `static` folders, and set the language to Spanish.
- `urls.py`: includes the URLs of each app.

### core/

- `views.py`: `index` shows the welcome page to visitors and sends logged in users to their library.
- `urls.py`: URL of the welcome page.
- `templates/core/index.html`: the welcome page, with the three steps of how the app works and buttons to register and log in.
- `templates/core/pagination.html`: pagination component included in the library and in the room list.

### accounts/

Uses the default Django user model.

- `views.py`: `auth_register` checks that both passwords match, creates the user and logs them in. `auth_login` and `auth_logout` log the user in and out. If something is wrong, the form is shown again with an error message.
- `urls.py`: URLs for these three views.
- `templates/accounts/register.html` and `templates/accounts/login.html`: the register and login forms, with an image on the side.
- `fixtures/demo_users.json`: three demo users.

### catalog/

- `models.py`: `Genre` and `Title`. A title has a name, a type (movie or series), a year, a synopsis, an image URL and genres. Titles are shared by all users, which is what makes it possible to compare libraries.
- `fixtures/catalog.json`: 13 genres and 50 titles.

### library/

- `models.py`: `Entry`, which links a user with a title. It has the status, an optional rating and comment, and the creation and update dates.
- `views.py`:
  - `entry_list` returns the user's entries as an HTML fragment, filtered by the search text, the status and the page.
  - `entry_new`, `entry_edit` and `remove_entry` add, edit and delete an entry. They validate the title, the status and the rating, and return a JSON message.
  - `entry_detail` returns the data of one entry as JSON to fill the edit form.
- `urls.py`: URLs of the library.
- `templates/library/dashboard.html`: the library page, with the search box, the status filters, the button to add a title, and the modals to add, edit and delete.
- `templates/library/entry_list.html`: fragment with the list of entries and the pagination.
- `templates/library/entry_card.html`: one entry, with its status, rating, comment and buttons to edit and delete.
- `static/library/library.js`: logic of the library page. It handles the search, the filters, the pagination and the three modals, and reloads the list after each change.
- `fixtures/demo_entries.json`: libraries of the demo users. They overlap on purpose, so the suggestions always have something to show.

### rooms/

- `models.py`: `Room` (name, host, status, code, option to allow seen titles, winner and dates), `Membership` (a user in a room), `Candidate` (a title in a room, with who proposed it, its origin, score and reason) and `Vote` (a user's vote on a candidate, up or down).
- `views.py`:
  - `dashboard` renders the library page (`library/dashboard.html`) with the first page of the user's entries. It is the first page a user sees after logging in.
  - `rooms` renders the rooms page and `room_list` returns the list of rooms as an HTML fragment. Both use `get_user_rooms`, which gets the user's rooms filtered by status and paginated.
  - `room_new` creates a room with a random unique code and adds the host as a member.
  - `room_join` cleans the code typed by the user, checks that the room exists and is open, adds the user as a member and returns the URL of the room.
  - `room_detail` renders the room page with the candidates and their votes, the favourite and, if the room is closed, the winner. Users who are not members are sent back to their rooms.
  - `room_exit` lets a member leave the room.
  - `candidate_list` returns the candidates as an HTML fragment.
  - `propose_title`, `suggest_candidates`, `vote` and `close_room` do what their names say, as described above.
- `urls.py`: URLs of the rooms.
- `templates/rooms/list.html`: rooms page, with the field to join with a code, the filters for open and closed rooms, and the modal to create a room with its name and the option to allow seen titles.
- `templates/rooms/room_list.html`: fragment with the list of rooms and the pagination.
- `templates/rooms/room_card.html`: one room in the list. Open rooms show the number of members and candidates. Closed rooms show the winner and the closing date.
- `templates/rooms/detail.html`: room page, with the winner if the room is closed, the code, the members, the buttons to suggest and propose, and their modals.
- `templates/rooms/candidate_list.html`: fragment with the candidates and, for the host, the button and modal to close the room.
- `templates/rooms/candidate_card.html`: one candidate, with its origin, reason, badges and vote buttons.
- `static/rooms/rooms.js`: logic of the rooms page. It filters and paginates the list, creates rooms and joins a room with a code.
- `static/rooms/room_detail.js`: logic of the room page. It copies the code, proposes, suggests, votes, leaves and closes the room, and reloads the candidate list after each action.

### Project level

- `templates/base.html`: base layout with the navigation bar, the favicon, the toast messages and the CSRF token for JavaScript.
- `static/css/main.css`: custom styles and the Bootstrap variables changed to use the app colors.
- `static/js/common.js`: shared functions. `apiFetch` and `apiFetchText` send requests with the CSRF token and show the server error if something fails, `showToast` shows messages and `debounce` waits until the user stops typing or clicking before reloading a list.
- `static/img/`: the favicon and the background images of the welcome, login and register pages.

## How to run

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata catalog.json demo_users.json demo_entries.json
python manage.py runserver
```

On Linux or macOS activate the environment with `source .venv/bin/activate`.

There are three demo users: `marta`, `luis` and `ana`. The password is `quevemos2026` for all of them.

To test the rooms, use a different browser or a private window for each user:

1. Log in as marta, create a room and copy the code.
2. Log in as luis and ana and join the room with the code.
3. Press "Sugerir títulos". The app should suggest Andor, Perfect Days, Shogun and Anatomía de una caída, because the three users have them as pending. Dune: Parte Dos should not appear, because one of them has already seen it.
4. Vote with each user and close the room as marta.

## Additional information

- The only Python package needed is Django. Bootstrap, Bootstrap Icons and the Manrope font are loaded from a CDN.
- The room does not update by itself. Votes from other members appear after your next action or when you refresh the page.
- Titles come from a fixed catalog. Searching them with the TMDb API is the next step.
- Dropped titles are not used by the suggestions yet.