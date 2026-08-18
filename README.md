# Rakt-Kosh

Rakt-Kosh (रक्तकोष — "blood repository") connects patients with nearby blood banks'
live stock and donation drives, and gives blood banks a simple way to keep that
stock current.

- **Patients / donors** can search for blood by city and blood group, browse
  upcoming donation drives near them, and submit a blood request — no account
  required.
- **Blood banks / hospitals** can register, manage their live blood inventory,
  post donation drives, and see pending requests near them, nearest first.

Built with Django, server-rendered templates, and real geolocation-based
matching — no separate JS framework, no external services beyond a database
and free geocoding.

## Why it's built this way

This is a ground-up rebuild of an earlier version of this project (originally
React + FastAPI + MySQL) that had grown out of an early, "just get something
on the resume" attempt — the previous version had no authentication on any
endpoint, a database password committed to source control, and no working
deployment. This rebuild is a straight Django app on purpose:

- **One language, top to bottom.** Django + server-rendered templates, no
  separate frontend build step.
- **Auth is Django's, not hand-rolled.** A custom `User` model with a `role`
  field, `login_required` + role-check decorators, and real sessions —
  closing the biggest gap in the earlier version.
- **No secrets in source.** `SECRET_KEY`/`DEBUG`/`DATABASE_URL` all come from
  environment variables; `.env` is gitignored, `.env.example` documents what's
  needed.
- **Distance ranking in plain Python**, not a database-specific spatial
  function — `geopy` geocodes a place name once, `geopy.distance.geodesic`
  ranks results. Easy to read top to bottom, portable across databases.

## Real data, honestly

The app ships pre-loaded with **2,400+ real blood bank locations across
India**, sourced from the National Health Portal's Blood Bank Directory (via
[data.gov.in](https://data.gov.in) / ArcGIS Hub open data — see
`data/blood_banks.csv`, imported with `manage.py import_real_banks`). These
are real facility names, addresses, and coordinates, so search results aren't
fake.

What's *not* faked: a real facility's **live stock**. `BloodBankProfile` rows
imported this way have no linked user account (`user=None`) — nobody has
consented to a login on that organization's behalf, so nobody but the actual
bank can enter stock for it. That means imported real banks show up in search
and on the map, but their inventory starts empty until a real account claims
it. A handful of demo bank accounts (`manage.py seed_demo`) exist purely so
there's something with live stock to click through locally.

## Tech stack

- **Backend / frontend**: Django 6.1, server-rendered templates, Bootstrap 5
  (CDN, no JS build step)
- **Database**: PostgreSQL in production, SQLite for local dev (switches
  automatically based on whether `DATABASE_URL` is set)
- **Geocoding & distance**: `geopy` (Nominatim/OpenStreetMap)
- **Static files**: WhiteNoise
- **Deployment target**: Render (web) + Neon (Postgres)

## Project structure

```
raktkosh/            Django project config (settings, urls, wsgi)
core/                 home page, base template, shared geo/constants helpers,
                      management commands (seed_demo, import_real_banks)
accounts/             custom User, DonorProfile, BloodBankProfile, auth
inventory/            BloodUnit model, add/search stock
drives/               DonationDrive model, create/search drives
blood_requests/       BloodRequest model, submit/pending requests
templates/            base.html, shared partials (navbar, messages)
static/css/           custom.css (layered on Bootstrap)
data/blood_banks.csv  real blood bank directory (see "Real data" above)
```

## Local setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows; use `source .venv/bin/activate` on macOS/Linux
pip install -r requirements.txt

copy .env.example .env          # then edit SECRET_KEY etc.

python manage.py migrate
python manage.py import_real_banks   # loads the real blood bank directory
python manage.py seed_demo           # optional: adds demo donors/banks/stock you can log into
python manage.py runserver
```

Demo accounts created by `seed_demo` (all use password `raktkosh123`):
`donor_asha`, `donor_rahul`, `donor_priya`, `donor_kabir` (donors) and
`bank_sunrise`, `bank_lifeline`, `bank_hope` (blood banks).

## Running tests

```bash
python manage.py test
```

## Deployment (Render + Neon)

1. **Database** — create a free Postgres project on [Neon](https://neon.tech),
   copy its connection string.
2. **Web service** — create a new Web Service on [Render](https://render.com)
   pointing at this repo:
   - Build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - Start command: `gunicorn raktkosh.wsgi`
   - Environment variables: `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS` (your
     `.onrender.com` domain), `DATABASE_URL` (from Neon).
3. Run migrations and load real data against the production database once
   (via Render's shell or a one-off job):
   ```bash
   python manage.py migrate
   python manage.py import_real_banks
   ```
4. Visit the live `.onrender.com` URL.

## License / data attribution

Blood bank directory data in `data/blood_banks.csv` is derived from India's
National Health Portal Blood Bank Directory, distributed as open government
data.
