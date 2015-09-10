import os
from flask import Flask
from flask.ext.cache import Cache
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

# Initialize the Flask application
cache = Cache(config={'CACHE_TYPE': 'simple'})

app = Flask(__name__)
app.config.from_pyfile('config.py')
db = SQLAlchemy(app)
cache.init_app(app)

migrate = Migrate(app, db)

# didn't fix: configparser.NoSectionError: No section: 'alembic'
#migrate = Migrate()
#migrate.init_app(app, db, directory=os.path.join(
#    os.path.realpath(os.path.dirname(__file__)), "migrations"
#))

manager = Manager(app)
manager.add_command('db', MigrateCommand)
