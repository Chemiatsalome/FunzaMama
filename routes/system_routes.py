from flask import Blueprint, render_template, request, redirect, url_for, session,flash,  jsonify
from chatbot.chatbot import get_chatbot_response  # Import the chatbot function
from models.models import User, Badge, UserResponse
from .gamelogic import check_and_award_badge
from chatbot.modelintergration import get_teaching_facts_by_stage

from models import db

home_bp = Blueprint("home", __name__)
gamestages_bp = Blueprint("gamestages", __name__)
profile_bp = Blueprint("profile", __name__)


@home_bp.route('/', methods=['GET', 'POST'])
def home():
    username = "Guest"  # Default username
    user = None  # Initialize user to None

    # Check if user is logged in
    if 'user_ID' in session:
        user_id = session['user_ID']
        user = User.query.get(user_id)
        if user:
            username = user.username

    if request.method == 'POST':  # Chatbot logic
        data = request.get_json()
        user_message = data.get('message', '')
        user_role = data.get('user_role', 'Curious Learner')  # Default role
        language = data.get('language', 'English')  # Default language

        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        bot_response = get_chatbot_response(user_message, language, user_role)
        return jsonify({"response": bot_response})

    # For GET request
    return render_template('index.html', user=user, username = username)


@gamestages_bp.route('/gamestages')
def game():
    username = "Guest"
    earned_stages = []
    badge_claimable = {}
    selected_badge = request.args.get('badge')  # Get selected badge key from query string
    total_stages = 4  # preconception, antenatal, birth_and_delivery, postnatal

    if 'user_ID' in session:
        user_id = session['user_ID']
        user = User.query.get(user_id)

        if user:
            username = user.username

            # Get all earned badge names
            earned_badges = Badge.query.filter_by(user_ID=user_id).all()
            earned_stages = [badge.badge_name for badge in earned_badges]

            # Count stages with progress > 0
            completed_stages = sum(1 for badge in earned_badges if badge.progress > 0)
            overall_progress = int((completed_stages / total_stages) * 100)

            # Prepare badge data
            badge_data = {}
            for stage in ['preconception', 'antenatal', 'birth_and_delivery', 'postnatal']:
                badge = Badge.query.filter_by(user_ID=user_id, badge_name=stage).first()
                if badge:
                    badge_data[stage] = {
                        'score': badge.score,
                        'progress': badge.progress,
                        'attempts': badge.number_of_attempts
                    }
                else:
                    badge_data[stage] = {
                        'score': 0,
                        'progress': 0,
                        'attempts': 0
                    }

            selected_badge_data = badge_data.get(selected_badge) if selected_badge else None

            return render_template(
                'gamestages.html',
                user_logged_in=True,
                user=user,
                username=username,
                earned_stages=earned_stages,
                badge_claimable=badge_claimable,
                badge_data=badge_data,
                selected_badge=selected_badge,
                selected_badge_data=selected_badge_data,
                overall_progress=overall_progress
            )
        else:
            flash('User not found, please login again.', 'error')
            return redirect(url_for('auth.login'))

    # Guest user fallback
    flash('Login for a personalized experience.', 'info')
    return render_template(
        'gamestages.html',
        user_logged_in=False,
        username=username,
        user=None,
        earned_stages=[],
        badge_claimable={},
        badge_data={},
        selected_badge=None,
        selected_badge_data=None,
        overall_progress=0  # guests don't track progress
    )

# @profile_bp.route('/profile')
# def profile():
#     user_id = session['user_id']
#     user = get_user(user_id)
#     game_stats = get_game_stats(user_id)

#     # Determine the most failed stage
#     most_failed_stage = max(game_stats['stages'], key=lambda x: x['failed'], default=None)
#     if most_failed_stage:
#         most_failed_stage['facts'] = generate_facts(most_failed_stage['name'])

#     return render_template('profile.html', username=user.username, stats={
#         "total_attempted": game_stats['total'],
#         "total_correct": game_stats['correct'],
#         "total_failed": game_stats['failed'],
#         "leading_stage": get_leading_stage(game_stats),
#         "stages": game_stats['stages'],
#         "most_failed_stage": most_failed_stage
#     })


from flask import redirect, url_for, session, flash

@profile_bp.route('/profile', methods=['GET', 'POST'])
def view_profile():
    # Default values for guests
    username = "Guest"
    stats = {
        "total_attempted": 0,
        "total_correct": 0,
        "total_failed": 0,
        "leading_stage": "",
        "stages": [],
        "most_failed_stage": {
            "name": "",
            "facts": []
        }
    }

    # Check if the user is logged in
    if 'user_ID' not in session:
        flash("You need to be logged in to view your profile.", 'warning')  # Flash message
        return redirect(url_for('home.home'))  # Redirect to the home page if user is not logged in

    # If the user is logged in, proceed with fetching their data
    user_id = session['user_ID']
    user = User.query.get(user_id)

    if user:
        username = user.username  # Use the logged-in user's username
        avatar = user.avatar

        # Handle POST request to change username
        if request.method == 'POST':
            new_username = request.form['username']

            # Check if the new username already exists
            existing_user = User.query.filter_by(username=new_username).first()
            if existing_user:
                flash("Username already exists, please pick a different one.", 'error')
            else:
                # Update username in the database
                user.username = new_username
                db.session.commit()
                flash("Username updated successfully!", 'success')
                username = new_username  # Update username for the current session

        # Query user responses
        responses = UserResponse.query.filter_by(user_id=user_id).all()

        # Initialize data for stages
        stage_data = {
            'prenatal': {'correct': 0, 'failed': 0},
            'preconception': {'correct': 0, 'failed': 0},
            'birth': {'correct': 0, 'failed': 0},
            'postnatal': {'correct': 0, 'failed': 0}
        }

        # Count total attempts, correct, and failed answers
        for response in responses:
            if response.is_correct:
                stats["total_correct"] += 1
                stage_data[response.stage]['correct'] += 1
            else:
                stats["total_failed"] += 1
                stage_data[response.stage]['failed'] += 1
            stats["total_attempted"] += 1

        # Find the leading stage based on the highest number of correct answers
        leading_stage = max(stage_data, key=lambda stage: stage_data[stage]['correct'])
        stats["leading_stage"] = leading_stage.capitalize()

        # Prepare data for individual stages
        stats["stages"] = [
            {"name": "Prenatal Care", "correct": stage_data['prenatal']['correct'], "failed": stage_data['prenatal']['failed']},
            {"name": "Preconception Care", "correct": stage_data['preconception']['correct'], "failed": stage_data['preconception']['failed']},
            {"name": "Labor & Delivery", "correct": stage_data['birth']['correct'], "failed": stage_data['birth']['failed']},
            {"name": "Postnatal Care", "correct": stage_data['postnatal']['correct'], "failed": stage_data['postnatal']['failed']}
        ]

        # Find the most failed stage based on the highest number of failed answers
        most_failed_stage = max(stage_data, key=lambda stage: stage_data[stage]['failed'])

        # Get teaching facts from LLaMA model
        teaching_facts = get_teaching_facts_by_stage(most_failed_stage)

        # Add to stats
        stats["most_failed_stage"]["name"] = most_failed_stage.capitalize()
        stats["most_failed_stage"]["facts"] = teaching_facts

    # Render the profile page with the dynamic username and stats
    return render_template("profile.html", username=username, stats=stats, avatar=avatar, user=user)
