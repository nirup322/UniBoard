# UniBoard

A full-stack University Student Information and Academic Dashboard — built to let students check attendance and results, and give admins a simple console to manage both.

**Live demo:** https://uniboard-kcwl.onrender.com
**Screenshots / walkthrough:** [UniBoard-Screenshots](https://github.com/the7prajwal/UniBoard-Screenshots) — replace with your actual repo link once created

![Python](https://img.shields.io/badge/Python-3.x-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-Aiven-4479A1?logo=mysql&logoColor=white)
![Deployed on Render](https://img.shields.io/badge/Deployed%20on-Render-46E3B7?logo=render&logoColor=white)

---

## Overview

UniBoard is a two-role academic dashboard for a university CSE department:

- **Students** log in with just their **USN and date of birth** to view their attendance (with sub-75% flagging) and semester-wise results.
- **Admins** log in with a username/password to manage students, record attendance, and add or update results — with automatic grade calculation and upsert logic so re-entering a result updates it instead of creating a duplicate.

The database is seeded with 120 synthetic CSE students (via Faker, `en_IN` locale) across 5 semesters, so the app is fully explorable out of the box.

## Features

- **Two-role authentication**
  - Student login via USN + DOB (no separate password to manage)
  - Admin login via session-based auth, with route guards on every admin page
- **Attendance tracking** — per-subject attendance with automatic percentage calculation and a visual flag when a student drops below 75%
- **Results management** — semester-wise marks and grades, with server-side grade banding (A+ down to F) and upsert-based writes (no duplicate result rows)
- **Data integrity** — subject codes are validated against the `subjects` table before a result or attendance row is written
- **Custom UI** — an "academic register" visual theme (Fraunces + IBM Plex Mono/Sans, navy/brass/maroon on pale paper, stamped grade badges) rather than a generic admin-panel look
- **Security basics** — 100% parameterized SQL queries, session-guarded admin routes, secrets loaded from environment variables (never hardcoded)

## Tech Stack

| Layer          | Technology                                   |
|----------------|-----------------------------------------------|
| Backend        | Python, Flask                                 |
| Database       | MySQL (hosted on Aiven)                       |
| Templating     | Jinja2                                        |
| Styling        | Custom CSS (no framework)                     |
| App hosting    | Render (via Gunicorn)                         |
| Synthetic data | Faker (`en_IN` locale)                        |

## Project Structure

```
UniBoard/
├── app.py                   # Flask app: all routes (student + admin)
├── db.py                    # Single source of DB connection config (env-var driven)
├── init_aiven_schema.py     # One-time script: creates schema on a fresh Aiven MySQL instance
├── seed_data_mysql.py       # Generates 120 synthetic CSE students + attendance + results
├── schema_mysql.sql         # Table definitions (students, subjects, attendance, results)
├── requirements.txt
├── Procfile                 # Render/Gunicorn start command
├── static/
│   └── style.css            # Design system (tokens, typography, layout)
└── templates/
    ├── student_login.html
    ├── student_profile.html
    ├── admin_login.html
    ├── admin_dashboard.html
    ├── admin_add_student.html
    └── admin_manage_student.html
```

## Database Schema

Four tables, related by foreign keys:

- **students** — `usn` (PK), `name`, `dob`, `semester`, `branch`
- **subjects** — `subject_code` (PK), `subject_name`, `semester`, `branch`
- **attendance** — links a student + subject to `classes_held` / `classes_attended`
- **results** — links a student + subject + semester to `marks` / `grade`

Full definitions are in [`schema_mysql.sql`](./schema_mysql.sql).

## Getting Started (Local Setup)

### 1. Clone and install dependencies

```bash
git clone https://github.com/the7prajwal/UniBoard.git
cd UniBoard
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file in the project root (this file is git-ignored — never commit it):

```env
DB_HOST=your-mysql-host
DB_PORT=3306
DB_USER=your-mysql-user
DB_PASSWORD=your-mysql-password
DB_NAME=uniboard
DB_SSL_CA=ca.pem          # only needed for a managed/cloud MySQL provider that requires SSL
FLASK_SECRET_KEY=some-random-secret-string
ADMIN_USERNAME=admin
ADMIN_PASSWORD=choose-a-strong-password
```

> **Windows note:** File Explorer's "rename" will silently save `.env` as `.env.txt`. Create it via Notepad → **Save As** → set "Save as type" to **All Files**.

### 3. Create the schema and seed data

```bash
python init_aiven_schema.py     # creates the database + tables
python seed_data_mysql.py       # inserts 120 synthetic students, attendance, and results
```

### 4. Run the app

```bash
python app.py
```

Visit `http://localhost:5000`.

- Student login: `/student/login`
- Admin login: `/admin/login`

## Deployment

Deployed on **Render**, using **Gunicorn** as the WSGI server (`Procfile`: `web: gunicorn app:app`) and **Aiven** for managed MySQL. Set the same environment variables listed above in Render's **Environment** tab — do not rely on the `.env` file in production.

## Demo Credentials

> Replace these with your own values in the deployed environment. Do not reuse the local dev defaults in production.

| Role    | Login                          |
|---------|----------------------------------|
| Student | Any seeded USN + matching DOB (see `seed_data_mysql.py` for the generation logic, or query the `students` table) |
| Admin   | Set via `ADMIN_USERNAME` / `ADMIN_PASSWORD` env vars |

## Known Limitations / Roadmap

- [ ] Admin password currently defaults to a weak value if the env var isn't set — must be overridden in production (tracked, see below)
- [ ] No automated tests yet
- [ ] No password hashing for admin credentials (single hardcoded admin account by design, no user table)
- [ ] `ca.pem` is committed to the repo for SSL — fine for a portfolio project, but in a real production setup this would be pulled from a secrets manager instead
- [ ] No pagination on the admin student list (fine at 120 rows, would need it at scale)

## Links

| Resource                | Link                                                          |
|--------------------------|----------------------------------------------------------------|
| Live app                 | https://uniboard-kcwl.onrender.com                             |
| Source code (this repo)  | https://github.com/the7prajwal/UniBoard                        |
| Screenshots / demo walkthrough | https://github.com/the7prajwal/UniBoard-Screenshots (replace with actual link) |
| Author                   | [@the7prajwal](https://github.com/the7prajwal)                 |

## License

Not yet licensed. Add a `LICENSE` file (e.g. MIT) if you want others to be able to reuse this code.
