from flask import Flask

from .config import Config
from .extensions import db, migrate

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
migrate.init_app(app, db)

from .views import ui_bp
from .api_views import api_bp
from .error_handlers import register_error_handlers

app.register_blueprint(ui_bp)
app.register_blueprint(api_bp)
register_error_handlers(app)
