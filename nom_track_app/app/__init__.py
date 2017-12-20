from flask import Flask
from flask_cache import Cache
from flask_cors import CORS

cache = Cache(config={'CACHE_TYPE': 'simple'})
app = Flask(__name__,
            static_folder="./dist/static",
            template_folder="./dist")
cache.init_app(app)

# Enable CORS
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

from nom_track_app.app.app import app