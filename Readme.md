# Epic Events CRM

Epic Events CRM is a command-line application that allows the management of the company's CRM.
It includes three differents menus depending on the role of the user.

There are three roles:
- Management
- Sales
- Support

Depending on its role, the user will be able to read, create or delete a contract, an event, a client or a collaborator.

Sentry was added to the project to log exceptions and errors.
Permissions are used to limit the access of the users to the CRM.
Passwords are encrypted.

## Prerequisites

-SQLAlchemy
- Create a superuser
- Click
- Colorama
- Django
- Sentry


## Getting Started

    ### .env file & Sentry

    - Create a .env file at root with the following variables:
        - DB_NAME
        - DB_USER
        - DB_PASSWORD
        - SENTRY_DSN

    - Create a database and use it in the env file
    - Create an account at sentry.io and use the DSN in the env file

    ### Initialize the project
    1.
    - Open a terminal at root
    - Create a env (for environment variables) at root
    - cd ./epic_events
    - .\env\Scripts\activate
    - pip install -r requirements.txt
    -cd ./epic_events_CRM
    - python manage.py runserver
    2.
    - Open an other terminal at root
    - cd ./epic_events
    - .\env\Scripts\activate
    - cd ./epic_events_CRM 
    - python main.py
    3.
    - Type the username and password of the accessible user from the initializer.py file to access its menu
