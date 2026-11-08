# QuéVemos

QuéVemos is a web app that helps a small group of people decide what to watch together.

Every user keeps a personal library of movies and series, marking each title as seen, pending or dropped. When a group wants to watch something, one person creates a room and shares a short code. The others join with that code. Inside the room the app compares the libraries of all members and suggests titles the group wants to see. Members can also propose titles by hand. Then everybody votes, and the host closes the room choosing the winner.

The interface is in Spanish because the app is made for my own group of friends. The code and this document are in English.

## Distinctiveness and complexity

### Distinctiveness

QuéVemos is not a social network and not an e-commerce site. There is no feed, no posts, no followers and no public profiles. Users only meet inside a room, and a room exists to make one decision and then close.

None of the course projects takes data from several users and combines it to produce something new. That is the core of this app. The personal library is only the input. The output is a shared decision.

### Complexity

The most complex part is the suggestion feature. The server counts, for every title, how many room members have it as pending. This is done in one query with an annotation and a filtered count. Then it removes titles that any member has already seen, unless the room allows them. This step uses a subquery with the seen title ids, because a normal exclude over a many relation can give wrong results. The best five titles become candidates, each one with a score and a short reason like "Lo tenéis pendiente todos". If nothing can be suggested, the app explains the real cause.

Votes are not stored as totals. They are calculated with annotations every time the list loads, and the same query uses Exists subqueries to know how the current user voted. Pressing a new option changes the vote and pressing the same one again removes it. The current leader is preselected when the host closes the room.

Rooms have their own permission rules. Only members can see a room or call its endpoints, only the host can close it and the host cannot leave it. All of this is checked on the server. Unique constraints in the database stop duplicated entries, memberships, candidates and votes.

The library and the room are dynamic screens. The server renders small HTML fragments and JavaScript replaces them without reloading the page. Clicks are handled with event delegation because these parts change all the time. The app is fully responsive.

## Files

**config/** Project settings and main urls.

**core/** The welcome page for users who are not logged in.

**accounts/** Register, login and logout views and templates. It uses the default Django user model.

**catalog/** `Genre` and `Title` models. Titles are shared by all users, which is what makes it possible to compare libraries. Includes `fixtures/catalog.json` with 13 genres and 50 titles.

**library/** The `Entry` model (user, title, status, rating, comment). Views, templates and `library.js` for searching, filtering, paginating, adding, editing and deleting entries. Includes `fixtures/demo_users.json` and `fixtures/demo_entries.json` with three demo users and their libraries.

**rooms/** The `Room`, `Membership`, `Candidate` and `Vote` models. Views for listing, creating, joining and leaving rooms, and for proposing, suggesting, voting and closing. Templates for the room list, the room detail, the candidate list and the candidate card. `rooms.js` handles the room list and `room_detail.js` handles the room page.

**templates/base.html** Base layout with the navigation bar and toast messages.

**static/css/main.css** Custom styles and the Bootstrap color variables.

**static/js/common.js** Shared functions: `apiFetch` and `apiFetchText` to call the server with the CSRF token, `showToast` and `debounce`.

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

There are three demo users: `marta`, `luis` and `ana`. The password for all of them is `quevemos2026`.

To test the group features, use two browsers or a private window. Create a room with marta, join it with luis using the code and press "Sugerir títulos". The app should suggest Andor, Perfect Days, Shogun and Anatomía de una caída, because the three users have them as pending. Dune: Parte Dos should not appear because one of them already saw it.

## Additional information

- The room does not update by itself. Other members votes appear after your next action or a page refresh.
- Titles are added from the catalog. A future version would search them with the TMDb API.
- Dropped titles are not used by the suggestions yet.