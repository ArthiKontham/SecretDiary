import os
from datetime import datetime
from functools import wraps

import requests
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY",
    "secret-diary-local-key-change-me"
)

SUPABASE_URL = os.environ.get(
    "SUPABASE_URL",
    ""
).rstrip("/")

SUPABASE_KEY = (
    os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    or os.environ.get("SUPABASE_KEY", "")
)

USER_FILE = "users.txt"


def db_enabled():
    return bool(SUPABASE_URL and SUPABASE_KEY)


def db_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }


def db_request(method, table, params=None, json=None):
    if not db_enabled():
        raise RuntimeError(
            "Supabase environment variables are not configured."
        )

    response = requests.request(
        method,
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=db_headers(),
        params=params,
        json=json,
        timeout=15
    )

    if not response.ok:
        raise RuntimeError(
            f"Supabase error {response.status_code}: {response.text}"
        )

    if not response.text:
        return []

    return response.json()


def find_user(username):
    if db_enabled():
        rows = db_request(
            "GET",
            "users",
            params={
                "username": f"eq.{username}",
                "select": "id,username,password_hash"
            }
        )

        return rows[0] if rows else None

    try:
        with open(USER_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                if not line:
                    continue

                parts = line.split(",", 1)

                if len(parts) != 2:
                    continue

                saved_username, saved_password = parts

                if saved_username.strip().lower() == username.strip().lower():
                    return {
                        "id": saved_username.strip(),
                        "username": saved_username.strip(),
                        "password_hash": saved_password.strip()
                    }

    except FileNotFoundError:
        pass

    return None


def create_user(username, password):
    if db_enabled():
        db_request(
            "POST",
            "users",
            params={
                "select": "id,username"
            },
            json={
                "username": username,
                "password_hash": generate_password_hash(password)
            }
        )
        return

    with open(USER_FILE, "a", encoding="utf-8") as f:
        f.write(f"{username},{password}\n")


def current_username():
    return session.get("username")


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_username():
            return redirect(url_for("login"))

        return view(*args, **kwargs)

    return wrapped


@app.route("/")
def frontpage():
    return render_template("frontpage.html")


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/signupsuccess", methods=["POST"])
def signupsuccess():
    username = request.form.get(
        "username",
        ""
    ).strip().lower()

    password = request.form.get(
        "password",
        ""
    )

    confirm_password = request.form.get(
        "confirmPassword",
        ""
    )

    if not username or not password:
        return render_template(
            "signup.html",
            error="Please fill in all fields."
        )

    if len(password) < 6:
        return render_template(
            "signup.html",
            error="Password must be at least 6 characters."
        )

    if password != confirm_password:
        return render_template(
            "signup.html",
            error="Passwords do not match."
        )

    try:
        if find_user(username):
            return render_template(
                "signup.html",
                error="This email/username is already in use."
            )

        create_user(
            username,
            password
        )

        session["username"] = username

        return redirect(
            url_for("theme1")
        )

    except Exception as exc:
        print(f"Signup error: {repr(exc)}")

        return render_template(
            "signup.html",
            error=f"Signup error: {str(exc)}"
        )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get(
            "username",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        try:
            user = find_user(username)

            valid = False

            if user:
                stored = user.get(
                    "password_hash",
                    ""
                )

                if stored.startswith(
                    (
                        "pbkdf2:",
                        "scrypt:",
                        "argon2:"
                    )
                ):
                    valid = check_password_hash(
                        stored,
                        password
                    )
                else:
                    valid = stored == password

            if valid:
                session["username"] = user["username"]

                return redirect(
                    url_for("theme1")
                )

            return render_template(
                "login.html",
                error="Invalid username or password."
            )

        except Exception as exc:
            print(f"Login error: {exc}")

            return render_template(
                "login.html",
                error="Unable to log in right now. Please try again."
            )

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()

    return redirect(
        url_for("frontpage")
    )


@app.route("/view_accounts")
def view_accounts():
    try:
        if db_enabled():
            rows = db_request(
                "GET",
                "users",
                params={
                    "select": "username,created_at",
                    "order": "created_at.desc"
                }
            )

            accounts = [
                r.get("username")
                for r in rows
            ]

        else:
            try:
                with open(
                    USER_FILE,
                    "r",
                    encoding="utf-8"
                ) as f:
                    accounts = f.readlines()

            except FileNotFoundError:
                accounts = []

        return render_template(
            "view-accounts.html",
            accounts=accounts
        )

    except Exception as exc:
        print(f"View accounts error: {exc}")

        return render_template(
            "view-accounts.html",
            accounts=[]
        )


@app.route("/theme1")
@login_required
def theme1():
    return render_template("theme1.html")


@app.route("/year<theme>", methods=["GET", "POST"])
@login_required
def year(theme):
    theme = theme.replace(".html", "")

    return render_template(
        f"year{theme}.html"
    )


@app.route("/month<theme>", methods=["GET", "POST"])
@login_required
def month(theme):
    theme = theme.replace(".html", "")

    return render_template(
        f"month{theme}.html"
    )


@app.route("/day<theme>", methods=["GET", "POST"])
@login_required
def day(theme):
    theme = theme.replace(".html", "")

    return render_template(
        f"day{theme}.html"
    )


@app.route("/diary")
@login_required
def diary():
    selected_month = request.args.get(
        "selectedMonth",
        ""
    ).strip()

    selected_day = request.args.get(
        "selectedDay",
        ""
    ).strip()

    selected_year = request.args.get(
        "selectedYear",
        ""
    ).strip()

    selected_date = ""

    if (
        selected_year
        and selected_month
        and selected_day
    ):
        try:
            if selected_month.isdigit():
                month_number = int(selected_month)
            else:
                try:
                    month_number = datetime.strptime(
                        selected_month,
                        "%B"
                    ).month
                except ValueError:
                    month_number = datetime.strptime(
                        selected_month,
                        "%b"
                    ).month

            selected_date = datetime(
                int(selected_year),
                month_number,
                int(selected_day)
            ).strftime("%Y-%m-%d")

        except (
            ValueError,
            TypeError
        ):
            selected_date = ""

    elif selected_day.isdigit():
        try:
            today = datetime.now()

            selected_date = datetime(
                today.year,
                today.month,
                int(selected_day)
            ).strftime("%Y-%m-%d")

        except ValueError:
            selected_date = ""

    elif selected_month and selected_day:
        try:
            if selected_month.isdigit():
                month_number = int(selected_month)
            else:
                try:
                    month_number = datetime.strptime(
                        selected_month,
                        "%B"
                    ).month
                except ValueError:
                    month_number = datetime.strptime(
                        selected_month,
                        "%b"
                    ).month

            selected_date = datetime(
                datetime.now().year,
                month_number,
                int(selected_day)
            ).strftime("%Y-%m-%d")

        except (
            ValueError,
            TypeError
        ):
            selected_date = ""

    return render_template(
        "DiaryPage.html",
        selected_date=selected_date
    )


@app.route("/submit_entry", methods=["POST"])
@login_required
def submit_entry():
    entry_text = request.form.get(
        "entry",
        ""
    ).strip()

    entry_date = request.form.get(
        "entry_date",
        ""
    ).strip()

    if not entry_text:
        return render_template(
            "DiaryPage.html",
            selected_date=entry_date,
            error="Please write something before saving."
        )

    if not entry_date:
        entry_date = datetime.now().strftime(
            "%Y-%m-%d"
        )

    if entry_date.isdigit():
        try:
            today = datetime.now()

            entry_date = datetime(
                today.year,
                today.month,
                int(entry_date)
            ).strftime("%Y-%m-%d")

        except ValueError:
            entry_date = datetime.now().strftime(
                "%Y-%m-%d"
            )

    try:
        if not db_enabled():
            return render_template(
                "DiaryPage.html",
                selected_date=entry_date,
                error="Supabase is not configured."
            )

        db_request(
        "POST",
        "diary_entries",
         json={
        "username": current_username(),
         "entry": entry_text,
         "entry_date": entry_date,
         "entry_text": entry_text
        }
        )

        return render_template(
            "DiaryPage.html",
            selected_date=entry_date,
            message="Diary entry saved successfully!"
        )

    except Exception as exc:
        print(
            f"Save entry error: {repr(exc)}"
        )

        return render_template(
            "DiaryPage.html",
            selected_date=entry_date,
            error=f"Unable to save the diary entry: {str(exc)}"
        )


@app.route("/previousentries")
@login_required
def previous_entries():
    try:
        if db_enabled():
            entries = db_request(
                "GET",
                "diary_entries",
                params={
                    "username": f"eq.{current_username()}",
                    "select": "entry_date,entry_text,created_at",
                    "order": "created_at.desc"
                }
            )

        else:
            entries = []

            try:
                with open(
                    "diaryEntries.txt",
                    "r",
                    encoding="utf-8"
                ) as f:
                    for line in f:
                        entries.append(
                            {
                                "entry_date": "",
                                "entry_text": line.strip()
                            }
                        )

            except FileNotFoundError:
                pass

        return render_template(
            "view_entries.html",
            entries=entries
        )

    except Exception as exc:
        print(
            f"View entries error: {exc}"
        )

        return render_template(
            "view_entries.html",
            entries=[]
        )


@app.route("/save_reminder", methods=["POST"])
@login_required
def save_reminder():
    reminder_date = request.form.get(
        "reminder_date",
        ""
    ).strip()

    reminder_time = request.form.get(
        "reminder_time",
        ""
    ).strip()

    if (
        not reminder_date
        or not reminder_time
    ):
        return redirect(
            url_for("diary")
        )

    try:
        if db_enabled():
            db_request(
                "POST",
                "reminders",
                json={
                    "username": current_username(),
                    "reminder_date": reminder_date,
                    "reminder_time": reminder_time
                }
            )

        else:
            with open(
                "reminders.txt",
                "a",
                encoding="utf-8"
            ) as f:
                f.write(
                    f"{reminder_date} {reminder_time}\n"
                )

        return render_template(
            "DiaryPage.html",
            selected_date=reminder_date,
            message=(
                f"Reminder saved for "
                f"{reminder_date} at "
                f"{reminder_time}!"
            )
        )

    except Exception as exc:
        print(
            f"Save reminder error: {repr(exc)}"
        )

        return render_template(
            "DiaryPage.html",
            selected_date=reminder_date,
            error=f"Unable to save the reminder: {str(exc)}"
        )


@app.route("/reminders")
@login_required
def reminders():
    try:
        if db_enabled():
            reminder_rows = db_request(
                "GET",
                "reminders",
                params={
                    "username": f"eq.{current_username()}",
                    "select": (
                        "reminder_date,"
                        "reminder_time,"
                        "created_at"
                    ),
                    "order": (
                        "reminder_date.asc,"
                        "reminder_time.asc"
                    )
                }
            )

        else:
            reminder_rows = []

            try:
                with open(
                    "reminders.txt",
                    "r",
                    encoding="utf-8"
                ) as f:
                    for line in f:
                        parts = line.strip().split(
                            " ",
                            1
                        )

                        if len(parts) == 2:
                            reminder_rows.append(
                                {
                                    "reminder_date": parts[0],
                                    "reminder_time": parts[1]
                                }
                            )

            except FileNotFoundError:
                pass

        return render_template(
            "view_reminders.html",
            reminders=reminder_rows
        )

    except Exception as exc:
        print(
            f"View reminders error: {exc}"
        )

        return render_template(
            "view_reminders.html",
            reminders=[]
        )


@app.route("/save_calculation", methods=["POST"])
@login_required
def save_calculation():
    expression = request.form.get(
        "expression",
        ""
    ).strip()

    result = request.form.get(
        "result",
        ""
    ).strip()

    if expression and result:
        try:
            if db_enabled():
                db_request(
                    "POST",
                    "calculations",
                    json={
                        "username": current_username(),
                        "expression": expression,
                        "result": result
                    }
                )

            else:
                with open(
                    "calculations.txt",
                    "a",
                    encoding="utf-8"
                ) as f:
                    f.write(
                        f"{expression} = {result}\n"
                    )

        except Exception as exc:
            print(
                f"Save calculation error: {exc}"
            )

    return redirect(
        url_for("diary")
    )


if __name__ == "__main__":
    app.run(debug=True)