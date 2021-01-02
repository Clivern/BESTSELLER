## BESTSELLER

This application watches S3 bucket path for new partner products, transforms them into JSON format and then stores them on a separate S3 path. It can run on a reactive way or on a traditional polling way. It uses MySQL to keep track of tasks that need to be done, failed ones and to make sure we don't have duplicate incoming requests to act upon.


### Getting Started

Clone the project and then create a python environment:

```bash
$ git clone https://Clivern@bitbucket.org/Clivern/bestseller.git
$ cd bestseller

# This may change based on your local python setup
$ python3 -m venv venv
$ source venv/bin/activate
```

Create `.env` from `.env.example` and update DB credentials. You can use `mysql` or `sqlite`.

```bash
$ cp .env.example .env
```

```bash
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=bestseller
DB_USERNAME=root
DB_PASSWORD=root

// OR

DB_CONNECTION=sqlite
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=bestseller
DB_USERNAME=root
DB_PASSWORD=root
```

Also provide AWS S3 credentials. `ENABLE_AWS_S3_POLLING` option used to identify if the application should poll s3 continuously for new files or work with S3 object create events.

```
AWS_S3_ACCESS_KEY=
AWS_S3_SECRET_KEY=
AWS_S3_REGION_NAME=us-east-1
AWS_S3_ENDPOINT_URL=https://nyc3.digitaloceanspaces.com
AWS_S3_BUCKET_NAME=bestseller
AWS_S3_IMPORT_PATH=partners-files
AWS_S3_OUTPUT_PATH=bestseller-files
ENABLE_AWS_S3_POLLING=true
```

Install dependencies (the mandatory ones and the ones required for the sanity check command `make ci`).

```bash
$ make config
```

Migrate database

```bash
$ make migrate
```

Then run the application

```bash
$ make run
```

To run the daemon or the queue consumer

```bash
$ make daemon
```

As long as `ENABLE_AWS_S3_POLLING` is `true`, The application will keep polling the bucket for new xml files to transfer. Also you can disable polling and configure S3 Object create event to call `/api/v1/s3/event` endpoint with the new file.

If you did any code changes, you can run `make ci` to run the sanity checks locally. For all available commands, use `make help`


### Deployment

### With docker-compose

Install docker and docker-compose on your environment. Here is for ubuntu

```bash
$ apt-get update
$ sudo apt install docker.io
$ sudo systemctl enable docker
$ sudo apt install docker-compose
```

Create a config file, add configs to docker-compose.yml and then start the containers:

```bash
$ git clone https://Clivern@bitbucket.org/Clivern/bestseller.git
$ cd bestseller

# Create config file
$ cp .env.example .env

# Update AWS key, secret, bucket and import path on docker-compose.yml file
- AWS_S3_ACCESS_KEY=
- AWS_S3_SECRET_KEY=
- AWS_S3_REGION_NAME=us-east-1
- AWS_S3_ENDPOINT_URL=https://nyc3.digitaloceanspaces.com
- AWS_S3_BUCKET_NAME=bestseller
- AWS_S3_IMPORT_PATH=partners-files
- AWS_S3_OUTPUT_PATH=bestseller-files
- ENABLE_AWS_S3_POLLING=true

# Tear up
$ docker-compose up -d

# Tear down
$ docker-compose down

# Check containers
$ docker ps

# Check logs
$ tail -f /var/lib/docker/volumes/bestseller_daemon_storage/_data/logs/prod.log
$ tail -f /var/lib/docker/volumes/bestseller_app_storage/_data/logs/prod.log
```


### Notes & Limitations

* I couldn't test with a real AWS S3 since my account got locked and new one will need a credit card but it is tested with digitalOcean S3. It is the same as AWS S3 https://www.digitalocean.com/docs/spaces/resources/s3-sdk-examples/. They even use the same SDKs from amazon. So it must work with amazon S3.

* I created endpoint for the application to work based on events not only polling. My endpoint design based on this documentation https://docs.aws.amazon.com/AmazonS3/latest/dev/notification-content-structure.html . I couldn't test with AWS for the reason on bullet point one and digitalocean sadly don't support events feature. The event payload must have the bucket and the object like this command for the endpoint to work.

```bash
$ curl -X PUT \
    -H 'Content-Type: application/json' \
    -d '{"Records":[{"s3":{"bucket":{"name":"~bucket-name-here~"},"object":{"key":"~file/path/here~"}}}]}' \
    'http://127.0.0.1:8000/api/v1/s3/event' -v

# For Example
$ curl -X PUT \
    -H 'Content-Type: application/json' \
    -d '{"Records":[{"s3":{"bucket":{"name":"partners-files"},"object":{"key":"partners-files/product4.xml"}}}]}' \
    'http://127.0.0.1:8000/api/v1/s3/event'
```

* Based on time and requirements, I created an application that can push tasks to a queue and queue consumer (daemon) that will do the actual work. Also queue consumer (daemon) can poll s3 for new files and push tasks to the queue. But If the application has to handle a lot or grown number of task, we can replace the DB queue with RabbitMQ or kafka and use multiple consumers. Celery https://docs.celeryproject.org/en/stable/ is quite good and supports RabbitMQ.

* CI pipelines for both github and bitbucket included. Also a workflow to publish docker image to github registry (if it is hosted on github).

* Some classes and files added only to demonstrate the application architecture and directory structure like middlewares and themes for different application frontend, translation ... etc
