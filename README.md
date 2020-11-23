TAMSAT
======

About
-----
This repository defines the TAMSAT website, which includes the following components:

* The main, Drupal-based website, including information on the project, links to publications, and recent news items
* A data download tool for accessing the raw TAMSAT data
* A data subsetting tool for downloading timeseries of TAMSAT data, both at a point, and averaged over a region
* The TAMSAT ALERT system for providing various metrics (in the form of graphs and data) to users via a web-based interface


Code Structure
--------------
The code for this project is split into a number of repositories, which are configured as submodules of this main project.  After checking out this repository, you will need to run:

```
git submodule update --init --recursive
```

to update the code in all of the submodules.

The following is a brief description of how the code is organised, with a high-level overview of what each component does.  Further information about each component is usually found in a `README.md` in the appropriate subdirectory.


### Root (this directory)
This directory contains this README, and the `docker-compose.yml` file which will bring up all of the services.

Prior to initialising the TAMSAT system, some configuration needs to be done.  You should fill in the SMTP (email) server in the following files:

```
data-subset/backend/config.xml
alert/app/tamsat-alert.cfg
```

and additionally must create a file named `.env` in the current directory, with the contents:

```
MYSQL_ROOT_PASSWORD=<root password>
MYSQL_USER=<user>
MYSQL_PASSWORD=<user password>
```

This configures the settings for the MySQL database which holds the content for the main, Drupal-based, TAMSAT website.  They will not generally need to be used for direct access, but must be configured for the site to function correctly.

You can then bring the system up using:

```
docker-compose up --build
```

and bring it down using

```
docker-compose stop
docker-compose down
```

Note that this is different from the standard procedure, which is simply to call `docker-compose down`.  By running the `stop` command first, it ensures that the TAMSAT ALERT system will finish running the jobs in its queue prior to shutting down.  This may mean that it will take a while before the `stop` command finishes running, but that a clean shutdown will result.


### nginx Routing (./routing/)
This contains the `Dockerfile` and the configuration for running an nginx container.  This routes HTTP requests to the appropriate Docker container.  It also exposes the public TAMSAT data directory to the web, with JSON-based directory listings.


### Drupal Website and Data Download Tool (./tamsat_www/)
This contains definitions for two Docker images - `mysql` which provides the database backend to the Drupal site; and `drupal` which contains the actual Drupal image.

This git submodule contains sensitive information and so is not available publicly.

#### `mysql`
The `mysql` container is very simple, and simply sets up and populates a MySQL instance with the desired TAMSAT information and database dump.

For instructions on how to update the database dump which populates this container, see the README in the `drupal` subdirectory.

#### `drupal`
This container has some useful tools (namely `drush`) installed alongside Drupal, and configures the connection to the MySQL container.  This directory also contains the static code for the data download tool.  This tool is implemented in HTML + Javascript using the jQuery library, and relies on the public data being exposed to the web with a JSON-based directory listing.


### Data Subsetting Tool (./data-subset/)
The data subsetting tool is a Java-based queue system for data extraction, with a web interface.

Two Docker containers are defined here - one to build the subsetting tool (`backend-build`), and one to run it on Apache Tomcat - a servlet container (`backend`).  There is a third directory `process-africa-masks`, which contains the code used to process the shapefile containing African countries into a required data file for the subset tool.  This should not need to be used unless the grid of the TAMSAT data changes, African country borders are amended.


### TAMSAT ALERT Web Tool (./alert/)
The TAMSAT ALERT web tool is a python (Flask + Celery) based queuing system and web frontend for running code written by the TAMSAT research group.

This tool comprises of three Docker containers - `redis` (direct from Docker hub), a celery worker container (defined in `Dockerfile.celeryworker`), and the main Flask webapp (running on an nginx instance, and defined in `Dockerfile`)

HTTPS Support
-------------

HTTPS support involves obtaining HTTPS certificates from the https://letsencrypt.org site and then periodically checking that these certificates are not about to expire (and updating them if they are).

To do this we add a certbot container to docker-compose, and use a utility script that needs to be run once when the service is deployed on a new host.

The script `init-letsencrypt.sh` and a general overview is available here: https://github.com/sugenk/nginx-certbot

### HTTPS setup procedure (do this for each new deployment):

(1) temporarily comment out or remove the following line from `docker-compose.yml`:

   `entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"`

(2) run the initialisation script that obtains the first SSL keys.

```
mkdir -p data/certbot/www
mkdir -p data/certbot/conf
cp routing/init-letsencrypt.sh .
sudo ./init-letsencrypt.sh
```

When prompted about whether you want to share your e-mail address with the FSF, you can press (N)

This should create a data sub-folder and install the SSL keys under `data/certbot/conf/live/tamsat.org.uk`

After a SUCCESS message is printed about the keys being successfully installed, there is an error reported about not starting nginx, that can safely be ignored.

(3) change permissions so that the certificates can be read by the tamsat account.  For example:

```
sudo chmod -R a+rx data/certbot/conf/live/*
```

(4) Restore the change to `docker-compose.yml` in step (1) and remove the `init-letsencrypt.sh` script copied to the root directory in step (2)

You should now be able to bring up the tamsat service as described above.

Author
------
[@guygriffiths](https://github.com/guygriffiths)
