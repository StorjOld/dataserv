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
manager = Manager(app)
manager.add_command('db', MigrateCommand)
