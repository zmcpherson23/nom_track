import os
from flask import Flask
from flask_cache import Cache
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy


cache = Cache(config={'CACHE_TYPE': 'simple'})
app = Flask(__name__,
            static_folder="./dist/static",
            template_folder="./dist")
cache.init_app(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///{}".format(os.path.join(BASE_DIR, "data-dev.db"))
db = SQLAlchemy(app)

# Enable CORS
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

from nom_track_app.app.app import app