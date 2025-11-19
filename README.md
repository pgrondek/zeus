# The Zeus election server

[![pipeline status](https://gitlab.com/partia_razem_public/zeus/badges/master/pipeline.svg)](https://gitlab.com/partia_razem_public/zeus/-/commits/master)
[![codecov](https://codecov.io/gh/pwmarcz/zeus/branch/master/graph/badge.svg)](https://codecov.io/gl/partia_razem_public/zeus)

LICENCE: This code is released under the GPL v3 or later

This is a fork of Ben Adida's Helios server. The differences from Helios are as follows:

* Whereas Helios produces election results, Zeus produces a tally of the ballots cast.

* This allows Zeus to be used in voting systems other than approval voting (which is supported
  by Helios), since the vote tally can be fed to any other system that actually produces the
  election results.

* In terms of overall architecture and implementation it is closer to the [original Helios
  implementation](http://static.usenix.org/events/sec08/tech/full_papers/adida/adida.pdf) than Helios v. 3.

## Installation

Here is how to set up Zeus and database on your local machine.

1. Set up environment variables: copy `.env.template` to `.env`, customize.

2. If necessary: install PostgreSQL (e.g. `sudo apt install postgresql`),
   create user and database:

        sudo -u postgres createuser zeus --pwprompt
        createdb zeus --owner zeus

3. (optional) Make sure PostgreSQL accepts connections from Docker:

    * In `/etc/postgresql/.../main/postgresql.conf`, add Docker interface
      address (172.17.0.1) to `listen_addresses`, e.g.:

      ```
      listen_addresses = 'localhost,172.17.0.1'
      ```

    * In `/etc/postgresql/.../main/pg_hba.conf`, add a line for Zeus to be able
      to connect from all Docker's networks:

      ```
      # TYPE  DATABASE   USER  ADDRESS      METHOD
      ...
      host    zeus       zeus  172.0.0.0/8  md5
      ```

      For running tests, you need to allow access to additional databases:

      ```
      host    all       zeus  172.0.0.0/8  md5
      ```

    * Restart Postgres:

      ```
      sudo systemctl restart postgresql.service
      ```

    * Verify if you can connect from Docker:

      ```
      docker run --rm -it postgres:latest psql -h 172.17.0.1 -U zeus zeus
      ```

5. Set up the initial database: run migrations, create user and institution:

        docker-compose exec prod bash

        # inside the container:
        python manage.py migrate
        python manage.py manage_users --create-institution "ZEUS"
        python manage.py manage_users --create-user <username> --institution=1 --superuser

## Run (development)

To run Zeus locally:

    docker-compose up

This will run a Django development server under `localhost:8000`. It should
reload automatically as you edit the code. The files will be mounted from host,
so that all changes will be visible inside the container.

To open a shell in the Docker container, for running additional commands:

    docker-compose run --rm dev sh

## Run tests

    docker-compose run --rm dev pytest -v

You can run multiple tests in parallel:

    docker-compose run --rm dev pytest -v -n auto

If you ran into permission problems with Postgres, see "Installation" above,
the part about `pg_hba.conf`.

## Manage Python packages

We use [pip-tools](https://github.com/jazzband/pip-tools) to manage dependencies:

- `requirements.in` - contains a list of direct dependencies, with version
  specifiers if necessary
- `requirements.txt` - auto-generated from `requirements.in`, all packages, all
  versions pinned

In order to install a new package:

- add it to `requirements.in`
- regenerate the list of packages (`requirements.txt`):

        docker-compose run --rm dev pip-compile

  If upgrading existing packages, run `pip-compile --upgrade`.

- rebuild the container to install new packages:

        docker-compose build

- make sure to commit the changes to both files!

## Run (production)

1. Build the containers:

        docker-compose -f docker-compose-prod.yml build

2. Make sure to edit `.env` and set the right parameters.

3. Run:

        docker-compose -f docker-compose-prod.yml up

This will serve Zeus under `localhost:8000`. You can proxy it from outside, add
SSL, etc.

If you update the code, execute database migrations before restarting:

    docker-compose -f docker-compose-prod.yml run --rm prod python manage.py migrate

## Environment properties

### Database configuration

| ENV        | Note                            | Default |
|------------|---------------------------------|---------|
| PGDATABASE | Postgres database name for zeus | `zeus`  |
| PGUSER     | Postgres user name              | `zeus`  |
| PGPASSWORD | Postgres password               | ``      |
| PGHOST     | Postgres database hostname/IP   | ``      |
| PGPORT     | Postgres database port          | `5432`  |

### Django configuration

| ENV          | Note                                           | Default     |
|--------------|------------------------------------------------|-------------|
| `SECRET_KEY` | Secret key for generating user sessions hashes | `replaceme` |

### Zeus configuration

| ENV                         | Note                                                | Example                    |
|-----------------------------|-----------------------------------------------------|----------------------------|
| `ZEUS_PROD_HOST`            | Hostname for your zeus instance                     | `zeus.example.com`         |
| `ZEUS_PROD_USE_HTTPS`       | Use https instead of http                           | `True`                     |
| `SITE_TITLE`                | Site title                                          | `Zeus election server`     |
| `LANGUAGE_CODE`             | Language code                                       | `pl`                       |
| `HELP_EMAIL_ADDRESS`        | Zeus support email address                          | `zeus-support@example.com` |
| `ZEUS_DEPLOYMENT`           | Determines whenever it's `dev` or `prod` deployment | `prod`                     |
| `ZEUS_ADMIN_NAME`           | Name of zeus admin                                  | `Zeus admin`               |
| `ZEUS_ADMIN_EMAIL`          | Email address of zeus admin                         | `zeus.admin@example.com`   |
| `ZEUS_ELECTION_ADMIN_NAME`  | Name of election admin                              | `Zeus admin`               |
| `ZEUS_ELECTION_ADMIN_EMAIL` | Email address of election admin                     | `zeus.admin@example.com`   |

### Email configuration

| ENV                   | Note                                                 | Example                                           |
|-----------------------|------------------------------------------------------|---------------------------------------------------|
| `EMAIL_HOST`          | Email server                                         | `smtp.gmail.com`                                  |
| `EMAIL_PORT`          | Port on which we connect to email server             | `25` - SMTP <br/> `465` - SMTPS <br/> `587` - TLS |
| `EMAIL_HOST_USER`     | User for email server                                | `zeus`                                            |
| `EMAIL_HOST_PASSWORD` | Password for user email account                      | `verysecurepassword`                              |
| `EMAIL_USE_TLS`       | Whenever to use TLS for connecting to email server   | `True`                                            |
| `EMAIL_USE_SSL`       | Whenever to use SMTPS for connecting to email server |                                                   |
| `DEFAULT_FROM_EMAIL`  | Email address from which we send emails              | `zeus@example.com`                                |
| `DEFAULT_FROM_NAME`   | Name that will be displayed from whom is email       | `Zeus admin`                                      |

### Oauth authentication

Mainly supported oauth authentication is `discord`, there is also a `other` client but it's not tested and can have a
missing functionality

| ENV                        | Note                                                      | Default   |
|----------------------------|-----------------------------------------------------------|-----------|
| OAUTH_ENABLED              | Enable oauth authentication                               | `False`   |
| OAUTH_TYPE                 | Oauth client type, supported values: `discord`, `other`*  | `discord` |
| OAUTH_CLIENT_ID            | Oauth client id                                           | `None`    |
| OAUTH_CLIENT_SECRET        | Oauth client secret                                       | `None`    |
| OAUTH_CREATE_ADMIN         | Create voting admin user in zeus if account doesn't exist | `True`    |
| OAUTH_ADMIN_INSTITUTION_ID | In which institution should we create admin user          | 1         |

#### Discord client properties

| ENV                         | Note                                                   | Example              | Default |
|-----------------------------|--------------------------------------------------------|----------------------|---------|
| OAUTH_DISCORD_SERVER_ID     | Required discord server/guild for user to authenticate | `123456789123456789` | None    |
| OAUTH_DISCORD_ADMIN_ROLE_ID | User role to create                                    | `123456789123456789` | None    |

#### Other client properties

| ENV                     | Note                                                          | Example                                              |
|-------------------------|---------------------------------------------------------------|------------------------------------------------------|
| OAUTH_AUTHORIZATION_URL | Url where application will redirect user to get authorization | `https://authentik.company/application/o/authorize/` | 
| OAUTH_TOKEN_URL         | Url where application will get user token for challange token | `https://authentik.company/application/o/token/`     | 
| OAUTH_USER_INFO_URL     | Url where application will get user info                      | `https://authentik.company/application/o/userinfo/`  | 
