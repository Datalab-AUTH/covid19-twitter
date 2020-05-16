## covid19-twitter

This is a python script that reads data from a MongoDB filled with
Twitter data and outputs CSV files that are are ready to be visualized
using wordclouds, lineplots etc.

## Requirements

A Python 3.x installation is needed, with additional modules listed in
`requirements.txt`. Install everything needed with:

```
pip install -r requirements.txt
```

## Execution

You have to set a few envirnment variables to run this. These include:

* `MONGOURL`: A URL pointing to your MongoDB installation, including
	username, password, port and database. Example:
	"mongodb://user:pass@servername:port/dbname"
* `MONGODB`: The database you want to access. Example: "dbname"
* `MONGOCOLLECTION`: The collection within the database. Example: "mycollection"

Additionally, there is a `TWITTER_INIT` environment variable. Set it to
`1` when you first run the script. Don't set it to anything (or any
value other than `1`) for subsequent use.

## Deployment

Deployment is done using Docker. There is a docker image at
`datalabauth/covid19-twitter`. You need to mount the `app/data` directory on
the host, in order to have persistance for files.

```
export MONGOURL="mongodb://user:pass@servername:port/dbname"
export MONGODB="dbname"
export MONGOCOLLECTION="mycollection"
docker run -v /host/path/to/data:/app/data \
	-e MONGOURL \
	-e MONGODB \
	-e MONGOCOLLECTION \
	datalabauth/covid19-twitter
```

This will run the python script within the docker container every 4
hours.

