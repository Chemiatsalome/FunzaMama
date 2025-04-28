from flask import Flask, render_template, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import db  # Import db from models/__init__.py
from models.models import User, Badge, GameStage, UserResponse, QuizQuestion, UserScenarioProgress # Import models
from flask_cors import CORS
from dotenv import load_dotenv


app = Flask(__name__)


CORS(app, supports_credentials=True)

app.config.from_object('config.Config')

db.init_app(app)
migrate = Migrate(app, db)


# Import models to register them
with app.app_context():
    from models.models import *


from routes.auth_routes import Login_bp, signup_bp
from routes.system_routes import home_bp, gamestages_bp, profile_bp
from routes.gamestage_routes import preconceptionstage_bp, prenatalstage_bp , birthstage_bp , postnatalstage_bp
from routes.gamelogic import quiz_bp
# Register Blueprints (modular routes)
app.register_blueprint(Login_bp)
app.register_blueprint(signup_bp)
app.register_blueprint(home_bp)
app.register_blueprint(gamestages_bp)
app.register_blueprint(preconceptionstage_bp)
app.register_blueprint(prenatalstage_bp)
app.register_blueprint(birthstage_bp )
app.register_blueprint(postnatalstage_bp)
app.register_blueprint(quiz_bp)
app.register_blueprint(profile_bp)


# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 5000))  # Get the port from environment variables, default to 5000
#     app.run(host="0.0.0.0", port=port)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # 10000 is Render's default
    app.run(host="0.0.0.0", port=port, debug=False)  # debug=False for production

