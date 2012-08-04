# Pub

Pub is a simple automatic publisher of static pages only via GitHub and Heroku:

1. Uses Heroku Scheduler to be launched once a day.
2. In `scripts` file it has a list of GitHub repos with scripts (scrapers, generators), coupled with GitHub Pages repos where the output of each script should go.
3. Clones both these GitHub repos in such way the pages are available for the script in `output` directory.
4. Launches `pubfile.py` in root of each script repo. Script performs changes on pages.
5. Commits changes on pages and pushes them to GitHub.

## Installation

Fork & clone this repository. Then create `.env` file similar to this:

    GITHUB_USERNAME=honzajavorek
    GITHUB_PASSWORD=...
    COMMIT_NAME=Honza Javorek
    COMMIT_EMAIL=jan.javorek@gmail.com

Create `scripts` file so it looks similar to this:

    honzajavorek/kino   honzajavorek/blog

The first repo is the one with script (`pubfile.py`). The other one has to have ready `gh-pages` branch and is treated as destination for publishing.

If you are done with this, commit your changes.