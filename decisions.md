# Secure Login System — Security Decisions

## 1. Password Storage

### Decision
Use Argon2id to hash user passwords before storing them in the database.

### Why?
Passwords should never be stored as plain text. If the database is compromised, plain-text passwords would immediately be exposed.
Argon2id is designed specifically for password hashing and is resistant to brute-force attacks.

---

## 2. Database Queries

### Decision
Use parameterized SQL queries with `?` placeholders.

### Why?
User input should not be directly inserted into SQL statements. Parameterized queries help prevent SQL injection.

---

## 3. Authentication

### Decision
Use Flask sessions to maintain the user's authenticated state.

### Why?
After successful login, the user's ID is stored in the session. Protected routes check whether a valid user ID exists before allowing access.

---

## 4. Password Verification
### Decision
Verify passwords using Argon2 rather than comparing passwords directly.

### Why?
The database contains only the password hash. During login, Argon2 verifies the submitted password against the stored hash.

---

## 5. Login Rate Limiting
### Decision
Lock an email for 60 seconds after 5 failed login attempts.

### Why?
Repeated login attempts can be used to guess passwords. Temporary lockout makes brute-force attacks more difficult.

### Limitation
The current implementation stores login-attempt information in memory. Restarting the application clears the counters. A production application would use a persistent or distributed rate-limiting system.

---

## 6. Generic Login Errors
### Decision
Use the same error message for an incorrect email and an incorrect password.

### Why?
Different error messages could allow an attacker to determine whether a particular email address is registered.
The application therefore displays:
"INVALID EMAIL OR PASSWORD"
for both cases.

---

## 7. Input Validation
### Decision
Validate registration data on the server.
Current Rules-
Username is required.
Email is required.
Password is required.
Username must contain 3–30 characters.
Password must contain at least 8 characters.

### Why?
Client-side validation can be bypassed, so important validation must also happen on the server.

---

# REJECTED/REVISED APPROACHES
## 1. Plain-Text Password Storage — Rejected
Initially, a simple login system could store the password directly in the database.
This approach was rejected because anyone who gains access to the database could immediately read all user passwords.
The final implementation uses Argon2id password hashing instead.

## 2. Hardcoded User Credentials — Rejected
During the early prototype, login credentials were stored directly in Python code.
This was useful for understanding the basic login flow but was rejected for the final implementation.
The final system stores users in SQLite and stores only password hashes.

## 3. Detailed Login Error Messages — Rejected
Messages such as:
"EMAIL NOT FOUND"
"WRONG PASSWORD"
were avoided.
The final system uses one generic authentication error to reduce account enumeration risk.
