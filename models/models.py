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
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(255), nullable=True)
    # New columns for email verification - with nullable=True for backward compatibility
    email_verified = db.Column(db.Boolean, default=False, nullable=True)
    email_verification_token = db.Column(db.String(255), nullable=True)
    last_login = db.Column(db.DateTime, nullable=True, index=True)  # Indexed for admin active users query
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=True, index=True)  # Indexed for admin sorting
    # User role: 'user' for regular users, 'admin' for administrators
    role = db.Column(db.String(20), default='user', nullable=True, index=True)  # Indexed for admin filtering
    # Demographics for analytics
    age = db.Column(db.Integer, nullable=True, index=True)  # Indexed for admin demographics analytics
    gender = db.Column(db.String(10), nullable=True, index=True)  # Indexed for admin demographics analytics

    # Relationships
    responses = db.relationship('UserResponse', backref='user', lazy=True)
    badges = db.relationship('Badge', backref='user', lazy=True)
    game_stages = db.relationship('GameStage', backref='user', lazy=True)
    scenario_progress = db.relationship('UserScenarioProgress', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user has admin role"""
        return self.role == 'admin'



# ----------------------
# QuizQuestion Model
# ----------------------
class QuizQuestion(BaseModel):
    __tablename__ = 'quiz_questions'

    scenario = db.Column(db.String(50), nullable=False, index=True)
    question = db.Column(db.Text, nullable=False)
    options = db.Column(db.Text, nullable=False)  # Store as JSON string
    answer = db.Column(db.String(255), nullable=False)
    correct_reason = db.Column(db.Text)
    incorrect_reason = db.Column(db.Text)
    used = db.Column(db.Boolean, default=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_ID'), nullable=True, index=True)

    # Relationship: one question -> many user responses
    responses = db.relationship('UserResponse', backref='question', lazy=True)


# ----------------------
# UserResponse Model
# ----------------------
class UserResponse(BaseModel):
    __tablename__ = 'user_responses'

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_ID'), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey('quiz_questions.id'), nullable=True, index=True)  # now a FK
    selected_option = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False, index=True)
    attempt_number = db.Column(db.Integer, default=1, index=True)
    stage = db.Column(db.String(50), nullable=False, index=True)


# ----------------------
# Badge Model
# ----------------------
class Badge(db.Model):
    __tablename__ = 'badges'
    id = db.Column(db.Integer, primary_key=True)
    user_ID = db.Column(db.Integer, db.ForeignKey('users.user_ID'), nullable=False, index=True)
    badge_name = db.Column(db.String(100), nullable=False, index=True)
    score = db.Column(db.Integer, nullable=False)
    number_of_attempts = db.Column(db.Integer, nullable=False)
    progress = db.Column(db.Float, nullable=False)
    claimed = db.Column(db.Boolean, default=False)  # New column to track if claimed
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=True)
    
    # Unique constraint: one badge per user per stage
    __table_args__ = (db.UniqueConstraint('user_ID', 'badge_name', name='uq_user_badge'),)



# ----------------------
# GameStage Model
# ----------------------
class GameStage(BaseModel):
    __tablename__ = 'game_stages'
    user_ID = db.Column(db.Integer, db.ForeignKey('users.user_ID'), nullable=False, index=True)
    # Use String instead of Enum for PostgreSQL compatibility (can be 'preconception', 'antenatal', 'birth', 'postnatal')
    stage_name = db.Column(db.String(50), nullable=False, index=True)
    number_of_attempts = db.Column(db.Integer, default=0)
    overall_score = db.Column(db.Integer, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=True)
    
    # Unique constraint: one record per user per stage
    __table_args__ = (db.UniqueConstraint('user_ID', 'stage_name', name='uq_user_stage'),)


# ----------------------
# UserScenarioProgress Model
# ----------------------
class UserScenarioProgress(BaseModel):
    __tablename__ = 'user_scenario_progress'
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_ID'), nullable=False, index=True)
    scenario = db.Column(db.String(50), nullable=False, index=True)
    attempt_count = db.Column(db.Integer, default=0)
    last_attempt_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=True)
    
    # Unique constraint: one record per user per scenario
    __table_args__ = (db.UniqueConstraint('user_id', 'scenario', name='uq_user_scenario'),)


# ----------------------
# UserQuestionHistory Model for Adaptive Learning
# ----------------------
class UserQuestionHistory(BaseModel):
    __tablename__ = 'user_question_history'
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_ID'), nullable=False, index=True)
    stage = db.Column(db.String(50), nullable=False, index=True)
    question_text = db.Column(db.Text, nullable=False)
    question_hash = db.Column(db.String(64), nullable=False, index=True)
    is_correct = db.Column(db.Boolean, nullable=False)
    attempt_count = db.Column(db.Integer, default=1)
    last_attempted = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    difficulty_level = db.Column(db.Integer, default=1)
    needs_review = db.Column(db.Boolean, default=False)
    
    # Unique constraint: one record per user per question hash per stage
    __table_args__ = (db.UniqueConstraint('user_id', 'question_hash', 'stage', name='uq_user_question_stage'),)


# ----------------------
# Feedback Model
# ----------------------
class Feedback(BaseModel):
    __tablename__ = 'feedback'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_ID'), nullable=True, index=True)  # Optional: can be anonymous
    user_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False, index=True)  # bug, feature, content, ui, performance, other
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending', index=True)  # pending, reviewed, resolved, replied
    admin_reply = db.Column(db.Text, nullable=True)
    screenshot_path = db.Column(db.String(255), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=True)