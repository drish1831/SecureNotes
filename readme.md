# SecureNotes — Secure Login System

## Overview

SecureNotes is a Flask-based web application created to demonstrate secure user authentication and common web security practices.

## Features

- User registration and login
- Argon2id password hashing
- Flask session-based authentication
- Protected dashboard
- Logout functionality
- Server-side input validation
- Duplicate email prevention
- Login rate limiting (5 failed attempts → 60-second lockout)
- Generic login error messages
- Parameterized SQL queries
- Secure session cookie settings

## Technologies

- Python
- Flask
- SQLite
- HTML/CSS
- Argon2id

## Security

Passwords are never stored in plain text and are hashed using Argon2id.

SQL queries use parameterized inputs to reduce SQL injection risk. Authentication is maintained using Flask sessions, and protected routes require an authenticated session.

Failed login attempts are tracked to reduce brute-force attempts.

## Testing

The application was tested for:

Registration and validation
Successful and failed login
Password hashing
Session authentication
Protected routes
Logout
Login lockout
Duplicate email handling
Parameterized database 

## Limitations

This is an educational local prototype. Production deployment would require HTTPS, persistent rate limiting, secure secret management, and additional security controls.

## Documentation

Security decisions and rejected approaches are documented in DECISIONS.md.
AI assistance used during development is documented in AI_USAGE.md.