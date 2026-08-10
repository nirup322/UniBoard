# Deployment

## Local Setup

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

---

## Render Deployment

UniBoard runs on **Render** as the app host, with **Aiven** providing managed MySQL, and **Gunicorn** as the production WSGI server.

### 1. Database — Aiven MySQL

- Create a MySQL service on Aiven.
- Download the service's CA certificate and save it as `ca.pem` in the project root (already present in this repo).
- Note the host, port, user, password, and database name from the Aiven console.

### 2. App service — Render

- Create a new **Web Service** on Render, connected to this GitHub repo.
- Render will detect the [`Procfile`](./Procfile):

  ```
  web: gunicorn app:app
  ```

- Under the service's **Environment** tab, set the same variables used locally:

  ```
  DB_HOST
  DB_PORT
  DB_USER
  DB_PASSWORD
  DB_NAME
  DB_SSL_CA=ca.pem
  FLASK_SECRET_KEY
  ADMIN_USERNAME
  ADMIN_PASSWORD
  ```

  Do **not** rely on the local `.env` file in production — it isn't deployed (see `.gitignore`).

### 3. Deploy

- Push to the connected branch (`main`); Render builds and deploys automatically.
- Once live, run `init_aiven_schema.py` and `seed_data_mysql.py` locally (pointed at the Aiven credentials) to provision and seed the production database.

### Debugging deployment issues

A useful pattern for tracing environment-variable problems on Render: add a temporary diagnostic route (e.g. `/debug-env`) that prints which expected env vars are present/missing, then remove it once the issue is resolved — don't leave debug routes in the deployed app long-term.
