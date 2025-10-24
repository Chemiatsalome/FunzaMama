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
        # Use hybrid AI service with correct fallback order: Together API -> Hugging Face -> Fallback
        from chatbot.hybrid_ai_service import get_hybrid_service
        hybrid_service = get_hybrid_service("together")  # Together API first for reliability
        
        # Generate quiz questions using hybrid service
        quiz_result = hybrid_service.generate_quiz_questions("preconception", user_id)
        
        if isinstance(quiz_result, list) and len(quiz_result) > 0:
            quiz = quiz_result
        else:
            # Fallback to instant questions if hybrid service fails
            from chatbot.optimized_modelintegration import get_instant_questions
            quiz = get_instant_questions("preconception", 10)
        
        # Track questions in session to prevent repetition
        for question in quiz:
            track_session_question("preconception", user_id, question.get('question', ''))
        
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
        # Use hybrid AI service with correct fallback order: Together API -> Hugging Face -> Fallback
        from chatbot.hybrid_ai_service import get_hybrid_service
        hybrid_service = get_hybrid_service("together")  # Together API first for reliability
        
        # Generate quiz questions using hybrid service
        quiz_result = hybrid_service.generate_quiz_questions("prenatal", user_id)
        
        if isinstance(quiz_result, list) and len(quiz_result) > 0:
            quiz = quiz_result
        else:
            # Fallback to instant questions if hybrid service fails
            from chatbot.optimized_modelintegration import get_instant_questions
            quiz = get_instant_questions("prenatal", 10)
        
        # Track questions in session to prevent repetition
        for question in quiz:
            track_session_question("prenatal", user_id, question.get('question', ''))
        
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
        # Use hybrid AI service with correct fallback order: Together API -> Hugging Face -> Fallback
        from chatbot.hybrid_ai_service import get_hybrid_service
        hybrid_service = get_hybrid_service("together")  # Together API first for reliability
        
        # Generate quiz questions using hybrid service
        quiz_result = hybrid_service.generate_quiz_questions("birth", user_id)
        
        if isinstance(quiz_result, list) and len(quiz_result) > 0:
            quiz = quiz_result
        else:
            # Fallback to instant questions if hybrid service fails
            from chatbot.optimized_modelintegration import get_instant_questions
            quiz = get_instant_questions("birth", 10)
        
        # Track questions in session to prevent repetition
        for question in quiz:
            track_session_question("birth", user_id, question.get('question', ''))
        
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
        # Use hybrid AI service with correct fallback order: Together API -> Hugging Face -> Fallback
        from chatbot.hybrid_ai_service import get_hybrid_service
        hybrid_service = get_hybrid_service("together")  # Together API first for reliability
        
        # Generate quiz questions using hybrid service
        quiz_result = hybrid_service.generate_quiz_questions("postnatal", user_id)
        
        if isinstance(quiz_result, list) and len(quiz_result) > 0:
            quiz = quiz_result
        else:
            # Fallback to instant questions if hybrid service fails
            from chatbot.optimized_modelintegration import get_instant_questions
            quiz = get_instant_questions("postnatal", 10)
        
        # Track questions in session to prevent repetition
        for question in quiz:
            track_session_question("postnatal", user_id, question.get('question', ''))
        
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
    MIN_ATTEMPTS_REQUIRED = 3  # Changed from 30 questions to 3 attempts
    REQUIRED_ACCURACY = 0.8

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
    
    # Calculate correct answers
    correct_answers = sum(1 for r in responses if r.is_correct)
    
    # Calculate accuracy
    accuracy = correct_answers / total_questions_attempted if total_questions_attempted else 0

    # Progress toward badge (based on BOTH attempts AND accuracy)
    # Count unique attempts for this stage
    unique_attempts = len(set(r.attempt_number for r in responses))
    
    # More debugging output
    print(f"Debug - check_and_award_badge: user_id={user_id}, stage={normalized_stage}")
    print(f"Debug - Total Questions Attempted: {total_questions_attempted}")
    print(f"Debug - Correct Answers: {correct_answers}")
    print(f"Debug - Accuracy: {accuracy*100:.2f}%")
    print(f"Debug - Unique Attempts: {unique_attempts}")
    print(f"Debug - MIN_ATTEMPTS_REQUIRED: {MIN_ATTEMPTS_REQUIRED}")
    print(f"Debug - REQUIRED_ACCURACY: {REQUIRED_ACCURACY}")
    
    # Calculate progress more logically:
    # - If both requirements are met: 100%
    # - If only attempts met: 50% + (accuracy/required_accuracy) * 25%
    # - If only accuracy met: (attempts/required_attempts) * 25% + 50%
    # - If neither met: (attempts/required_attempts) * 25% + (accuracy/required_accuracy) * 25%
    
    attempts_met = unique_attempts >= MIN_ATTEMPTS_REQUIRED
    accuracy_met = accuracy >= REQUIRED_ACCURACY
    
    if attempts_met and accuracy_met:
        progress = 100.0  # Both requirements met
    elif attempts_met and not accuracy_met:
        # Attempts met, but accuracy not met
        accuracy_ratio = accuracy / REQUIRED_ACCURACY
        progress = 50.0 + (accuracy_ratio * 25.0)  # 50% + up to 25% for accuracy
    elif not attempts_met and accuracy_met:
        # Accuracy met, but attempts not met
        attempts_ratio = unique_attempts / MIN_ATTEMPTS_REQUIRED
        progress = (attempts_ratio * 25.0) + 50.0  # up to 25% for attempts + 50% for accuracy
    else:
        # Neither requirement met
        attempts_ratio = unique_attempts / MIN_ATTEMPTS_REQUIRED
        accuracy_ratio = accuracy / REQUIRED_ACCURACY
        progress = (attempts_ratio * 25.0) + (accuracy_ratio * 25.0)  # up to 50% total
    
    progress = round(progress, 1)
    
    # Debug progress calculation
    print(f"Debug - Attempts Met: {attempts_met} ({unique_attempts}/{MIN_ATTEMPTS_REQUIRED})")
    print(f"Debug - Accuracy Met: {accuracy_met} ({accuracy*100:.1f}%/{REQUIRED_ACCURACY*100:.1f}%)")
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

    # Check eligibility
    if unique_attempts < MIN_ATTEMPTS_REQUIRED:
        attempts_needed = MIN_ATTEMPTS_REQUIRED - unique_attempts
        return {
            "badge_claimable": False,
            "reason": f"Complete {attempts_needed} more attempts to earn this badge! You've completed {unique_attempts} out of {MIN_ATTEMPTS_REQUIRED} required attempts."
        }

    if accuracy < REQUIRED_ACCURACY:
        current_accuracy = round(accuracy * 100, 1)
        required_accuracy = int(REQUIRED_ACCURACY * 100)
        return {
            "badge_claimable": False,
            "reason": f"Improve your accuracy to earn this badge! Your current accuracy is {current_accuracy}%, but you need at least {required_accuracy}%. Keep practicing to improve your score!"
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
        attempt_number = len(set(r.attempt_number for r in existing_responses)) + 1
        
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
    
    try:
        # Use hybrid AI service with correct fallback order: Together API -> Hugging Face -> Fallback
        from chatbot.hybrid_ai_service import get_hybrid_service
        hybrid_service = get_hybrid_service("together")  # Together API first for reliability
        
        # Generate fresh quiz questions using hybrid service
        quiz_result = hybrid_service.generate_quiz_questions(stage, user_id)
        
        if isinstance(quiz_result, list) and len(quiz_result) > 0:
            questions = quiz_result
            
            # Track questions in session to prevent repetition
            for question in questions:
                track_session_question(stage, user_id, question.get('question', ''))
            
            return jsonify({
                "success": True,
                "questions": questions,
                "count": len(questions),
                "stage": stage
            })
        else:
            # Fallback to instant questions if hybrid service fails
            from chatbot.optimized_modelintegration import get_instant_questions
            questions = get_instant_questions(stage, 10)
            
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
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to get fresh questions: {str(e)}",
            "stage": stage
        }), 500
