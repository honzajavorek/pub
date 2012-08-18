
# Pub

Pub is a simple automatic publisher of static pages only via GitHub and Heroku.

## Status: ACTIVE

Under active development and maintenance.

## How does it work?

1. Uses Heroku Scheduler to be launched once a day.
2. In `scripts` file it has a list of GitHub repos with scripts (scrapers, generators), coupled with GitHub Pages repos where the output of each script should go.
3. Clones both these GitHub repos in such way the pages are available for the script in `output` directory.
4. Launches `pubfile.py` in root of each script repo. Script performs changes on pages.
5. Commits changes on pages and pushes them to GitHub.

## Why Pub?

_Pub_ is short from _publish_, of course!

## Installation

It's Heroku worker app. I assume you are familiar with Heroku and GitHub.

Fork & clone this repository. Then create `.env` file similar to this:

    GITHUB_USERNAME=honzajavorek
    GITHUB_PASSWORD=...
    COMMIT_NAME="Honza Javorek"
    COMMIT_EMAIL=jan.javorek@gmail.com

Create `scripts` file so it looks similar to this:

    honzajavorek/kino   honzajavorek/honzajavorek.cz

The first repo is the one with script (`pubfile.py`). The other one has to have ready `gh-pages` branch and is treated as destination for publishing.

If you are done with this, commit your changes. Then create your Heroku app by `heroku create` and `git push heroku master`. Push config via `heroku config:push`. Be sure you have no all-time-running processes: `heroku ps:scale worker=0`. Add scheduler by `heroku addons:add scheduler:standard` and adjust it's settings on admin panel. Use `worker` as the task name.

You can test & debug by `foreman start` (locally) or `heroku run python pub.py` (remotely, Heroku stack).

## License: ISC

© 2012 Jan Javorek &lt;<a
href="mailto:jan.javorek&#64;gmail.com">jan.javorek&#64;gmail.com</a>&gt;

This work is licensed under [ISC license](https://en.wikipedia.org/wiki/ISC_license).
