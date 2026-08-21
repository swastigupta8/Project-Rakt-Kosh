# Rakt-Kosh

Rakt-Kosh (रक्तकोष — "blood repository") is a blood donation platform. Patients can
search for blood by city and blood group, browse upcoming donation drives, and submit
a request without creating an account. Blood banks and hospitals can register, manage
their own live inventory, and see nearby requests ranked by distance.

**Live:** https://raktkosh-nims.onrender.com
(demo accounts below if you want to see both sides of it)

## Screenshots

*(drop images into `docs/screenshots/` and reference them here, e.g.
`![Donor dashboard](docs/screenshots/donor-dashboard.png)` — see
`docs/screenshots/README.md` for suggested shots to grab)*

## The story behind it

I originally built this as a React + FastAPI + MySQL project, mostly to have something
finished for my resume. It worked, but it showed — there was no authentication on any
endpoint, a database password committed straight into the repo, and it never actually
got deployed anywhere. Once I had time to slow down and do it properly, I rewrote the
whole thing from scratch in Django, in a language I'm actually confident in, and tried
to fix every one of those mistakes on purpose instead of patching over them.

A few decisions I made along the way:

- Everything is one language end to end — Django with server-rendered templates, no
  separate frontend build step to maintain.
- Auth uses Django's own system instead of anything hand-rolled: a custom `User` model
  with a `role` field, `login_required` plus role-check decorators, and real sessions.
- No secrets live in the source. `SECRET_KEY`, `DEBUG`, and `DATABASE_URL` all come
  from environment variables, and `.env` is gitignored.
- Distance ranking between patients and blood banks happens in plain Python
  (`geopy.distance.geodesic`) instead of a database-specific spatial function, so it's
  easy to read top to bottom and doesn't lock the app to one database engine.

## Real data, not just demo rows

The app ships with over 2,400 real blood bank locations across India, pulled from the
National Health Portal's Blood Bank Directory (open government data via data.gov.in /
ArcGIS Hub — see `data/blood_banks.csv`). These are real names, addresses, and
coordinates, so searching near an actual city returns actual hospitals, not placeholder
text.

What I didn't fake is live stock. Blood bank profiles imported from that directory
don't have a login attached — I don't have those organizations' consent to create
accounts on their behalf — so they show up in search, but their inventory starts empty
until the real bank registers and enters stock themselves. That's the honest version of
the feature, even though it means most of the map starts at zero. The demo accounts
below exist so there's at least one bank with live stock to actually click through.

## Tech stack

Django 6.1, server-rendered templates with Bootstrap 5, PostgreSQL in production
(SQLite for local dev), `geopy` for geocoding and distance, WhiteNoise for static
files. Deployed on Render, database on Neon.

```
raktkosh/            project config (settings, urls, wsgi)
core/                 home page, base template, shared geo/constants helpers,
                      management commands (seed_demo, import_real_banks, populate_demo_content)
accounts/             custom User, DonorProfile, BloodBankProfile, auth
inventory/            BloodUnit model, add/search stock
drives/               DonationDrive model, create/search drives
blood_requests/       BloodRequest model, submit/pending requests
templates/            base.html, shared partials (navbar, messages)
static/css/           custom.css (layered on Bootstrap)
data/blood_banks.csv  real blood bank directory (see above)
```

## Try it yourself

Both use password `raktkosh123`:

- `demo_donor` ("Demo User") — a few live requests across different cities
- `demo_bank` ("Demo Blood Bank") — live stock across every blood group, plus a couple of posted drives

## Running it locally

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows; use `source .venv/bin/activate` on macOS/Linux
pip install -r requirements.txt

copy .env.example .env          # then fill in SECRET_KEY etc.

python manage.py migrate
python manage.py import_real_banks       # loads the real blood bank directory
python manage.py populate_demo_content   # creates the demo accounts above
python manage.py runserver
```

There's also `python manage.py seed_demo` if you want a wider spread of throwaway
donor/bank accounts for local testing.

## Tests

```bash
python manage.py test
```

## Deploying it (Render + Neon)

1. Create a free Postgres project on [Neon](https://neon.tech) and grab its connection
   string.
2. Create a Web Service on [Render](https://render.com) pointing at this repo:
   - Build command: `pip install -r requirements.txt`
   - Start command: `python manage.py collectstatic --noinput && python manage.py migrate --noinput && gunicorn raktkosh.wsgi`
     (the free tier has no shell access, so static collection and migrations run on
     every startup instead — both are cheap and safe to repeat. See `Procfile`.)
   - Environment variables: `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS` (your
     `.onrender.com` domain), `DATABASE_URL` (from Neon).
3. Load the real bank directory and demo accounts **once**, from your own machine,
   pointed at the production database (there's no Render shell to run them from):
   ```bash
   DATABASE_URL=<your Neon connection string> python manage.py import_real_banks
   DATABASE_URL=<your Neon connection string> python manage.py populate_demo_content
   ```
   These used to be chained into the start command so they'd run on every boot, but
   `import_real_banks` does one existence-check query per CSV row — with 2,400+ rows,
   that's 2,400+ round-trips to the database before the app can even start serving
   requests. On Render's free tier, where the service spins down after ~15 minutes of
   inactivity and has to cold-boot on the next visit, that turned every wake-up into a
   several-minute hang. The data doesn't need re-checking on every restart — Postgres
   already has it durably stored — so these only need to run again if the source CSV
   changes.
4. Visit the live URL once the first deploy finishes.

## Data attribution

The blood bank directory in `data/blood_banks.csv` is derived from India's National
Health Portal Blood Bank Directory, distributed as open government data.
