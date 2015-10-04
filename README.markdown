text4coffee
===========

It makes coffee. What more could you want?

SMS Command Summary
===================

There are three permissions available in text4coffee: `admin` (A), `control`
(C), and query `Q`. Each command requires zero or more permissions on your
account in order to run.

Basic commands
--------------

* `on` (C): turn coffee machine on
* `off` (C): turn coffee machine off
* `(q|query)` (Q): query coffee machine state

Management commands
-------------------

* `register <password|token> <name...>` (no permissions required): register an
  account on the coffee machine. The password set in the server configuration
  and will create an account with all privileges. See below for an explanation
  of tokens.
* `token <permission...>` (A): create a registration token with the given
  privileges. Registration tokens can be used in place of the password when
  registering accounts. The account registered with a token will be given the
  privileges associated with that token. Tokens may be registered only once.
* `revoke <token>` (A): revoke a token so it may no longer.
* `unregister [number]`: unregister your account. If a number is given, then
  the `admin` privilege is required, and the account of the given number will
  be deleted.
* `list` (A): list all user accounts with their names, phone numbers, and
  permissions.

General commands
----------------

* `doc`: display a summary of commands

Setup
=====

Install system dependencies.

* postgresql
* redis

Install python dependencies.

    virtualenv --python=/usr/bin/python2.7 .
    source bin/activate
    pip install -r requirements.txt

Set up the database.

    psql> CREATE USER coffee4text WITH PASSWORD 'coffee4text4lulz';
    psql> CREATE DATABASE coffee4text;


    psql -f sql/schema.sql -d coffee4text -U coffee4text

Set up a Twilio number to hit the `/sms` endpoint of the web server.

Usage
=====

Run these scripts, in any order really.

    python analyzer.py
    python photographer.py
    python run.py

