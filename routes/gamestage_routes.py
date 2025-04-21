from flask import Blueprint, render_template, request, redirect, url_for, session,flash
from models.models import User
# from app import db

preconceptionstage_bp = Blueprint("preconception", __name__)
prenatalstage_bp = Blueprint("prenatal", __name__)
birthstage_bp = Blueprint("birth", __name__)
postnatalstage_bp = Blueprint("postnatal", __name__)


@preconceptionstage_bp.route('/preconception')
def preconception():
    
    username = "Guest"
    user = None  # Initialize user to None

    if 'user_ID' in session:
        user_id = session['user_ID']
        user = User.query.get(user_id)
        if user:
            username = user.username

        return render_template('preconception.html', user_logged_in=True, user=user, username=username)
    else:
        flash('Login for a personalized experience.', 'info')
        return render_template('preconception.html', user_logged_in=False, user=user, username=username)

    
@prenatalstage_bp.route('/prenatal')
def prenatal():

    username = "Guest"
    user = None  # Initialize user to None

    if 'user_ID' in session:
        # User is logged in, show personalized experience
        user_id = session['user_ID']
        user = User.query.get(user_id)
        if user:
            username = user.username
            
        return render_template('prenatal.html', user_logged_in=True, user = user, username = username)
    else:
        # Guest user, show limited features and a login prompt
        flash('Login for a personalized experience.', 'info')
        return render_template('prenatal.html', user_logged_in=False, username=username, user=user)
    
   

@birthstage_bp.route('/birth')
def birth():

    username = "Guest"
    user = None  # Initialize user to None

    if 'user_ID' in session:
        # User is logged in, show personalized experience
        user_id = session['user_ID']
        user = User.query.get(user_id)
        if user:
            username = user.username

        return render_template('birth.html', user_logged_in=True, user=user, username=username)
    else:
        # Guest user, show limited features and a login prompt
        flash('Login for a personalized experience.', 'info')
        return render_template('birth.html', user_logged_in=False, username=username, user=user)

@postnatalstage_bp.route('/postnatal')
def postnatal():

    username = "Guest"  # Default username
    user = None  # Initialize user to None
    
    if 'user_ID' in session:
        # User is logged in, show personalized experience
        user_id = session['user_ID']
        user = User.query.get(user_id)
        if user:
            username = user.username
        return render_template('postnatal.html', user_logged_in=True, user=user, username = username)
    else:
        # Guest user, show limited features and a login prompt
        flash('Login for a personalized experience.', 'info')
        return render_template('postnatal.html', user_logged_in=False, username=username, user=user)