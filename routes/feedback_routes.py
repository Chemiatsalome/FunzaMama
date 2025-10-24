from flask import Blueprint, request, jsonify, current_app
from models import db
from models.models import Feedback
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime

feedback_bp = Blueprint("feedback", __name__)

# Allowed file extensions for screenshots
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@feedback_bp.route("/api/feedback", methods=["POST"])
def submit_feedback():
    """Submit user feedback"""
    try:
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        category = request.form.get('category')
        message = request.form.get('message')
        
        # Validate required fields
        if not all([name, email, category, message]):
            return jsonify({
                "success": False,
                "error": "All required fields must be filled"
            }), 400
        
        # Validate category
        valid_categories = ['bug', 'feature', 'content', 'ui', 'performance', 'other']
        if category not in valid_categories:
            return jsonify({
                "success": False,
                "error": "Invalid category"
            }), 400
        
        # Handle screenshot upload
        screenshot_path = None
        if 'screenshot' in request.files:
            file = request.files['screenshot']
            if file and file.filename and allowed_file(file.filename):
                # Generate unique filename
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                
                # Create uploads directory if it doesn't exist
                upload_dir = os.path.join(current_app.static_folder, 'uploads', 'feedback')
                os.makedirs(upload_dir, exist_ok=True)
                
                # Save file
                file_path = os.path.join(upload_dir, unique_filename)
                file.save(file_path)
                screenshot_path = f"uploads/feedback/{unique_filename}"
        
        # Create feedback record
        feedback = Feedback(
            user_name=name,
            email=email,
            category=category,
            message=message,
            screenshot_path=screenshot_path,
            status='pending'
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Feedback submitted successfully",
            "feedback_id": feedback.id
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": f"Failed to submit feedback: {str(e)}"
        }), 500

@feedback_bp.route("/api/feedback/<int:feedback_id>", methods=["GET"])
def get_feedback(feedback_id):
    """Get specific feedback by ID"""
    try:
        feedback = Feedback.query.get(feedback_id)
        if not feedback:
            return jsonify({
                "success": False,
                "error": "Feedback not found"
            }), 404
        
        return jsonify({
            "success": True,
            "feedback": {
                "id": feedback.id,
                "user_name": feedback.user_name,
                "email": feedback.email,
                "category": feedback.category,
                "message": feedback.message,
                "status": feedback.status,
                "admin_reply": feedback.admin_reply,
                "screenshot_path": feedback.screenshot_path,
                "created_at": feedback.created_at.isoformat()
            }
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to get feedback: {str(e)}"
        }), 500

@feedback_bp.route("/api/feedback/<int:feedback_id>/reply", methods=["POST"])
def reply_to_feedback(feedback_id):
    """Admin reply to feedback"""
    try:
        data = request.get_json()
        reply = data.get('reply')
        
        if not reply:
            return jsonify({
                "success": False,
                "error": "Reply message is required"
            }), 400
        
        feedback = Feedback.query.get(feedback_id)
        if not feedback:
            return jsonify({
                "success": False,
                "error": "Feedback not found"
            }), 404
        
        feedback.admin_reply = reply
        feedback.status = 'replied'
        feedback.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Reply sent successfully"
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": f"Failed to send reply: {str(e)}"
        }), 500

@feedback_bp.route("/api/feedback/<int:feedback_id>/status", methods=["PUT"])
def update_feedback_status(feedback_id):
    """Update feedback status"""
    try:
        data = request.get_json()
        status = data.get('status')
        
        valid_statuses = ['pending', 'reviewed', 'resolved', 'replied']
        if status not in valid_statuses:
            return jsonify({
                "success": False,
                "error": "Invalid status"
            }), 400
        
        feedback = Feedback.query.get(feedback_id)
        if not feedback:
            return jsonify({
                "success": False,
                "error": "Feedback not found"
            }), 404
        
        feedback.status = status
        feedback.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Status updated successfully"
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": f"Failed to update status: {str(e)}"
        }), 500

@feedback_bp.route("/api/feedback/stats")
def feedback_stats():
    """Get feedback statistics"""
    try:
        total_feedback = Feedback.query.count()
        
        # Count by status
        status_counts = db.session.query(
            Feedback.status,
            db.func.count(Feedback.id)
        ).group_by(Feedback.status).all()
        
        status_stats = {status: count for status, count in status_counts}
        
        # Count by category
        category_counts = db.session.query(
            Feedback.category,
            db.func.count(Feedback.id)
        ).group_by(Feedback.category).all()
        
        category_stats = {category: count for category, count in category_counts}
        
        # Recent feedback (last 7 days)
        from datetime import timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_feedback = Feedback.query.filter(
            Feedback.created_at >= week_ago
        ).count()
        
        return jsonify({
            "success": True,
            "stats": {
                "total": total_feedback,
                "by_status": status_stats,
                "by_category": category_stats,
                "recent_week": recent_feedback
            }
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Failed to get feedback stats: {str(e)}"
        }), 500
