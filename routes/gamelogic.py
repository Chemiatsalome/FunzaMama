from flask import Blueprint, jsonify, session, render_template, request, redirect, url_for, flash, session, json
from chatbot.optimized_modelintegration import get_chatbot_response_preconception , get_chatbot_response_birth, get_chatbot_response_postnatal, get_chatbot_response_prenatal, get_hybrid_questions, get_performance_stats, track_session_question, reset_stage_questions, clear_stage_session  # Import the optimized function that generates the quiz
from chatbot.adaptive_learning import generate_adaptive_questions, record_question_attempt, get_learning_insights
from models import db
from models.models import User, QuizQuestion, UserResponse, Badge

quiz_bp = Blueprint("quiz", __name__)

from flask import session

@quiz_bp.route("/get_quiz_preconception", methods=["GET"])
def get_quiz_preconception():
    """API Endpoint to fetch adaptive quiz questions for preconception stage"""
    user_id = session.get("user_ID", "guest_user")
    print(f"User ID (or guest): {user_id}")

    try:
        # Clear session if starting a new round (last attempt has 10+ questions)
        if user_id != "guest_user":
            existing_responses = UserResponse.query.filter_by(user_id=user_id, stage="preconception").all()
            if existing_responses:
                max_attempt = max(r.attempt_number for r in existing_responses)
                current_attempt_responses = [r for r in existing_responses if r.attempt_number == max_attempt]
                if len(current_attempt_responses) >= 10:
                    from chatbot.optimized_modelintegration import clear_stage_session
                    clear_stage_session("preconception", user_id)
                    print(f"Debug - Cleared session for new round (attempt {max_attempt + 1})")
        
        # Use optimized hybrid questions - returns instant questions first (0ms), then cached, then AI-generated
        # This is much faster than hybrid_ai_service which uses the slow 405B model
        quiz = get_hybrid_questions("preconception", user_id, difficulty_level=1)
        
        # Ensure we have a list of questions
        if not isinstance(quiz, list) or len(quiz) == 0:
            # Fallback to instant questions if hybrid fails
            from chatbot.optimized_modelintegration import get_instant_questions
            quiz = get_instant_questions("preconception", 10)
        
        return jsonify({
            "success": True,
            "questions": quiz,
            "count": len(quiz)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@quiz_bp.route("/get_quiz_prenatal", methods=["GET"])
def get_quiz_prenatal():
    """API Endpoint to fetch adaptive quiz questions for prenatal stage"""
    user_id = session.get("user_ID", "guest_user")
    print(f"User ID (or guest): {user_id}")

    try:
        # Clear session if starting a new round (last attempt has 10+ questions)
        if user_id != "guest_user":
            existing_responses = UserResponse.query.filter_by(user_id=user_id, stage="prenatal").all()
            if existing_responses:
                max_attempt = max(r.attempt_number for r in existing_responses)
                current_attempt_responses = [r for r in existing_responses if r.attempt_number == max_attempt]
                if len(current_attempt_responses) >= 10:
                    from chatbot.optimized_modelintegration import clear_stage_session
                    clear_stage_session("prenatal", user_id)
                    print(f"Debug - Cleared session for new round (attempt {max_attempt + 1})")
        
        # Use optimized hybrid questions - returns instant questions first (0ms), then cached, then AI-generated
        # This is much faster than hybrid_ai_service which uses the slow 405B model
        quiz = get_hybrid_questions("prenatal", user_id, difficulty_level=1)
        
        # Ensure we have a list of questions
        if not isinstance(quiz, list) or len(quiz) == 0:
            # Fallback to instant questions if hybrid fails
            from chatbot.optimized_modelintegration import get_instant_questions
            quiz = get_instant_questions("prenatal", 10)
        
        return jsonify({
            "success": True,
            "questions": quiz,
            "count": len(quiz)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@quiz_bp.route("/get_quiz_birth", methods=["GET"])
def get_quiz_birth():
    """API Endpoint to fetch adaptive quiz questions for birth stage"""
    user_id = session.get("user_ID", "guest_user")
    print(f"User ID (or guest): {user_id}")

    try:
        # Clear session if starting a new round (last attempt has 10+ questions)
        # Check database using normalized stage name, but clear session using route stage name
        if user_id != "guest_user":
            existing_responses = UserResponse.query.filter_by(user_id=user_id, stage="birth_and_delivery").all()
            if existing_responses:
                max_attempt = max(r.attempt_number for r in existing_responses)
                current_attempt_responses = [r for r in existing_responses if r.attempt_number == max_attempt]
                if len(current_attempt_responses) >= 10:
                    from chatbot.optimized_modelintegration import clear_stage_session
                    # Clear session using "birth" (what get_hybrid_questions uses)
                    clear_stage_session("birth", user_id)
                    print(f"Debug - Cleared session for new round (attempt {max_attempt + 1})")
        
        # Use optimized hybrid questions - returns instant questions first (0ms), then cached, then AI-generated
        # This is much faster than hybrid_ai_service which uses the slow 405B model
        quiz = get_hybrid_questions("birth", user_id, difficulty_level=1)
        
        # Ensure we have a list of questions
        if not isinstance(quiz, list) or len(quiz) == 0:
            # Fallback to instant questions if hybrid fails
            from chatbot.optimized_modelintegration import get_instant_questions
            quiz = get_instant_questions("birth", 10)
        
        return jsonify({
            "success": True,
            "questions": quiz,
            "count": len(quiz)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@quiz_bp.route("/get_quiz_postnatal", methods=["GET"])
def get_quiz_postnatal():
    """API Endpoint to fetch adaptive quiz questions for postnatal stage"""
    user_id = session.get("user_ID", "guest_user")
    print(f"User ID (or guest): {user_id}")

    try:
        # Clear session if starting a new round (last attempt has 10+ questions)
        if user_id != "guest_user":
            existing_responses = UserResponse.query.filter_by(user_id=user_id, stage="postnatal").all()
            if existing_responses:
                max_attempt = max(r.attempt_number for r in existing_responses)
                current_attempt_responses = [r for r in existing_responses if r.attempt_number == max_attempt]
                if len(current_attempt_responses) >= 10:
                    from chatbot.optimized_modelintegration import clear_stage_session
                    clear_stage_session("postnatal", user_id)
                    print(f"Debug - Cleared session for new round (attempt {max_attempt + 1})")
        
        # Use optimized hybrid questions - returns instant questions first (0ms), then cached, then AI-generated
        # This is much faster than hybrid_ai_service which uses the slow 405B model
        quiz = get_hybrid_questions("postnatal", user_id, difficulty_level=1)
        
        # Ensure we have a list of questions
        if not isinstance(quiz, list) or len(quiz) == 0:
            # Fallback to instant questions if hybrid fails
            from chatbot.optimized_modelintegration import get_instant_questions
            quiz = get_instant_questions("postnatal", 10)
        
        return jsonify({
            "success": True,
            "questions": quiz,
            "count": len(quiz)
        })
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
    MIN_ATTEMPTS_REQUIRED = 3  # Require 3 complete rounds
    REQUIRED_ACCURACY_PER_ROUND = 0.9  # Each round must have 90% accuracy

    # Debug print BEFORE normalization
    print(f"Raw stage name received: '{stage_name}'")

    # Normalize the stage name
    stage_name = stage_name.strip().lower()
    badge_to_stage = {
        "preconception care": "preconception",
        "preconception": "preconception",
        "antenatal care": "prenatal",
        "prenatal": "prenatal",  # Map prenatal to prenatal for backend
        "birth and delivery": "birth_and_delivery",
        "birth": "birth_and_delivery",  # Map birth to birth_and_delivery for backend
        "postnatal care": "postnatal",
        "postnatal": "postnatal"
    }
    normalized_stage = badge_to_stage.get(stage_name, stage_name)

    # Debug print AFTER normalization
    print(f"Normalized stage: '{normalized_stage}'")

    # Fetch all the responses for the user in this stage
    responses = UserResponse.query.filter_by(user_id=user_id, stage=normalized_stage).all()
    total_questions_attempted = len(responses)
    
    # Calculate correct answers (overall)
    correct_answers = sum(1 for r in responses if r.is_correct)
    
    # Calculate overall accuracy
    overall_accuracy = correct_answers / total_questions_attempted if total_questions_attempted else 0

    # Count unique attempts for this stage
    unique_attempts = len(set(r.attempt_number for r in responses))
    
    # NEW LOGIC: Check each round separately for 90% accuracy
    # Group responses by attempt_number
    attempts_data = {}
    for r in responses:
        if r.attempt_number not in attempts_data:
            attempts_data[r.attempt_number] = {'total': 0, 'correct': 0}
        attempts_data[r.attempt_number]['total'] += 1
        if r.is_correct:
            attempts_data[r.attempt_number]['correct'] += 1
    
    # Calculate accuracy per attempt
    rounds_with_90_percent = 0
    round_details = []
    for attempt_num, data in sorted(attempts_data.items()):
        attempt_accuracy = data['correct'] / data['total'] if data['total'] > 0 else 0
        round_details.append({
            'attempt': attempt_num,
            'accuracy': attempt_accuracy,
            'total': data['total'],
            'correct': data['correct']
        })
        # A round qualifies if it has at least 90% accuracy AND at least 10 questions (complete round)
        if attempt_accuracy >= REQUIRED_ACCURACY_PER_ROUND and data['total'] >= 10:
            rounds_with_90_percent += 1
    
    # More debugging output
    print(f"Debug - check_and_award_badge: user_id={user_id}, stage={normalized_stage}")
    print(f"Debug - Total Questions Attempted: {total_questions_attempted}")
    print(f"Debug - Correct Answers: {correct_answers}")
    print(f"Debug - Overall Accuracy: {overall_accuracy*100:.2f}%")
    print(f"Debug - Unique Attempts: {unique_attempts}")
    print(f"Debug - Rounds with 90%+: {rounds_with_90_percent}/{MIN_ATTEMPTS_REQUIRED}")
    print(f"Debug - MIN_ATTEMPTS_REQUIRED: {MIN_ATTEMPTS_REQUIRED}")
    print(f"Debug - REQUIRED_ACCURACY_PER_ROUND: {REQUIRED_ACCURACY_PER_ROUND*100:.0f}%")
    
    # Debug each round
    for rd in round_details:
        print(f"Debug - Round {rd['attempt']}: {rd['correct']}/{rd['total']} = {rd['accuracy']*100:.1f}%")
    
    # Calculate progress based on rounds with 90%+ accuracy
    # - If both requirements are met: 100%
    # - If only rounds met: 50% + (rounds/min_rounds) * 25%
    # - If neither met: (rounds/min_rounds) * 50%
    
    rounds_met = rounds_with_90_percent >= MIN_ATTEMPTS_REQUIRED
    
    if rounds_met:
        progress = 100.0  # All requirements met
    else:
        # Calculate progress based on number of qualifying rounds
        rounds_ratio = min(rounds_with_90_percent / MIN_ATTEMPTS_REQUIRED, 1.0)
        progress = rounds_ratio * 100.0
    
    progress = round(progress, 1)
    
    # Debug progress calculation
    print(f"Debug - Rounds Met: {rounds_met} ({rounds_with_90_percent}/{MIN_ATTEMPTS_REQUIRED})")
    print(f"Debug - Final Progress: {progress:.1f}%")

    # Fetch or create badge
    badge = Badge.query.filter_by(user_ID=user_id, badge_name=normalized_stage).first()
    if not badge:
        badge = Badge(
            user_ID=user_id,
            badge_name=normalized_stage,
            claimed=False
        )
        db.session.add(badge)

    badge.score = correct_answers
    badge.number_of_attempts = unique_attempts
    badge.progress = progress
    db.session.commit()

    # Check eligibility - NEW LOGIC: Each round must have 90% accuracy
    if rounds_with_90_percent < MIN_ATTEMPTS_REQUIRED:
        rounds_needed = MIN_ATTEMPTS_REQUIRED - rounds_with_90_percent
        
        # Find which rounds don't meet 90% requirement
        failing_rounds = [rd for rd in round_details if rd['accuracy'] < REQUIRED_ACCURACY_PER_ROUND or rd['total'] < 10]
        
        if failing_rounds:
            failing_info = ", ".join([f"Round {rd['attempt']} ({rd['accuracy']*100:.0f}%)" for rd in failing_rounds])
            return {
                "badge_claimable": False,
                "reason": f"You need {rounds_needed} more round(s) with at least 90% accuracy. Currently, you have {rounds_with_90_percent} qualifying rounds. Rounds that need improvement: {failing_info}. Each round requires 90% accuracy to count toward the badge."
            }
        else:
            return {
                "badge_claimable": False,
                "reason": f"Complete {rounds_needed} more round(s) with at least 90% accuracy to earn this badge! You've completed {rounds_with_90_percent} out of {MIN_ATTEMPTS_REQUIRED} required rounds. Each round must have at least 90% accuracy."
            }

    # Check if badge is already claimed to avoid repetitive messages
    if badge.claimed:
        return {
            "badge_claimable": False,
            "reason": "Badge already claimed! Great job!"
        }
    else:
        return {
            "badge_claimable": True,
            "reason": "All conditions met! You can now claim your badge."
        }


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
    
    # Normalize stage name to match badge checking logic
    stage = stage.strip().lower()
    stage_normalization = {
        "preconception care": "preconception",
        "preconception": "preconception",
        "antenatal care": "prenatal",
        "prenatal": "prenatal",
        "birth and delivery": "birth_and_delivery",
        "birth": "birth_and_delivery",
        "postnatal care": "postnatal",
        "postnatal": "postnatal"
    }
    stage = stage_normalization.get(stage, stage)

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

        # Step 2: Calculate attempt number for this stage
        existing_responses = UserResponse.query.filter_by(user_id=user_id, stage=stage).all()
        if existing_responses:
            # Get the highest attempt number and check if we need to clear session for new round
            max_attempt = max(r.attempt_number for r in existing_responses)
            # Count responses for the current attempt (last attempt)
            current_attempt_responses = [r for r in existing_responses if r.attempt_number == max_attempt]
            
            # If the last attempt has 10 responses (this will be the 11th question), start new round
            # Note: When submitting the 10th question, current_attempt_responses has 9 (not yet saved)
            # So questions 1-10 are in attempt 1, question 11+ starts attempt 2
            if len(current_attempt_responses) >= 10:
                # This is the 11th+ question in this round, start new round and clear session
                from chatbot.optimized_modelintegration import clear_stage_session
                clear_stage_session(stage, user_id)
                attempt_number = max_attempt + 1
                print(f"Debug - Starting new round {attempt_number}, cleared session for {stage}")
            else:
                attempt_number = max_attempt  # Continue in current round
        else:
            attempt_number = 1  # First question ever
        
        # Step 3: Save the user response
        user_response = UserResponse(
            user_id=user_id,
            question_id=question_id,
            selected_option=selected_option,
            is_correct=is_correct,
            stage=stage,
            attempt_number=attempt_number
        )
        db.session.add(user_response)
        
        # Step 4: Record question attempt for adaptive learning
        try:
            record_question_attempt(
                user_id=user_id,
                stage=stage,
                question_text=question_text,
                is_correct=is_correct,
                difficulty_level=1  # Default difficulty, can be enhanced later
            )
        except Exception as e:
            print(f"Warning: Failed to record question attempt: {e}")
            # Continue without failing the main response
        
        db.session.commit()

        # Step 5: Call check_and_award_badge function to award badge if criteria met
        result = check_and_award_badge(user_id, stage)  # Check if the user meets the badge criteria

        return jsonify({"success": True, "message": result.get('reason', 'Response saved successfully')})

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to save response: {str(e)}"}), 500


from flask import session, redirect, url_for, jsonify

@quiz_bp.route('/claim_badge/<badge_name>', methods=['POST'])
def claim_badge(badge_name):
    try:
        if 'user_ID' not in session:
            return jsonify({"success": False, "message": "User not logged in."})

        user_id = session['user_ID']
        
        badge_name = badge_name.strip().lower()
        badge_to_stage = {
            "preconception care": "preconception",
            "antenatal care": "antenatal",
            "antenatal": "antenatal",
            "birth & delivery": "birth_and_delivery",
            "postnatal care": "postnatal"
        }
        badge_name = badge_to_stage.get(badge_name, badge_name)

        print(f"Debug - claim_badge: user_id={user_id}, original_badge_name={badge_name}, mapped_badge_name={badge_name}")
        
        badge = Badge.query.filter_by(user_ID=user_id, badge_name=badge_name).first()

        # Debugging output: check the badge status
        print(f"Debug - claim_badge: user_id={user_id}, badge_name={badge_name}")
        if badge:
            print(f"Debug - Badge already exists. Claimed: {badge.claimed}")
        else:
            print(f"Debug - Badge not found in database.")
        
        # If badge already exists and is claimed, just return that
        if badge and badge.claimed:
            return jsonify({
                "success": False,
                "message": "🎉 Congratulations! You've already earned this badge! Keep up the great work!",
                "score": badge.score,
                "progress": badge.progress,
                "attempts": badge.number_of_attempts,
                "claimed": True
            })

        # Only then run the eligibility logic
        result = check_and_award_badge(user_id, badge_name)
        
        # Debugging output: check eligibility result
        print(f"Debug - Eligibility result from check_and_award_badge: {result}")
        
        if not result["badge_claimable"]:
            return jsonify({"success": False, "message": result['reason']})

        # At this point, badge must be eligible and not yet claimed
        if badge:
            try:
                badge.claimed = True
                db.session.commit()
                return jsonify({
                    "success": True,
                    "message": "Badge claimed successfully!",
                    "score": badge.score,
                    "progress": badge.progress,
                    "attempts": badge.number_of_attempts,
                    "claimed": badge.claimed
                })
            except Exception as e:
                print(f"Error claiming badge: {e}")
                db.session.rollback()
                return jsonify({"success": False, "message": f"Database error: {str(e)}"})
        else:
            print(f"Badge not found: {badge_name} for user {user_id}")
            return jsonify({"success": False, "message": "Badge not found. Please complete the stage requirements first."})
    
    except Exception as e:
        print(f"Unexpected error in claim_badge: {e}")
        return jsonify({"success": False, "message": f"Unexpected error: {str(e)}"})

@quiz_bp.route('/learning_insights/<stage>', methods=['GET'])
def get_learning_insights_route(stage):
    """Get learning insights for a specific stage"""
    try:
        if 'user_ID' not in session:
            return jsonify({'error': 'User not logged in'}), 401
        
        user_id = session['user_ID']
        insights = get_learning_insights(user_id, stage)
        
        return jsonify(insights)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@quiz_bp.route('/performance_stats', methods=['GET'])
def get_performance_stats_route():
    """Get performance statistics for question generation"""
    try:
        stats = get_performance_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@quiz_bp.route("/reset_stage/<stage>", methods=["POST"])
def reset_stage(stage):
    """Reset a stage to start fresh with new questions"""
    user_id = session.get("user_ID", "guest_user")
    
    try:
        # Reset the stage questions and cache
        reset_stage_questions(stage, user_id)
        
        return jsonify({
            "success": True,
            "message": f"Stage {stage} has been reset successfully",
            "stage": stage
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to reset stage: {str(e)}"
        }), 500

@quiz_bp.route("/clear_stage_session/<stage>", methods=["POST"])
def clear_stage_session_endpoint(stage):
    """Clear session data for a specific stage"""
    user_id = session.get("user_ID", "guest_user")
    
    try:
        clear_stage_session(stage, user_id)
        
        return jsonify({
            "success": True,
            "message": f"Session cleared for stage {stage}",
            "stage": stage
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to clear stage session: {str(e)}"
        }), 500

@quiz_bp.route("/get_fresh_questions/<stage>", methods=["GET"])
def get_fresh_questions(stage):
    """Get completely fresh questions for a stage (force new generation)"""
    user_id = session.get("user_ID", "guest_user")
    
    # Normalize stage name - frontend may send "birth_and_delivery" but get_hybrid_questions expects "birth"
    # This matches the normalization in other routes (get_quiz_birth uses "birth", not "birth_and_delivery")
    stage_normalization = {
        "birth_and_delivery": "birth",  # Convert frontend format to backend format
        "birth": "birth",  # Already correct
        "preconception": "preconception",
        "prenatal": "prenatal",
        "postnatal": "postnatal"
    }
    normalized_stage = stage_normalization.get(stage.lower(), stage)
    
    try:
        # Use optimized hybrid questions with force_new=True to reset session and get fresh questions
        # This is much faster than hybrid_ai_service which uses the slow 405B model
        questions = get_hybrid_questions(normalized_stage, user_id, difficulty_level=1, force_new=True)
        
        # Ensure we have a list of questions
        if not isinstance(questions, list) or len(questions) == 0:
            # Fallback to instant questions if hybrid fails
            from chatbot.optimized_modelintegration import get_instant_questions
            questions = get_instant_questions(normalized_stage, 10)
            
            if isinstance(questions, list) and len(questions) > 0:
                return jsonify({
                    "success": True,
                    "questions": questions,
                    "count": len(questions),
                    "stage": stage
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "No questions available",
                    "stage": stage
                }), 404
        
        return jsonify({
            "success": True,
            "questions": questions,
            "count": len(questions),
            "stage": stage
        })
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to get fresh questions: {str(e)}",
            "stage": stage
        }), 500
