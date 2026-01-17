import os
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, session,flash,  jsonify
from chatbot.chatbot import get_chatbot_response  # Import the chatbot function
from models.models import User, Badge, UserResponse
from .gamelogic import check_and_award_badge
from chatbot.modelintergration import get_teaching_facts_by_stage
from datetime import datetime

from models import db

# Intelligent Fallback Response System
def get_intelligent_fallback_response(user_message, current_question="", current_options=None, current_answer=""):
    """Provide intelligent, contextual responses when the main AI service is unavailable"""
    if current_options is None:
        current_options = []
    
    input_lower = user_message.lower()
    
    # General maternal health responses
    maternal_responses = {
        'pregnancy': [
            "Pregnancy is a beautiful journey that requires proper care and attention. Focus on regular checkups, balanced nutrition, and listening to your body.",
            "During pregnancy, your body goes through amazing changes. Stay connected with your healthcare provider and don't hesitate to ask questions.",
            "Prenatal care is essential for a healthy pregnancy. Regular checkups, proper nutrition, and staying active are key components."
        ],
        'nutrition': [
            "Good nutrition during pregnancy is crucial for both you and your baby. Focus on a balanced diet with plenty of fruits, vegetables, and whole grains.",
            "Prenatal vitamins are important, but they don't replace a healthy diet. Include iron-rich foods and stay hydrated.",
            "Eat a variety of foods to ensure you get all the nutrients you and your baby need. Don't forget to take your prenatal vitamins."
        ],
        'exercise': [
            "Regular, moderate exercise is beneficial during pregnancy. Walking, swimming, and prenatal yoga are excellent choices.",
            "Listen to your body and avoid high-impact activities. Always consult your healthcare provider before starting new exercises.",
            "Staying active during pregnancy can help with energy levels, sleep, and preparation for labor."
        ],
        'labor': [
            "Labor is a natural process. Learn about the signs of labor and when to contact your healthcare provider.",
            "Preparation for labor includes understanding the process, practicing breathing techniques, and creating a birth plan.",
            "Every labor experience is unique. Trust your healthcare team and your body's ability to give birth."
        ],
        'postpartum': [
            "The postpartum period is a time of adjustment and healing. Take care of yourself so you can take care of your baby.",
            "Postpartum recovery takes time. Rest when you can, eat nutritious foods, and don't hesitate to ask for help.",
            "Bonding with your baby is important. Skin-to-skin contact and breastfeeding can help establish this connection."
        ]
    }
    
    # Check for specific topics
    if any(word in input_lower for word in ['pregnant', 'pregnancy', 'baby', 'fetus']):
        return maternal_responses['pregnancy'][0]
    elif any(word in input_lower for word in ['nutrition', 'diet', 'food', 'eat', 'vitamin']):
        return maternal_responses['nutrition'][0]
    elif any(word in input_lower for word in ['exercise', 'workout', 'activity', 'fitness']):
        return maternal_responses['exercise'][0]
    elif any(word in input_lower for word in ['labor', 'birth', 'delivery', 'contraction']):
        return maternal_responses['labor'][0]
    elif any(word in input_lower for word in ['postpartum', 'after', 'recovery', 'newborn']):
        return maternal_responses['postpartum'][0]
    
    # If there's a current question context, provide specific help for FAILED QUESTIONS
    if current_question:
        # Check if this is about a failed question (user is asking about the question they just got wrong)
        if current_answer and current_options:
            # This is a failed question - provide helpful explanation
            response = f"I can help you understand '{current_question}'!\n\n"
            response += f"**The correct answer is: {current_answer}**\n\n"
            
            # Provide context-specific help based on question content
            question_lower = current_question.lower()
            if any(word in question_lower for word in ['nutrition', 'diet', 'food', 'vitamin', 'supplement']):
                response += "**Key points about nutrition:**\n"
                response += "• Eat a balanced diet with fruits, vegetables, whole grains, and lean proteins\n"
                response += "• Take prenatal vitamins as recommended by your healthcare provider\n"
                response += "• Stay hydrated by drinking plenty of water\n"
                response += "• Avoid certain foods like raw fish, unpasteurized dairy, and excessive caffeine\n\n"
            elif any(word in question_lower for word in ['exercise', 'activity', 'workout', 'fitness']):
                response += "**Key points about exercise:**\n"
                response += "• Regular moderate exercise is generally safe and beneficial during pregnancy\n"
                response += "• Activities like walking, swimming, and prenatal yoga are excellent choices\n"
                response += "• Listen to your body and stop if you feel pain or discomfort\n"
                response += "• Consult your healthcare provider before starting any new exercise routine\n\n"
            elif any(word in question_lower for word in ['prenatal', 'visit', 'checkup', 'appointment']):
                response += "**Key points about prenatal care:**\n"
                response += "• Regular prenatal visits are essential for monitoring your health and baby's development\n"
                response += "• These visits allow your healthcare provider to detect and address any issues early\n"
                response += "• Bring questions and concerns to each appointment\n"
                response += "• Follow your healthcare provider's recommendations for tests and screenings\n\n"
            elif any(word in question_lower for word in ['labor', 'birth', 'delivery', 'contraction']):
                response += "**Key points about labor and birth:**\n"
                response += "• Know the signs of labor: regular contractions, water breaking, or bloody show\n"
                response += "• Create a birth plan but remain flexible\n"
                response += "• Have a support person ready to accompany you\n"
                response += "• Trust your healthcare team during delivery\n\n"
            else:
                response += "**General guidance:**\n"
                response += "• Always consult your healthcare provider for personalized medical advice\n"
                response += "• Trust reliable sources for maternal health information\n"
                response += "• Every pregnancy is unique - what works for others may not work for you\n"
                response += "• Don't hesitate to ask questions - knowledge empowers you\n\n"
            
            response += "Would you like me to explain any specific aspect of this topic in more detail?"
            return response
        else:
            # General question context without answer
            return f"Based on your question about '{current_question}', here are some key points to consider:\n\n• Regular prenatal care is essential\n• Balanced nutrition supports healthy development\n• Exercise and rest are both important\n• Stay connected with your healthcare provider\n• Trust your instincts and ask questions\n\nRemember, every pregnancy journey is unique. Always consult your healthcare provider for personalized advice."
    
    # Default helpful response
    return "I can help with preconception planning, nutrition, and preparing for a healthy pregnancy. For specific medical concerns, always consult your healthcare provider. What would you like to know more about?" "I'm here to help with your maternal health questions! While I'm experiencing some technical difficulties, I can still provide general guidance. For specific medical concerns, always consult your healthcare provider. What would you like to know about pregnancy, childbirth, or postnatal care?"

home_bp = Blueprint("home", __name__)
gamestages_bp = Blueprint("gamestages", __name__)
profile_bp = Blueprint("profile", __name__)


@home_bp.route('/chat', methods=['GET', 'POST'])
def home():
    username = "Guest"  # Default username
    user = None  # Initialize user to None

    # Check if user is logged in
    if 'user_ID' in session:
        user_id = session['user_ID']
        try:
            user = User.query.get(user_id)
            if user:
                # Use first_name and second_name instead of username
                username = f"{user.first_name} {user.second_name}".strip()
        except Exception as e:
            print(f"Database schema error: {e}")
            # Continue with guest user if there's a schema issue
            user = None
            username = "Guest"

    if request.method == 'POST':  # Chatbot logic
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "Invalid JSON data"}), 400
                
            user_message = data.get('message', '')
            user_role = data.get('user_role', 'Curious Learner')  # Default role
            language = data.get('language', 'English')  # Default language
            
            # Get current question context if provided
            current_question = data.get('current_question', None)
            current_options = data.get('current_options', None)
            current_answer = data.get('current_answer', None)

            if not user_message:
                return jsonify({"error": "Message is required"}), 400

            # Check if hybrid AI service is requested
            use_hybrid = data.get('use_hybrid', False)
            stage = data.get('stage', 'general')
            
            try:
                if use_hybrid:
                    # Use hybrid AI service (Together API main, Hugging Face fallback, then fallback responses)
                    from chatbot.hybrid_ai_service import get_hybrid_service
                    hybrid_service = get_hybrid_service("together")  # Together API first for reliability
                    
                    # Create context for the hybrid service
                    context = {
                        'current_question': current_question,
                        'current_options': current_options,
                        'current_answer': current_answer
                    }
                    
                    # Generate chat response using hybrid service
                    bot_response = hybrid_service.generate_chat_response(user_message, stage, context)
                else:
                    # Use original chatbot with conversation continuity
                    # Pass user_id and session_id for per-user chat history
                    user_id = session.get('user_ID', 'guest_user')
                    session_id = session.get('session_id', None)  # Use session ID if available
                    clear_history = data.get('clear_history', False)  # Allow clearing history for new conversations
                    
                    # Only pass current_question if user is explicitly asking about it
                    # For new questions, don't pass old question context
                    bot_response = get_chatbot_response(
                        user_message, 
                        language, 
                        user_role, 
                        current_question if data.get('is_question_context', False) else None,  # Only use if explicitly flagged
                        current_options if data.get('is_question_context', False) else None,
                        current_answer if data.get('is_question_context', False) else None,
                        user_id=user_id,
                        session_id=session_id,
                        clear_history=clear_history
                    )
                
                # Check if the response indicates rate limiting
                if bot_response and ("high demand" in bot_response.lower() or "rate limit" in bot_response.lower()):
                    print("Rate limit detected, switching to fallback chatbot")
                    # Use intelligent fallback but with the NEW user message, not old question
                    bot_response = get_intelligent_fallback_response(user_message, None, None, None)  # Don't use old question context
                    
            except Exception as chatbot_error:
                import traceback
                print(f"Chatbot function error: {chatbot_error}")
                print(f"Traceback: {traceback.format_exc()}")
                # Check if it's a rate limit error
                if "rate" in str(chatbot_error).lower() or "limit" in str(chatbot_error).lower() or "quota" in str(chatbot_error).lower():
                    print("Rate limit detected in exception, using fallback")
                    # Use intelligent fallback but with the NEW user message, not old question
                    bot_response = get_intelligent_fallback_response(user_message, None, None, None)  # Don't use old question context
                else:
                    # Other error fallback - use intelligent fallback with NEW message only
                    # Don't use current_question for new questions - it causes confusion
                    bot_response = get_intelligent_fallback_response(user_message, None, None, None)
            
            return jsonify({"response": bot_response})
            
        except Exception as e:
            print(f"Chatbot route error: {e}")
            # Use intelligent fallback even for server errors
            bot_response = get_intelligent_fallback_response(user_message, current_question, current_options, current_answer)
            return jsonify({"response": bot_response})

    # For GET request
    user_logged_in = user is not None
    return render_template('index.html', user=user, username=username, user_logged_in=user_logged_in)


@home_bp.route('/', methods=['GET'])
def index():
    username = "Guest"  # Default username
    user = None  # Initialize user to None

    # Check if user is logged in
    if 'user_ID' in session:
        user_id = session['user_ID']
        try:
            user = User.query.get(user_id)
            if user:
                # Use first_name and second_name instead of username
                username = f"{user.first_name} {user.second_name}".strip()
        except Exception as e:
            print(f"Database schema error: {e}")
            # Continue with guest user if there's a schema issue
            user = None
            username = "Guest"

    user_logged_in = user is not None
    print(f"Debug - Home route: user_logged_in={user_logged_in}, user={user}, session_user_ID={session.get('user_ID', 'None')}")
    return render_template('index.html', user=user, username=username, user_logged_in=user_logged_in)

def update_badge_progress(user_id, stage):
    responses = UserResponse.query.filter_by(user_id=user_id, stage=stage).all()
    attempts = len(responses)
    correct = sum(1 for r in responses if r.is_correct)
    accuracy = (correct / attempts) if attempts > 0 else 0

    badge = Badge.query.filter_by(user_ID=user_id, badge_name=stage).first()
    if not badge:
        badge = Badge(user_ID=user_id, badge_name=stage)

    badge.score = correct
    badge.progress = round(accuracy * 100, 2)
    badge.number_of_attempts = attempts // 10  # Adjust based on your design

    db.session.add(badge)
    db.session.commit()

def update_badge_progress(user_id, stage):
    MIN_QUESTIONS_REQUIRED = 30
    REQUIRED_ACCURACY = 0.8

    responses = UserResponse.query.filter_by(user_id=user_id, stage=stage).all()
    attempts = len(responses)
    correct = sum(1 for r in responses if r.is_correct)
    accuracy = (correct / attempts) if attempts > 0 else 0

    # Composite progress calculation
    attempt_score = min(attempts / MIN_QUESTIONS_REQUIRED, 1)
    accuracy_score = min(accuracy / REQUIRED_ACCURACY, 1)
    composite_progress = round((0.5 * attempt_score + 0.5 * accuracy_score) * 100, 2)

    # Fetch or create badge
    badge = Badge.query.filter_by(user_ID=user_id, badge_name=stage).first()
    if not badge:
        badge = Badge(user_ID=user_id, badge_name=stage)

    badge.score = correct
    badge.number_of_attempts = attempts
    badge.progress = composite_progress

    db.session.add(badge)
    db.session.commit()


@gamestages_bp.route('/gamestages')
def game():
    # print("Route accessed")  # Debug output commented out
    username = "Guest"
    earned_stages = []
    badge_claimable = {}
    selected_badge = request.args.get('badge')  # e.g. 'preconception'
    total_stages = 4

    if 'user_ID' in session:
        user_id = session['user_ID']
        try:
            user = User.query.get(user_id)

            if user:
                # Use first_name and second_name instead of username
                username = f"{user.first_name} {user.second_name}".strip()

                # ✅ Update badge progress for all 4 stages
                for stage in ['preconception', 'antenatal', 'birth_and_delivery', 'postnatal']:
                    update_badge_progress(user_id, stage)

                # ✅ Now fetch updated badges
                earned_badges = Badge.query.filter_by(user_ID=user_id).all()
                # Only consider badges as "earned" if they can actually be claimed (progress = 100%)
                # Use the calculated progress instead of database progress
                earned_stages = []
                for badge in earned_badges:
                    # Recalculate progress for this badge
                    responses = UserResponse.query.filter_by(user_id=user_id, stage=badge.badge_name).all()
                    if responses:
                        total_questions = len(responses)
                        correct_answers = sum(1 for r in responses if r.is_correct)
                        accuracy = correct_answers / total_questions if total_questions else 0
                        unique_attempts = len(set(r.attempt_number for r in responses))
                        
                        # Calculate progress using the same logic
                        MIN_ATTEMPTS_REQUIRED = 3
                        REQUIRED_ACCURACY = 0.8
                        
                        attempts_met = unique_attempts >= MIN_ATTEMPTS_REQUIRED
                        accuracy_met = accuracy >= REQUIRED_ACCURACY
                        
                        if attempts_met and accuracy_met:
                            calculated_progress = 100.0
                        elif attempts_met and not accuracy_met:
                            accuracy_ratio = accuracy / REQUIRED_ACCURACY
                            calculated_progress = 50.0 + (accuracy_ratio * 25.0)
                        elif not attempts_met and accuracy_met:
                            attempts_ratio = unique_attempts / MIN_ATTEMPTS_REQUIRED
                            calculated_progress = (attempts_ratio * 25.0) + 50.0
                        else:
                            attempts_ratio = unique_attempts / MIN_ATTEMPTS_REQUIRED
                            accuracy_ratio = accuracy / REQUIRED_ACCURACY
                            calculated_progress = (attempts_ratio * 25.0) + (accuracy_ratio * 25.0)
                        
                        if calculated_progress >= 100.0:
                            earned_stages.append(badge.badge_name)
                
                # Determine which badges are claimable (ready to claim but not yet earned)
                badge_claimable = {}
                for badge in earned_badges:
                    if badge.badge_name not in earned_stages:
                        # Badge is claimable if it has significant progress (>= 80%)
                        badge_claimable[badge.badge_name] = badge.progress >= 80.0
        except Exception as e:
            print(f"Database schema error in game(): {e}")
            # Continue with guest user if there's a schema issue
            user = None
            username = "Guest"

    # Calculate progress for logged-in users
    if 'user_ID' in session and user:
        try:
            # ✅ Calculate progress based on earned badges (progress >= 100%)
            # Count how many badges are actually earned (can be claimed)
            earned_badge_count = sum(1 for badge in earned_badges if badge.progress >= 100.0)
            overall_progress = round((earned_badge_count / total_stages) * 100, 1)
            
            # print(f"Debug - Earned badges: {earned_badge_count}/{total_stages}")  # Debug output commented out
            # print(f"Debug - Overall progress: {overall_progress}%")  # Debug output commented out

            # ✅ Build badge_data dictionary with detailed progress info
            badge_data = {}
            for badge in earned_badges:
                # Get detailed stats for this badge
                responses = UserResponse.query.filter_by(user_id=user_id, stage=badge.badge_name).all()
                total_questions = len(responses)
                correct_answers = sum(1 for r in responses if r.is_correct)
                accuracy = correct_answers / total_questions if total_questions else 0
                unique_attempts = len(set(r.attempt_number for r in responses))
                
                # Calculate progress breakdown using the same logic as check_and_award_badge
                MIN_ATTEMPTS_REQUIRED = 3
                REQUIRED_ACCURACY = 0.8
                
                attempts_met = unique_attempts >= MIN_ATTEMPTS_REQUIRED
                accuracy_met = accuracy >= REQUIRED_ACCURACY
                
                if attempts_met and accuracy_met:
                    attempts_progress = 50.0
                    accuracy_progress = 50.0
                elif attempts_met and not accuracy_met:
                    attempts_progress = 50.0
                    accuracy_ratio = accuracy / REQUIRED_ACCURACY
                    accuracy_progress = accuracy_ratio * 25.0
                elif not attempts_met and accuracy_met:
                    attempts_ratio = unique_attempts / MIN_ATTEMPTS_REQUIRED
                    attempts_progress = attempts_ratio * 25.0
                    accuracy_progress = 50.0
                else:
                    attempts_ratio = unique_attempts / MIN_ATTEMPTS_REQUIRED
                    accuracy_ratio = accuracy / REQUIRED_ACCURACY
                    attempts_progress = attempts_ratio * 25.0
                    accuracy_progress = accuracy_ratio * 25.0
                
                # Calculate the correct progress using the new logic
                if attempts_met and accuracy_met:
                    calculated_progress = 100.0
                elif attempts_met and not accuracy_met:
                    calculated_progress = 50.0 + (accuracy_ratio * 25.0)
                elif not attempts_met and accuracy_met:
                    calculated_progress = (attempts_ratio * 25.0) + 50.0
                else:
                    calculated_progress = (attempts_ratio * 25.0) + (accuracy_ratio * 25.0)
                
                calculated_progress = round(calculated_progress, 1)
                
                badge_data[badge.badge_name] = {
                    'score': badge.score,
                    'progress': calculated_progress,  # Use calculated progress instead of database progress
                    'attempts': badge.number_of_attempts,
                    'claimed': badge.claimed,
                    'total_questions': total_questions,
                    'correct_answers': correct_answers,
                    'accuracy': round(accuracy * 100, 1),
                    'attempts_progress': round(attempts_progress, 1),
                    'accuracy_progress': round(accuracy_progress, 1)
                }

            selected_badge_data = badge_data.get(selected_badge) if selected_badge else None

            # ✅ Debug print statements (commented out)
            # print("USERNAME:", username)  # Debug output commented out
            # print("EARNED STAGES:", earned_stages)  # Debug output commented out
            # print("BADGE DATA:", badge_data)  # Debug output commented out
            # print("SELECTED BADGE:", selected_badge)  # Debug output commented out
            # print("SELECTED BADGE DATA:", selected_badge_data)  # Debug output commented out
            # print("OVERALL PROGRESS:", overall_progress)  # Debug output commented out

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
        except Exception as e:
            print(f"Error calculating progress: {e}")
            # Fall back to guest mode
            pass

    # Guest user or error fallback
    return render_template(
        'gamestages.html',
        user_logged_in=False,
        user=None,
        username=username,
        earned_stages=[],
        badge_claimable={},
        badge_data={},
        selected_badge=None,
        selected_badge_data=None,
        overall_progress=0
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
        # Use first_name and second_name instead of username
        username = f"{user.first_name} {user.second_name}".strip()
        avatar = user.avatar

        # Handle POST request to change username or avatar
        if request.method == 'POST':
            # Handle username update
            if 'username' in request.form:
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
            
            # Handle avatar upload
            if 'avatar_file' in request.files:
                file = request.files['avatar_file']
                if file and file.filename != '':
                    # Validate file type
                    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
                    if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                        # Create uploads directory if it doesn't exist
                        upload_dir = os.path.join('static', 'uploads', 'avatars')
                        os.makedirs(upload_dir, exist_ok=True)
                        
                        # Delete old uploaded avatar if it exists (not predefined)
                        if user.avatar and user.avatar.startswith('uploads/avatars/'):
                            old_path = os.path.join('static', user.avatar)
                            if os.path.exists(old_path):
                                try:
                                    os.remove(old_path)
                                except:
                                    pass  # Ignore errors when deleting old file
                        
                        # Generate unique filename
                        filename = secure_filename(file.filename)
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        filename = f"{user_id}_{timestamp}_{filename}"
                        
                        # Save file
                        file_path = os.path.join(upload_dir, filename)
                        file.save(file_path)
                        
                        # Update user avatar in database
                        user.avatar = f"uploads/avatars/{filename}"
                        db.session.commit()
                        avatar = user.avatar
                        flash('Avatar uploaded successfully!', 'success')
                    else:
                        flash('Invalid file type. Please upload PNG, JPG, JPEG, GIF, or WEBP.', 'warning')
            
            # Handle predefined avatar selection
            if 'avatar' in request.form:
                avatar_path = request.form.get('avatar')
                if avatar_path:
                    # Delete old uploaded avatar if it exists (not predefined)
                    if user.avatar and user.avatar.startswith('uploads/avatars/'):
                        old_path = os.path.join('static', user.avatar)
                        if os.path.exists(old_path):
                            try:
                                os.remove(old_path)
                            except:
                                pass  # Ignore errors when deleting old file
                    
                    user.avatar = avatar_path
                    db.session.commit()
                    avatar = user.avatar
                    flash('Avatar updated successfully!', 'success')

        # Query user responses
        responses = UserResponse.query.filter_by(user_id=user_id).all()

        # Initialize data for stages (using database stage names)
        stage_data = {
            'antenatal': {'correct': 0, 'failed': 0},
            'preconception': {'correct': 0, 'failed': 0},
            'birth_and_delivery': {'correct': 0, 'failed': 0},
            'postnatal': {'correct': 0, 'failed': 0}
        }

        # Count total attempts, correct, and failed answers
        # Group responses by stage and attempt_number to count unique attempts
        stage_attempts = {}
        
        for response in responses:
            stage = response.stage
            attempt_num = response.attempt_number
            
            # Map database stage names to our stage_data keys
            stage_mapping = {
                'prenatal': 'antenatal',  # Map prenatal to antenatal
                'antenatal': 'antenatal',
                'preconception': 'preconception',
                'birth_and_delivery': 'birth_and_delivery',
                'birth': 'birth_and_delivery',  # Map birth to birth_and_delivery
                'postnatal': 'postnatal'
            }
            
            # Get the mapped stage name
            mapped_stage = stage_mapping.get(stage, stage)
            
            # Initialize stage if not exists
            if mapped_stage not in stage_attempts:
                stage_attempts[mapped_stage] = set()
            
            # Add this attempt to the stage
            stage_attempts[mapped_stage].add(attempt_num)
            
            # Count individual responses
            if response.is_correct:
                stats["total_correct"] += 1
                stage_data[mapped_stage]['correct'] += 1
            else:
                stats["total_failed"] += 1
                stage_data[mapped_stage]['failed'] += 1
        
        # Count total unique attempts across all stages
        stats["total_attempted"] = sum(len(attempts) for attempts in stage_attempts.values())
        
        # Debug information
        print(f"Debug - Profile stats for user {user_id}:")
        print(f"  Total responses: {len(responses)}")
        print(f"  Total unique attempts: {stats['total_attempted']}")
        print(f"  Total correct: {stats['total_correct']}")
        print(f"  Total failed: {stats['total_failed']}")
        print(f"  Stage attempts: {stage_attempts}")
        print(f"  Stage data: {stage_data}")

        # Find the leading stage based on the highest number of correct answers
        leading_stage = max(stage_data, key=lambda stage: stage_data[stage]['correct'])
        stats["leading_stage"] = leading_stage.capitalize()

        # Prepare data for individual stages (using correct database stage names)
        stats["stages"] = [
            {
                "name": "Prenatal Care", 
                "correct": stage_data['antenatal']['correct'], 
                "failed": stage_data['antenatal']['failed'],
                "attempts": len(stage_attempts.get('antenatal', set()))
            },
            {
                "name": "Preconception Care", 
                "correct": stage_data['preconception']['correct'], 
                "failed": stage_data['preconception']['failed'],
                "attempts": len(stage_attempts.get('preconception', set()))
            },
            {
                "name": "Labor & Delivery", 
                "correct": stage_data['birth_and_delivery']['correct'], 
                "failed": stage_data['birth_and_delivery']['failed'],
                "attempts": len(stage_attempts.get('birth_and_delivery', set()))
            },
            {
                "name": "Postnatal Care", 
                "correct": stage_data['postnatal']['correct'], 
                "failed": stage_data['postnatal']['failed'],
                "attempts": len(stage_attempts.get('postnatal', set()))
            }
        ]

        # Find the worst-performing stage based on accuracy percentage
        worst_stage = None
        worst_accuracy = 100  # Start with 100% accuracy
        
        for stage, data in stage_data.items():
            total_attempts = data['correct'] + data['failed']
            if total_attempts > 0:  # Only consider stages with attempts
                accuracy = (data['correct'] / total_attempts) * 100
                if accuracy < worst_accuracy:
                    worst_accuracy = accuracy
                    worst_stage = stage
        
        # If no stages have attempts, default to the first stage (use 'antenatal' not 'prenatal')
        if worst_stage is None:
            worst_stage = 'antenatal'  # Changed from 'prenatal' to match stage_data keys
            worst_accuracy = 0

        # Ensure worst_stage exists in stage_data (safety check)
        if worst_stage not in stage_data:
            # Map 'prenatal' to 'antenatal' if needed
            if worst_stage == 'prenatal':
                worst_stage = 'antenatal'
            else:
                # Fallback to first available stage
                worst_stage = list(stage_data.keys())[0] if stage_data else 'antenatal'

        # Get teaching facts from LLaMA model
        teaching_facts = get_teaching_facts_by_stage(worst_stage)

        # Add to stats with more detailed information (with safety check)
        if worst_stage in stage_data:
            stats["most_failed_stage"] = {
                "name": worst_stage.capitalize(),
                "accuracy": round(worst_accuracy, 1),
                "correct": stage_data[worst_stage]['correct'],
                "failed": stage_data[worst_stage]['failed'],
                "total_attempts": stage_data[worst_stage]['correct'] + stage_data[worst_stage]['failed'],
                "facts": teaching_facts
            }
        else:
            # Fallback if stage_data is empty or worst_stage doesn't exist
            stats["most_failed_stage"] = {
                "name": "No Stage",
                "accuracy": 0,
                "correct": 0,
                "failed": 0,
                "total_attempts": 0,
                "facts": []
            }

    # Render the profile page with the dynamic username and stats
    return render_template("profile.html", username=username, stats=stats, avatar=avatar, user=user)
