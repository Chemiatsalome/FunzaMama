import re  # Import regular expressions for password validation
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from models import db
from models.models import User
from utils.email_service import EmailService
from datetime import datetime, timedelta


#Define Blueprints
Login_bp = Blueprint("login", __name__)
signup_bp = Blueprint("signup", __name__)


# Password validation function
def is_strong_password(password):
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not re.search(r'[A-Z]', password):
        return "Password must contain at least one uppercase letter."
    if not re.search(r'[a-z]', password):
        return "Password must contain at least one lowercase letter."
    if not re.search(r'[0-9]', password):
        return "Password must contain at least one number."
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return "Password must contain at least one special character."
    return None  # Password is strong

#Signup Functionality
@signup_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        Uname = request.form.get('Uname')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        age = request.form.get('age')
        gender = request.form.get('gender')
        avatar_path = request.form.get('avatar')  # Get the selected avatar path

        # Validate inputs
        if not (fname and lname and Uname and email and password and confirm_password and age and gender):
            flash('All fields are required.', 'danger')
            return redirect(url_for('signup.signup'))
        
        # Validate age
        try:
            age = int(age)
            if age < 13 or age > 100:
                flash('Age must be between 13 and 100.', 'danger')
                return redirect(url_for('signup.signup'))
        except ValueError:
            flash('Please enter a valid age.', 'danger')
            return redirect(url_for('signup.signup'))
        
        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('signup.signup'))
        
        # Check password strength
        password_error = is_strong_password(password)
        if password_error:
            flash(password_error, 'danger')
            return redirect(url_for('signup.signup'))
        
        # Check if username exists
        existing_user = User.query.filter_by(username=Uname).first()
        if existing_user:
            flash('Username already registered. Please login.', 'warning')
            return redirect(url_for('signup.signup'))

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please login.', 'warning')
            return redirect(url_for('signup.signup'))

        # Hash the password before storing it
        hashed_password = generate_password_hash(password)

        # Generate email verification token
        email_service = EmailService()
        verification_token = email_service.generate_verification_token()
        
        # Create new user and assign the selected avatar
        new_user = User(
            first_name=fname, 
            second_name=lname, 
            username=Uname, 
            email=email, 
            password_hash=hashed_password, 
            avatar=avatar_path,
            age=age,
            gender=gender,
            email_verified=False,
            email_verification_token=verification_token
        )
        db.session.add(new_user)
        db.session.commit()

        # Send verification email
        if email_service.send_verification_email(email, f"{fname} {lname}", verification_token):
            flash('Registration successful! Please check your email to verify your account before logging in.', 'success')
        else:
            # For development: auto-verify users if email is not configured
            new_user.email_verified = True
            new_user.email_verification_token = None
            db.session.commit()
            flash('Registration successful! Email verification is not configured, so your account has been automatically verified. You can now log in.', 'success')
        
        return redirect(url_for('login.login'))

    return render_template('signup.html')


#Login Functionality 
@Login_bp.route('/login' , methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        

        # Check if user exists
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            # Check if email is verified
            if not user.email_verified:
                flash('Please verify your email before logging in. Check your inbox for a verification link.', 'warning')
                return redirect(url_for('login.login'))
            
            # Update last login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Store session data
            session['user_ID'] = user.user_ID
            session['email'] = user.email
            session['username'] = user.username 
        
            print(f"User ID stored in session: {session['user_ID']}")  # Debugging line


            flash('Login successful! Welcome back.', 'success')
            print("Session contents:", session)

            # Redirect based on user role
            if user.is_admin():
                return redirect(url_for('admin.admin_dashboard'))  # Redirect admins to admin dashboard
            else:
                return redirect(url_for('gamestages.game'))  # Redirect regular users to game stages
        else:
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('login.login'))  # Stay on login page if failed

    return render_template('login.html')

#Logout Functionlaity
@Login_bp.route('/logout')
def logout():
    session.pop('user_ID', None)  # Remove user session
    session.pop('email', None)  # Remove email from session (optional)
    
    # Clear all existing flash messages before adding logout message
    from flask import get_flashed_messages
    get_flashed_messages()  # This clears all flash messages
    
    flash('You have been logged out.', 'success')
    return redirect(url_for('login.login'))  # Redirect to login page after logout

# Email Verification Routes
@signup_bp.route('/verify-email/<token>')
def verify_email(token):
    """Verify user email with token"""
    try:
        user = User.query.filter_by(email_verification_token=token).first()
        
        if not user:
            flash('Invalid or expired verification link.', 'error')
            return redirect(url_for('login.login'))
        
        # Check if token is not expired (24 hours)
        if user.created_at < datetime.utcnow() - timedelta(hours=24):
            flash('Verification link has expired. Please sign up again.', 'error')
            return redirect(url_for('signup.signup'))
        
        # Verify the user
        user.email_verified = True
        user.email_verification_token = None  # Clear the token
        db.session.commit()
        
        flash('Email verified successfully! You can now log in.', 'success')
        return redirect(url_for('login.login'))
    
    except Exception as e:
        flash('An error occurred during verification. Please try again.', 'error')
        return redirect(url_for('login.login'))

@signup_bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    """Resend verification email"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({"success": False, "error": "Email is required"}), 400
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        if user.email_verified:
            return jsonify({"success": False, "error": "Email already verified"}), 400
        
        # Generate new verification token
        email_service = EmailService()
        new_token = email_service.generate_verification_token()
        
        user.email_verification_token = new_token
        user.created_at = datetime.utcnow()  # Reset the expiration time
        db.session.commit()
        
        # Send verification email
        if email_service.send_verification_email(user.email, f"{user.first_name} {user.second_name}", new_token):
            return jsonify({"success": True, "message": "Verification email sent successfully"})
        else:
            return jsonify({"success": False, "error": "Failed to send verification email"}), 500
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@signup_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle forgot password requests"""
    if request.method == 'GET':
        return render_template('forgot_password.html')
    
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({"success": False, "error": "Email is required"}), 400
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        # Generate password reset token
        email_service = EmailService()
        reset_token = email_service.generate_verification_token()
        
        # Store reset token (you might want to create a separate table for this)
        user.email_verification_token = reset_token  # Reusing the field for reset token
        user.created_at = datetime.utcnow()  # Reset expiration time
        db.session.commit()
        
        # Send password reset email
        if email_service.send_password_reset_email(user.email, f"{user.first_name} {user.second_name}", reset_token):
            return jsonify({"success": True, "message": "Password reset email sent successfully"})
        else:
            return jsonify({"success": False, "error": "Failed to send password reset email"}), 500
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@signup_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset with token"""
    if request.method == 'GET':
        # Verify token
        user = User.query.filter_by(email_verification_token=token).first()
        
        if not user or user.created_at < datetime.utcnow() - timedelta(hours=1):
            flash('Invalid or expired reset link.', 'error')
            return redirect(url_for('login.login'))
        
        return render_template('reset_password.html', token=token)
    
    try:
        data = request.get_json()
        new_password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        if not new_password or not confirm_password:
            return jsonify({"success": False, "error": "All fields are required"}), 400
        
        if new_password != confirm_password:
            return jsonify({"success": False, "error": "Passwords do not match"}), 400
        
        # Validate password strength
        password_error = is_strong_password(new_password)
        if password_error:
            return jsonify({"success": False, "error": password_error}), 400
        
        # Verify token
        user = User.query.filter_by(email_verification_token=token).first()
        if not user or user.created_at < datetime.utcnow() - timedelta(hours=1):
            return jsonify({"success": False, "error": "Invalid or expired reset link"}), 400
        
        # Update password
        user.set_password(new_password)
        user.email_verification_token = None  # Clear the token
        user.email_verified = True  # Mark as verified
        db.session.commit()
        
        return jsonify({"success": True, "message": "Password reset successfully"})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
