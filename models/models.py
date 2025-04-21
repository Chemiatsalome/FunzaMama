from flask_sqlalchemy import SQLAlchemy
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

# ----------------------
# Base mixin for common fields
# ----------------------
class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)


# ----------------------
# User Model
# ----------------------
class User(db.Model):
    __tablename__ = 'users'
    user_ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(100), nullable=False)
    second_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(255), nullable=True)

    # Relationships
    responses = db.relationship('UserResponse', backref='user', lazy=True)
    badges = db.relationship('Badge', backref='user', lazy=True)
    game_stages = db.relationship('GameStage', backref='user', lazy=True)
    scenario_progress = db.relationship('UserScenarioProgress', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



# ----------------------
# QuizQuestion Model
# ----------------------
class QuizQuestion(BaseModel):
    __tablename__ = 'quiz_questions'

    scenario = db.Column(db.String(50), nullable=False)
    question = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text, nullable=False)  # Store as JSON string
    answer = db.Column(db.String(255), nullable=False)
    correct_reason = db.Column(db.Text)
    incorrect_reason = db.Column(db.Text)
    used = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_ID'), nullable=True)

    # Relationship: one question -> many user responses
    responses = db.relationship('UserResponse', backref='question', lazy=True)


# ----------------------
# UserResponse Model
# ----------------------
class UserResponse(BaseModel):
    __tablename__ = 'user_responses'

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_ID'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('quiz_questions.id'), nullable=True)  # now a FK
    selected_option = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    attempt_number = db.Column(db.Integer, default=1)
    stage = db.Column(db.String(50), nullable=False)


# ----------------------
# Badge Model
# ----------------------
class Badge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_ID = db.Column(db.Integer, db.ForeignKey('users.user_ID'), nullable=False)
    badge_name = db.Column(db.String(100), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    number_of_attempts = db.Column(db.Integer, nullable=False)
    progress = db.Column(db.Float, nullable=False)
    claimed = db.Column(db.Boolean, default=False)  # New column to track if claimed



# ----------------------
# GameStage Model
# ----------------------
class GameStage(BaseModel):
    __tablename__ = 'game_stages'
    user_ID = db.Column(db.Integer, db.ForeignKey('users.user_ID'), nullable=False)
    stage_name = db.Column(db.Enum('Preconception', 'Antenatal', 'Birth', 'Postnatal'), nullable=False)
    number_of_attempts = db.Column(db.Integer, default=0)
    overall_score = db.Column(db.Integer, nullable=False)


# ----------------------
# UserScenarioProgress Model
# ----------------------
class UserScenarioProgress(BaseModel):
    __tablename__ = 'user_scenario_progress'
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_ID'), nullable=False)
    scenario = db.Column(db.String(50), nullable=False)
    attempt_count = db.Column(db.Integer, default=0)
    last_attempt_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)
