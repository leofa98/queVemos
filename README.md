[Leer en español](README.es.md)

# QuéVemos
**Live demo:** https://quevemos.pythonanywhere.com

QuéVemos is a web app to decide what to watch as a group. It's a personal project I work on from time to time. I use it to practice.
 
Each user keeps a library with what they want to watch and what they have already seen. To choose as a group, a user creates a room and shares the code. The app compares the members' libraries, suggests titles they have pending and leaves out the ones someone has already seen. Then the members vote and the host closes the room with the winner.
 
The interface is in Spanish.

## What you can do

**Account**
- Sign up, log in and log out

**Library**
- Add movies and series and mark them as pending, seen or dropped
- Rate what you have seen from 1 to 10 and write a comment
- Search, filter by status and change page without reloading

**Rooms**
- Create a room and share the code
- Join a room with the code
- Get suggestions based on the members' libraries
- Propose titles by hand
- Vote up or down, change your vote or remove it
- Close the room and pick the winner (host only)

## How suggestions work

1. Get all the members of the room.
2. For each title, count how many members have it as pending.
3. If the room doesn't allow seen titles, remove the ones someone has already seen.
4. Order them by the number of members that have them pending and keep the first five.
5. Each suggestion saves a reason, for example "Lo tenéis pendiente todos" ("all of you have it pending").

If nothing can be suggested, the app explains why: nobody has pending titles, everything pending was already seen by someone, or all the suggestions are already in the room.

## Tech

- Django 5.2
- SQLite
- Plain JavaScript
- Bootstrap 5 and Bootstrap Icons

## What I practiced

- Splitting the project into several Django apps (`accounts`, `catalog`, `library`, `rooms` and `core`) and relating their models
- ORM queries with `annotate`, `Count` with filters, `F`, `Q`, `Exists` and `OuterRef`
- Unique constraints in the database to avoid duplicated entries, members, candidates and votes
- Checking permissions on the server: only members can see a room and only the host can close it
- Requests with `fetch` and CSRF, reloading pieces of HTML rendered by Django without reloading the page
- Event delegation for elements that are repainted again and again
- Overriding Bootstrap variables to use my own color palette
- Mobile friendly layout

## Status

It's still in development. Everything above works, but there are things left to do:

- Search titles with the TMDb API. Right now they come from a small fixed catalog.
- Make the room update by itself when others vote.
- Use dropped titles in the suggestions.
- Use genres and ratings to improve the suggestions.
- Clean up some views that got too long.
- Tests.
- Deploy it.

## Run it locally

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata catalog.json demo_users.json demo_entries.json
python manage.py runserver
```

On Linux or macOS activate the environment with `source .venv/bin/activate`.

Then open `http://127.0.0.1:8000`, create an account and start adding titles to your library.

## Demo data
You can try the live demo with the demo users below, or create your own account. The data in the demo may be reset from time to time.

The `loaddata` command loads a catalog of 50 titles and three sample users: `marta`, `luis` and `ana`, with the password `quevemos2026`. Their libraries share some titles, so you can try the rooms without creating several accounts and filling them by hand. If you only want the catalog, load just `catalog.json`.

To try a room with several users, use a different browser or a private window for each one.