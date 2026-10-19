# Women B.Tech CSE Government Job Hub

A static page (no server) that lists government openings for a B.Tech CSE woman (70%, no GATE) and checks age and percentage from her own details.

## Publish (once)
1. Create a new empty GitHub repository, then upload everything in this folder (or `git init`, `git add .`, `git commit`, `git remote add origin <url>`, `git push -u origin main`).
2. Repo Settings, then Pages, then Source: **GitHub Actions**.
3. After the first run, the page is at `https://<username>.github.io/<repo>/`.

## Update openings (every week)
Edit only `data/jobs.json`. Commit the change and the site redeploys in about a minute. No code change is needed.
Each job has: `org`, `post`, `last` (YYYY-MM-DD), `qual`, `type`, `url`, plus optional `ageMax` (number, from the notice), `minPercent` (number) and `note`.
Fill `ageMax` after reading the notice and the page will show Fits / Over age automatically. Expired jobs hide on their own.
Run `python3 scripts/validate.py` before committing to catch mistakes.

## Change the profile
Change defaults in the page (DOB, category, percentage); they are saved in the visitor's browser only.

## Note
Open it through GitHub Pages or `python3 -m http.server`; opening index.html directly from disk blocks loading the JSON file.
