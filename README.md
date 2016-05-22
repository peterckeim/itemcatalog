# Item Catalog
Item Catalog -- Project 3 for Full-Stack Web Dev Udacity Program

**Assignment**

You will develop an application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users will have the ability to post, edit and delete their own items.

---

The given files utilize the Python micro web framework Flask (http://flask.pocoo.org/) alongside SQLAlchemy, the Python SQL Toolkit and Object Relational Mapper (http://www.sqlalchemy.org/) in order to manage a locally hosted database which allows users to securely Create, Read, Update, and Delete their own files. Login information is currently not handled internally, but through two popular OAuth2.0 (http://oauth.net/2/) authentication APIs, Google and Facebook.

This particular database is meant to act as a public repository for data on known electromechanical Relays. Through the 'relaypopulator.py' file, data has been pre-populated with Relay Series, Parts, and fake users, giving ownership of the Series and Parts to the fake users. These parts are unable to be edited by others.

Users of this website are able to easily fetch JSON for these parts and series though appending /JSON to the end of any valid URL, excluding the manipulation (edit, new, delete) and login URL's.

###Please note:###
The following libraries and programs are required to use these series of files:

-*Python 2.7.1* (https://www.python.org/downloads/)

along with the following python library installed:

-*flask* (http://pypi.python.org/packages/source/F/Flask/Flask-0.10.1.tar.gz or 'pip install Flask' in cmd)
-*SQLAlchemy* (http://www.sqlalchemy.org/download.html or 'pip install SQLAlchemy' in cmd)
-*oauth2client* (https://pypi.python.org/pypi/oauth2client)

---

###Running the Program###

First, download this repository. You should only have 9 files in total, including:

_static_, (folder containing default profile picture if none is fetched)

_templates_, (folder containing all HTML files which interact with the flask microframework via Jinja2 templating language -- http://jinja.pocoo.org/docs/dev/)

_client_secrets.json_, (credentials file for this project's Google OAuth2.0)

_database_setup.py_, (python file used to initialize the relayDatabase.db file)

_database_setup.pyc_, (compiled code of database_setup.py)

_fb_client_secrets.json_, (credentials file for this project's Facebook OAuth2.0)

_project.py_, (main python file used to host the server)

_relayDatabase.db_, (the database file containing prepopulated data of Series, Parts, and fake Users.)

_relaypopulator.py_, (python script used to initially populate the relayDatabase.db)

The server is hosted locally on port 5000. when the project.py file is running. Enter your favorite shell, navigate to the itemcatalog folder, and run the python command

```
python project.py
```

This will start up the server on your localhost. You can access the site via navigating on your web browser to http://localhost:5000 or http://127.0.0.1:5000. The site is quite self-explanatory. You are able to log-in via your Google or Facebook credentials. This gives you the ability to create a Relay series, and add parts into the series. Nobody will be able to edit or delete these files except for you.

If you would like to recreate the database yourself, delete the relayDatabase.db file, and perform the python command

```
python database_setup.py
python relaypopulator.py
```

This will initialize the database, and populate it with data via the relaypopulator file.
