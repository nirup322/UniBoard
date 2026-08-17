# UniBoard

A full-stack University Student Information and Academic Dashboard — built to let students check attendance and results, and give admins a simple console to manage both.

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

## Documentation

| Doc                                   | Covers                                                        |
|-----------------------------------------|------------------------------------------------------------------|
| [ARCHITECTURE.md](./ARCHITECTURE.md)   | Tech stack, project structure, database schema, architecture diagram |
| [DEPLOYMENT.md](./DEPLOYMENT.md)       | Local setup and Render deployment                              |

## Links

| Resource                       | Link                                                                          |
|----------------------------------|-----------------------------------------------------------------------------|
| Live app                         | https://uniboard-kcwl.onrender.com                                          |
| Source code                      | https://github.com/the7prajwal/UniBoard                                     |
| Screenshots / demo walkthrough   | https://github.com/the7prajwal/UniBoard/tree/main/Screenshots               |
| Author                           | [@the7prajwal](https://github.com/the7prajwal)                              |

## License

Licensed under the [MIT License](./LICENSE).
