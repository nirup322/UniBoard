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

## Links

| Resource                | Link                                                          |
|--------------------------|----------------------------------------------------------------|
| Live app                 | https://uniboard-kcwl.onrender.com                             |
| Source code (this repo)  | https://github.com/the7prajwal/UniBoard                        |
| Screenshots / demo walkthrough | https://github.com/the7prajwal/UniBoard-Screenshots (replace with actual link) |
| Author                   | [@the7prajwal](https://github.com/the7prajwal)                 |

## License

Not yet licensed. Add a `LICENSE` file (e.g. MIT) if you want others to be able to reuse this code.
