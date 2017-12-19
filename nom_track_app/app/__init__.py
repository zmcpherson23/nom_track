from flask import Flask
from flask_cache import Cache

cache = Cache(config={'CACHE_TYPE': 'simple'})
app = Flask(__name__)
cache.init_app(app)

from nom_track_app.app.app import app