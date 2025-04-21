from flask import Blueprint, jsonify, session, render_template, request, redirect, url_for, flash, session, json
from chatbot.modelintergration import get_chatbot_response_preconception , get_chatbot_response_birth, get_chatbot_response_postnatal, get_chatbot_response_prenatal  # Import the function that generates the quiz
from models import db
from models.models import User, QuizQuestion, UserResponse, Badge

quiz_bp = Blueprint("quiz", __name__)

from flask import session

@quiz_bp.route("/get_quiz_preconception", methods=["GET"])
def get_quiz_preconception():
    """API Endpoint to fetch AI-generated quiz (for both logged-in users and guests)"""
    user_id = session.get("user_ID", "guest_user")  # Use a default 'guest' ID for anonymous users
    print(f"User ID (or guest): {user_id}")

    try:
        quiz = get_chatbot_response_preconception(user_id)
        return jsonify(quiz)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@quiz_bp.route("/get_quiz_prenatal", methods=["GET"])
def get_quiz_prenatal():
    """API Endpoint to fetch AI-generated quiz (for both logged-in users and guests)"""
    user_id = session.get("user_ID", "guest_user")  # Use a default 'guest' ID for anonymous users
    print(f"User ID (or guest): {user_id}")

    try:
        quiz = get_chatbot_response_prenatal(user_id)
        return jsonify(quiz)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@quiz_bp.route("/get_quiz_birth", methods=["GET"])
def get_quiz_birth():
    """API Endpoint to fetch AI-generated quiz (for both logged-in users and guests)"""
    user_id = session.get("user_ID", "guest_user")  # Use a default 'guest' ID for anonymous users
    print(f"User ID (or guest): {user_id}")

    try:
        quiz = get_chatbot_response_birth(user_id)
        return jsonify(quiz)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@quiz_bp.route("/get_quiz_postnatal", methods=["GET"])
def get_quiz_postnatal():
    """API Endpoint to fetch AI-generated quiz (for both logged-in users and guests)"""
    user_id = session.get("user_ID", "guest_user")  # Use a default 'guest' ID for anonymous users
    print(f"User ID (or guest): {user_id}")

    try:
        quiz = get_chatbot_response_postnatal(user_id)
        return jsonify(quiz)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@quiz_bp.route('/select-avatar', methods=['POST'])
def select_avatar():
    if 'user_ID' in session:
        user_id = session['user_ID']
        avatar_path = request.form.get('avatar_path')

        if avatar_path:
            user = User.query.get(user_id)
            if user:
                user.avatar = avatar_path
                db.session.commit()
                flash('Avatar updated successfully!', 'success')
            else:
                flash('User not found.', 'danger')
        else:
            flash('No avatar selected.', 'warning')
    else:
        flash('Please log in to choose an avatar.', 'info')

    return redirect(url_for('gamestages.game'))  # update this if your route name is different

def check_and_award_badge(user_id, stage_name):
    MIN_ATTEMPTS_REQUIRED = 30
    REQUIRED_ACCURACY = 0.8

    # Ensure stage_name is consistent (lowercase and simplified)
    stage_name = stage_name.strip().lower()

    responses = UserResponse.query.filter_by(user_id=user_id, stage=stage_name).all()
    total_attempts = len(responses)
    correct_answers = sum(1 for r in responses if r.is_correct)

    if total_attempts >= MIN_ATTEMPTS_REQUIRED:
        accuracy = correct_answers / total_attempts

        if accuracy >= REQUIRED_ACCURACY:
            existing_badge = Badge.query.filter_by(user_ID=user_id, badge_name=stage_name).first()

            if not existing_badge:
                # If no badge exists for the user, create and award the badge
                new_badge = Badge(
                    user_ID=user_id,
                    badge_name=stage_name,
                    score=correct_answers,
                    number_of_attempts=total_attempts // 10,  # Assuming each attempt is 10 questions
                    progress=round(accuracy * 100, 2),
                    claimed=False  # Initially, the badge is not claimed
                )
                db.session.add(new_badge)
                db.session.commit()
                return {"message": f"Badge awarded for {stage_name}", "badge_claimable": True}
            else:
                return {"message": f"Badge already exists for {stage_name}", "badge_claimable": False}
        else:
            return {"message": f"Accuracy below 80% for badge in {stage_name}", "badge_claimable": False}
    else:
        return {"message": f"Not enough attempts in {stage_name} (minimum 30 needed)", "badge_claimable": False}
    
@quiz_bp.route("/submit_response", methods=["POST"])
def submit_response():
    if 'user_ID' not in session:
        return jsonify({"error": "User not logged in"}), 400

    data = request.get_json()
    user_id = session['user_ID']
    selected_option = data.get("selected_option")
    stage = data.get("stage")
    question_text = data.get("question")
    is_correct = data.get("is_correct")

    answer = data.get("answer", "")
    options = json.dumps(data.get("options", []))  # Convert list to JSON string
    correct_reason = data.get("correct_reason", "")
    incorrect_reason = data.get("incorrect_reason", "")

    try:
        # Step 1: Check if the question already exists
        existing_question = QuizQuestion.query.filter_by(
            question=question_text, user_id=user_id, scenario=stage
        ).first()

        if existing_question:
            question_id = existing_question.id
        else:
            quiz_question = QuizQuestion(
                scenario=stage,
                question=question_text,
                options=options,
                answer=answer,
                correct_reason=correct_reason,
                incorrect_reason=incorrect_reason,
                user_id=user_id
            )
            db.session.add(quiz_question)
            db.session.commit()
            question_id = quiz_question.id

        # Step 2: Save the user response
        user_response = UserResponse(
            user_id=user_id,
            question_id=question_id,
            selected_option=selected_option,
            is_correct=is_correct,
            stage=stage,
        )
        db.session.add(user_response)
        db.session.commit()

        # Step 3: Call check_and_award_badge function to award badge if criteria met
        result = check_and_award_badge(user_id, stage)  # Check if the user meets the badge criteria

        return jsonify({"success": True, "message": result['message']})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to save response: {str(e)}"}), 500


from flask import session, redirect, url_for, jsonify

@quiz_bp.route('/claim_badge/<badge_name>', methods=['POST'])
def claim_badge(badge_name):
    # Check if the user is logged in
    if 'user_ID' not in session:
        return jsonify({"success": False, "message": "User not logged in."})

    # Now retrieve user_ID from session
    user_id = session['user_ID']

    # Check if the badge exists and isn't already claimed
    badge = Badge.query.filter_by(user_ID=user_id, badge_name=badge_name).first()

    if badge and not badge.claimed:  # If the badge exists but isn't claimed yet
        badge.claimed = True
        db.session.commit()

        # Return badge details
        return jsonify({
            "success": True,
            "message": "Badge claimed successfully!",
            "score": badge.score,
            "progress": badge.progress,
            "attempts": badge.number_of_attempts,
            "claimed": badge.claimed
        })
    
    return jsonify({"success": False, "message": "Badge already claimed or not found."})
