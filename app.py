from flask import Flask, render_template, request, session, redirect, url_for
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import sqlite3
import time


# --------------------------------------------------
# APP SETUP
# --------------------------------------------------

app = Flask(__name__)

# Secret key used to securely sign Flask sessions
# Should be changed before deploying the app publicly.
app.secret_key = "hilol"

# Session cookie security settings
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# False because we are currently using HTTP locally.
# To be set to True when using HTTPS in production.
app.config["SESSION_COOKIE_SECURE"] = False


# Password hashing object
ph = PasswordHasher()


# Stores failed login attempts:
# email -> [number_of_attempts, lockout_end_time]
login_attempts = {}


# --------------------------------------------------
# HOME / LOGIN PAGE
# --------------------------------------------------

@app.route("/")
def hello():
    return render_template("login.html")


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@app.route("/login", methods=["POST"])
def login():

    # Get the email and password submitted through the form
    mail = request.form.get("email")
    password = request.form.get("password")

    current_time = time.time()  # Stores current time in seconds

    # Check whether this email is currently locked out
    if mail in login_attempts:

        attempts, lockout_until = login_attempts[mail]

        if current_time < lockout_until:
            return render_template(
                "login.html",
                message="TOO MANY FAILED ATTEMPTS. PLEASE TRY AGAIN LATER."
            )

    # Connect to the database
    connection = sqlite3.connect("securenotes.db")
    cursor = connection.cursor()

    # Find the user using their email
    cursor.execute(
        "SELECT * FROM users WHERE email = ?",
        (mail,)
    )

    user = cursor.fetchone()

    # Check whether the user exists AND the password is correct
    if user is not None:

        stored_hash = user[3]

        try:
            ph.verify(stored_hash, password)

            # Login successful → reset failed attempts
            login_attempts.pop(mail, None)

            # Store user information in the session
            session["user_id"] = user[0]
            session["username"] = user[1]

            connection.close()

            # Send the user to the dashboard
            return redirect(url_for("dashboard"))

        except VerifyMismatchError:
            pass

    # --------------------------------------------------
    # LOGIN FAILED
    # --------------------------------------------------

    # Count the failed attempt
    if mail not in login_attempts:
        login_attempts[mail] = [1, 0]
    else:
        login_attempts[mail][0] += 1

    attempts = login_attempts[mail][0]

    # Lock the account/email for 60 seconds after 5 failures
    if attempts >= 5:
        login_attempts[mail][1] = current_time + 60

    connection.close()

    # Use the same message for wrong email and wrong password
    # to avoid revealing whether an account exists.
    return render_template(
        "login.html",
        message="INVALID EMAIL OR PASSWORD"
    )


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

@app.route("/dashboard")
def dashboard():

    # Only logged-in users can access the dashboard
    if "user_id" not in session:
        return "You must be logged in to access the dashboard."

    return f"WELCOME TO THE DASHBOARD, {session['username']}!"


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

@app.route("/logout")
def logout():

    # Remove all information stored in the session
    session.clear()

    # Return to the login page
    return redirect(url_for("hello"))


# --------------------------------------------------
# REGISTRATION PAGE
# --------------------------------------------------

@app.route("/register")
def register():
    return render_template("register.html")


# --------------------------------------------------
# REGISTRATION
# --------------------------------------------------

@app.route("/register", methods=["POST"])
def register_user():

    # Get registration form data
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")

    # Make sure no field is empty
    if not username or not email or not password:
        return render_template(
            "register.html",
            message="ALL FIELDS ARE REQUIRED"
        )

    # Validate username length
    if len(username) < 3 or len(username) > 30:
        return render_template(
            "register.html",
            message="USERNAME MUST BE 3-30 CHARACTERS"
        )

    # Validate password length
    if len(password) < 8:
        return render_template(
            "register.html",
            message="PASSWORD MUST BE AT LEAST 8 CHARACTERS"
        )

    # Connect to database
    connection = sqlite3.connect("securenotes.db")
    cursor = connection.cursor()

    # Check whether the email is already registered
    cursor.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    )

    existing_user = cursor.fetchone()

    if existing_user is not None:
        connection.close()

        return render_template(
            "register.html",
            message="EMAIL ALREADY REGISTERED!"
        )

    # Hash the password before storing it
    hashed_password = ph.hash(password)

    # Store the new user in the database
    cursor.execute(
        """
        INSERT INTO users (username, email, password)
        VALUES (?, ?, ?)
        """,
        (username, email, hashed_password)
    )

    connection.commit()
    connection.close()

    # Registration successful → return to login page
    return redirect(url_for("hello"))


# --------------------------------------------------
# START THE APPLICATION
# --------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)