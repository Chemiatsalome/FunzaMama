from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from models import db
from models.models import User, QuizQuestion, UserResponse, Badge, UserQuestionHistory, Feedback
from sqlalchemy import func, desc, and_
from datetime import datetime, timedelta
import csv
import io
import json

# Try to import reportlab, but don't fail if it's not available
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    reportlab_available = True
except ImportError:
    reportlab_available = False
    print("ReportLab not available. PDF export features will be disabled.")

admin_bp = Blueprint("admin", __name__)

def admin_required(f):
    """Decorator to require admin authentication"""
    def decorated_function(*args, **kwargs):
        # Check if user is logged in and is admin
        if 'user_ID' not in session:
            return redirect(url_for('login.login'))
        
        user = User.query.get(session['user_ID'])
        if not user or not user.is_admin():  # Use role-based check
            return jsonify({"error": "Admin access required"}), 403
        
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route("/admin")
@admin_required
def admin_dashboard():
    """Admin dashboard page"""
    return render_template("admin.html")

@admin_bp.route("/admin/api/dashboard")
@admin_required
def admin_dashboard_data():
    """Get dashboard statistics and data"""
    try:
        # Calculate statistics
        total_users = User.query.count()
        
        # Active users (logged in within last 24 hours)
        yesterday = datetime.now() - timedelta(days=1)
        active_users = User.query.filter(User.last_login >= yesterday).count()
        
        # Total completions (users who completed all stages)
        total_completions = UserResponse.query.filter(
            UserResponse.stage.in_(['preconception', 'antenatal', 'birth', 'postnatal'])
        ).count()
        
        # Average score across all responses (calculate from is_correct field)
        total_responses = UserResponse.query.count()
        correct_responses = UserResponse.query.filter(UserResponse.is_correct == True).count()
        avg_score = round((correct_responses / total_responses * 100) if total_responses > 0 else 0, 1)
        
        # Recent activity (last 10 activities)
        recent_activities = []
        
        # Get recent user registrations
        recent_users = User.query.order_by(desc(User.created_at)).limit(5).all()
        for user in recent_users:
            recent_activities.append({
                'description': f"New user {user.first_name} {user.second_name} registered",
                'timestamp': user.created_at
            })
        
        # Get recent completions
        recent_completions = UserResponse.query.order_by(desc(UserResponse.created_at)).limit(5).all()
        for response in recent_completions:
            user = User.query.get(response.user_id)
            user_name = f"{user.first_name} {user.second_name}" if user else "Unknown User"
            recent_activities.append({
                'description': f"{user_name} completed {response.stage} stage",
                'timestamp': response.created_at
            })
        
        # Sort by timestamp and take last 10
        recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
        recent_activities = recent_activities[:10]
        
        return jsonify({
            "success": True,
            "stats": {
                "totalUsers": total_users,
                "activeUsers": active_users,
                "totalCompletions": total_completions,
                "avgScore": avg_score
            },
            "recentActivity": recent_activities
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route("/admin/api/users")
@admin_required
def admin_users_data():
    """Get users data for admin panel"""
    try:
        users = User.query.all()
        users_data = []
        
        for user in users:
            # Calculate user progress based on core stages only
            core_stages = ['preconception', 'antenatal', 'birth', 'postnatal']
            user_responses = UserResponse.query.filter_by(user_id=user.user_ID).all()
            
            # Count how many core stages the user has attempted
            attempted_stages = set()
            for response in user_responses:
                if response.stage in core_stages:
                    attempted_stages.add(response.stage)
            
            # Calculate progress as percentage of core stages attempted
            progress = round((len(attempted_stages) / len(core_stages)) * 100)
            # Ensure progress never exceeds 100%
            progress = min(progress, 100)
            
            # Get last active time
            last_active = user.last_login or user.created_at
            
            users_data.append({
                "user_ID": user.user_ID,
                "id": user.user_ID,  # Keep both for compatibility
                "name": f"{user.first_name} {user.second_name}",
                "email": user.email,
                "role": user.role or 'user',
                "created_at": user.created_at.isoformat() if user.created_at else "Unknown",
                "progress": progress,
                "last_active": last_active.isoformat() if last_active else "Never"
            })
        
        return jsonify({
            "success": True,
            "users": users_data
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route("/admin/api/analytics")
@admin_required
def admin_analytics_data():
    """Get analytics data for admin panel"""
    try:
        # Calculate knowledge retention rates (average score per stage)
        retention_data = {}
        stages = ['preconception', 'antenatal', 'birth', 'postnatal']
        
        for stage in stages:
            # Get all responses for this stage
            stage_responses = UserResponse.query.filter_by(stage=stage).all()
            
            if stage_responses:
                # Calculate average score for this stage
                correct_count = sum(1 for response in stage_responses if response.is_correct)
                total_count = len(stage_responses)
                avg_score = (correct_count / total_count) * 100 if total_count > 0 else 0
                retention_data[stage] = round(avg_score, 1)
            else:
                retention_data[stage] = 0
        
        # Get leaderboard (top 10 users by average score)
        leaderboard_data = []
        
        # Get all users with their average scores
        users = User.query.filter(User.role != 'admin').all()
        
        for user in users:
            user_responses = UserResponse.query.filter_by(user_id=user.user_ID).all()
            if user_responses:
                correct_count = sum(1 for response in user_responses if response.is_correct)
                avg_score = (correct_count / len(user_responses)) * 100
                
                # Calculate time spent (total responses as proxy for engagement)
                total_time_spent = len(user_responses) * 2  # Assume 2 minutes per question
                
                # Calculate age group
                age_group = "Unknown"
                if user.age:
                    if user.age < 25:
                        age_group = "18-24"
                    elif user.age < 35:
                        age_group = "25-34"
                    elif user.age < 45:
                        age_group = "35-44"
                    elif user.age < 55:
                        age_group = "45-54"
                    else:
                        age_group = "55+"
                
                leaderboard_data.append({
                    "id": user.user_ID,
                    "name": f"{user.first_name} {user.second_name}",
                    "email": user.email,
                    "age": user.age or "Unknown",
                    "age_group": age_group,
                    "gender": user.gender or "Unknown",
                    "score": round(avg_score, 1),
                    "completions": len(user_responses),
                    "time_spent": total_time_spent,
                    "last_active": user.last_login.isoformat() if user.last_login else "Never"
                })
        
        # Sort by score and take top 10
        leaderboard_data.sort(key=lambda x: x['score'], reverse=True)
        leaderboard_data = leaderboard_data[:10]
        
        # Calculate performance by topic (same as retention for now, but could be expanded)
        topic_performance = retention_data.copy()
        
        return jsonify({
            "success": True,
            "retention": retention_data,
            "topic_performance": topic_performance,
            "leaderboard": leaderboard_data
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route("/admin/api/charts/stage-completion")
@admin_required
def admin_stage_completion_data():
    """Get stage completion data for charts"""
    try:
        stages = ['preconception', 'antenatal', 'birth', 'postnatal']
        completion_data = {}
        
        for stage in stages:
            # Get all responses for this stage
            stage_responses = UserResponse.query.filter_by(stage=stage).all()
            
            # Group by user and calculate completion
            user_scores = {}
            for response in stage_responses:
                user_id = response.user_id
                if user_id not in user_scores:
                    user_scores[user_id] = {'total': 0, 'correct': 0}
                user_scores[user_id]['total'] += 1
                if response.is_correct:
                    user_scores[user_id]['correct'] += 1
            
            # Count users who have "completed" the stage (3+ attempts with 60%+ average score)
            completed_users = 0
            for user_id, scores in user_scores.items():
                if scores['total'] >= 3:
                    avg_score = (scores['correct'] / scores['total']) * 100
                    if avg_score >= 60:
                        completed_users += 1
            
            # Count total users (excluding admin)
            total_users = User.query.filter(User.role != 'admin').count()
            
            if total_users > 0:
                completion_rate = round((completed_users / total_users) * 100, 1)
            else:
                completion_rate = 0
                
            completion_data[stage] = completion_rate
        
        # Debug information
        debug_info = {}
        for stage in stages:
            stage_responses = UserResponse.query.filter_by(stage=stage).all()
            
            # Group by user and calculate completion
            user_scores = {}
            for response in stage_responses:
                user_id = response.user_id
                if user_id not in user_scores:
                    user_scores[user_id] = {'total': 0, 'correct': 0}
                user_scores[user_id]['total'] += 1
                if response.is_correct:
                    user_scores[user_id]['correct'] += 1
            
            debug_info[stage] = {
                'total_attempts': len(user_scores),
                'user_details': [
                    {
                        'user_id': user_id,
                        'attempts': scores['total'],
                        'avg_score': round((scores['correct'] / scores['total']) * 100, 1) if scores['total'] > 0 else 0,
                        'completed': scores['total'] >= 3 and (scores['correct'] / scores['total']) * 100 >= 60
                    }
                    for user_id, scores in user_scores.items()
                ]
            }
        
        return jsonify({
            "success": True,
            "data": completion_data,
            "debug": debug_info,
            "total_users": total_users,
            "completion_summary": {
                "preconception": f"{completion_data.get('preconception', 0)}%",
                "antenatal": f"{completion_data.get('antenatal', 0)}%", 
                "birth": f"{completion_data.get('birth', 0)}%",
                "postnatal": f"{completion_data.get('postnatal', 0)}%"
            }
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route("/admin/api/charts/user-growth")
@admin_required
def admin_user_growth_data():
    """Get user growth data for charts"""
    try:
        # Get user registrations for the last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        # Group by week
        weekly_data = {}
        for i in range(4):  # Last 4 weeks
            week_start = thirty_days_ago + timedelta(weeks=i)
            week_end = week_start + timedelta(weeks=1)
            
            week_users = User.query.filter(
                User.created_at >= week_start,
                User.created_at < week_end,
                User.role != 'admin'  # Exclude admin
            ).count()
            
            week_label = f"Week {i+1}"
            weekly_data[week_label] = week_users
        
        return jsonify({
            "success": True,
            "data": weekly_data
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route("/admin/api/feedback")
@admin_required
def admin_feedback_data():
    """Get feedback data for admin panel"""
    try:
        feedback_items = Feedback.query.order_by(desc(Feedback.created_at)).all()
        feedback_data = []
        
        for feedback in feedback_items:
            feedback_data.append({
                "id": feedback.id,
                "user_name": feedback.user_name,
                "email": feedback.email,
                "category": feedback.category,
                "message": feedback.message,
                "status": feedback.status,
                "admin_reply": feedback.admin_reply,
                "created_at": feedback.created_at.isoformat()
            })
        
        return jsonify({
            "success": True,
            "feedback": feedback_data
        })
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route("/admin/api/feedback", methods=["POST"])
@admin_required
def update_feedback():
    """Update feedback status or reply"""
    try:
        data = request.get_json()
        feedback_id = data.get('feedback_id')
        action = data.get('action')
        
        feedback = Feedback.query.get(feedback_id)
        if not feedback:
            return jsonify({"success": False, "error": "Feedback not found"}), 404
        
        if action == 'mark_reviewed':
            feedback.status = 'reviewed'
        elif action == 'mark_resolved':
            feedback.status = 'resolved'
        elif action == 'reply':
            feedback.admin_reply = data.get('reply')
            feedback.status = 'replied'
        
        db.session.commit()
        
        return jsonify({"success": True})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route("/admin/api/export/users")
@admin_required
def export_users_csv():
    """Export users data as CSV"""
    try:
        # Get filter parameter
        user_filter = request.args.get('filter', 'all')  # all, users, admins
        
        # Query users based on filter
        if user_filter == 'users':
            users = User.query.filter(User.role != 'admin').all()
        elif user_filter == 'admins':
            users = User.query.filter(User.role == 'admin').all()
        else:
            users = User.query.all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ID', 'First Name', 'Last Name', 'Email', 'Role', 'Created At', 'Last Login', 'Progress'])
        
        # Write data
        for user in users:
            try:
                # Calculate progress based on core stages only
                core_stages = ['preconception', 'antenatal', 'birth', 'postnatal']
                user_responses = UserResponse.query.filter_by(user_id=user.user_ID).all()
                
                # Count how many core stages the user has attempted
                attempted_stages = set()
                for response in user_responses:
                    if response.stage in core_stages:
                        attempted_stages.add(response.stage)
                
                # Calculate progress as percentage of core stages attempted
                progress = round((len(attempted_stages) / len(core_stages)) * 100)
                # Ensure progress never exceeds 100%
                progress = min(progress, 100)
                
                writer.writerow([
                    user.user_ID,
                    user.first_name or '',
                    user.second_name or '',
                    user.email or '',
                    user.role or 'user',
                    user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else 'Unknown',
                    user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Never',
                    f"{progress}%"
                ])
            except Exception as user_error:
                print(f"Error processing user {user.user_ID}: {user_error}")
                # Write a row with error info
                writer.writerow([
                    user.user_ID,
                    user.first_name or '',
                    user.second_name or '',
                    user.email or '',
                    user.role or 'user',
                    'Error',
                    'Error',
                    'Error'
                ])
        
        output.seek(0)
        
        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={"Content-disposition": f"attachment; filename=users_export_{user_filter}.csv"}
        )
    
    except Exception as e:
        print(f"Export error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route("/admin/api/export/feedback")
@admin_required
def export_feedback_csv():
    """Export feedback data as CSV"""
    try:
        feedback_items = Feedback.query.order_by(desc(Feedback.created_at)).all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['ID', 'User Name', 'Email', 'Category', 'Message', 'Status', 'Created At', 'Admin Reply'])
        
        # Write data
        for feedback in feedback_items:
            writer.writerow([
                feedback.id,
                feedback.user_name,
                feedback.email,
                feedback.category,
                feedback.message,
                feedback.status,
                feedback.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                feedback.admin_reply or ''
            ])
        
        output.seek(0)
        
        from flask import Response
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={"Content-disposition": "attachment; filename=feedback_export.csv"}
        )
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route("/admin/api/reports/users")
@admin_required
def generate_user_report_pdf():
    """Generate user performance report as PDF"""
    if not reportlab_available:
        return jsonify({
            "success": False, 
            "error": "PDF export not available. ReportLab not installed.",
            "message": "Please install reportlab to generate PDF reports: pip install reportlab"
        }), 503
    
    try:
        # Get user data
        users = User.query.all()
        
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1
        )
        story.append(Paragraph("Funza Mama - User Performance Report", title_style))
        story.append(Spacer(1, 20))
        
        # Summary
        story.append(Paragraph(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Paragraph(f"Total Users: {len(users)}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # User table
        table_data = [['Name', 'Email', 'Progress', 'Last Active']]
        
        for user in users:
            # Calculate progress based on core stages only
            core_stages = ['preconception', 'antenatal', 'birth', 'postnatal']
            user_responses = UserResponse.query.filter_by(user_id=user.user_ID).all()
            
            # Count how many core stages the user has attempted
            attempted_stages = set()
            for response in user_responses:
                if response.stage in core_stages:
                    attempted_stages.add(response.stage)
            
            # Calculate progress as percentage of core stages attempted
            progress = round((len(attempted_stages) / len(core_stages)) * 100)
            # Ensure progress never exceeds 100%
            progress = min(progress, 100)
            
            last_active = user.last_login or user.created_at
            
            table_data.append([
                f"{user.first_name} {user.second_name}",
                user.email,
                f"{progress}%",
                last_active.strftime('%Y-%m-%d')
            ])
        
        user_table = Table(table_data)
        user_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(Paragraph("User Performance Summary", styles['Heading2']))
        story.append(Spacer(1, 12))
        story.append(user_table)
        
        doc.build(story)
        buffer.seek(0)
        
        from flask import Response
        return Response(
            buffer.getvalue(),
            mimetype='application/pdf',
            headers={"Content-disposition": "attachment; filename=user_performance_report.pdf"}
        )
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route("/admin/api/reports/analytics")
@admin_required
def generate_analytics_report_pdf():
    """Generate analytics report as PDF"""
    if not reportlab_available:
        return jsonify({
            "success": False, 
            "error": "PDF export not available. ReportLab not installed.",
            "message": "Please install reportlab to generate PDF reports: pip install reportlab"
        }), 503
    
    try:
        # Get analytics data
        total_users = User.query.count()
        total_responses = UserResponse.query.count()
        
        # Calculate average scores by stage
        stage_scores = {}
        stages = ['preconception', 'antenatal', 'birth', 'postnatal']
        
        for stage in stages:
            # Calculate average score from is_correct field (True = 100, False = 0)
            stage_responses = UserResponse.query.filter_by(stage=stage).all()
            if stage_responses:
                correct_count = sum(1 for response in stage_responses if response.is_correct)
                total_count = len(stage_responses)
                avg_score = (correct_count / total_count) * 100 if total_count > 0 else 0
                stage_scores[stage] = round(avg_score, 1)
            else:
                stage_scores[stage] = 0
        
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1
        )
        story.append(Paragraph("Funza Mama - Analytics Report", title_style))
        story.append(Spacer(1, 20))
        
        # Summary
        story.append(Paragraph(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Paragraph(f"Total Users: {total_users}", styles['Normal']))
        story.append(Paragraph(f"Total Responses: {total_responses}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Stage performance table
        table_data = [['Stage', 'Average Score']]
        for stage, score in stage_scores.items():
            table_data.append([stage.title(), f"{score}%"])
        
        stage_table = Table(table_data)
        stage_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(Paragraph("Stage Performance Summary", styles['Heading2']))
        story.append(Spacer(1, 12))
        story.append(stage_table)
        
        doc.build(story)
        buffer.seek(0)
        
        from flask import Response
        return Response(
            buffer.getvalue(),
            mimetype='application/pdf',
            headers={"Content-disposition": "attachment; filename=analytics_report.pdf"}
        )
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route("/admin/api/reports/feedback")
@admin_required
def generate_feedback_report_pdf():
    """Generate feedback report as PDF"""
    if not reportlab_available:
        return jsonify({
            "success": False, 
            "error": "PDF export not available. ReportLab not installed.",
            "message": "Please install reportlab to generate PDF reports: pip install reportlab"
        }), 503
    
    try:
        # Get feedback data
        feedback_items = Feedback.query.order_by(desc(Feedback.created_at)).all()
        
        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1
        )
        story.append(Paragraph("Funza Mama - Feedback Report", title_style))
        story.append(Spacer(1, 20))
        
        # Summary
        story.append(Paragraph(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Paragraph(f"Total Feedback Items: {len(feedback_items)}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Feedback items
        for feedback in feedback_items:
            story.append(Paragraph(f"<b>From:</b> {feedback.user_name} ({feedback.email})", styles['Normal']))
            story.append(Paragraph(f"<b>Category:</b> {feedback.category}", styles['Normal']))
            story.append(Paragraph(f"<b>Date:</b> {feedback.created_at.strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            story.append(Paragraph(f"<b>Status:</b> {feedback.status}", styles['Normal']))
            story.append(Paragraph(f"<b>Message:</b> {feedback.message}", styles['Normal']))
            if feedback.admin_reply:
                story.append(Paragraph(f"<b>Admin Reply:</b> {feedback.admin_reply}", styles['Normal']))
            story.append(Spacer(1, 20))
        
        doc.build(story)
        buffer.seek(0)
        
        from flask import Response
        return Response(
            buffer.getvalue(),
            mimetype='application/pdf',
            headers={"Content-disposition": "attachment; filename=feedback_report.pdf"}
        )
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route("/admin/api/users/<int:user_id>")
@admin_required
def get_user_details(user_id):
    """Get detailed information about a specific user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        # Get user responses for progress calculation
        user_responses = UserResponse.query.filter_by(user_id=user_id).all()
        total_responses = len(user_responses)
        correct_responses = sum(1 for response in user_responses if response.is_correct)
        progress = round((correct_responses / total_responses * 100) if total_responses > 0 else 0, 1)
        
        # Get last active time
        last_active = user.last_login if user.last_login else user.created_at
        
        user_data = {
            "user_ID": user.user_ID,
            "id": user.user_ID,  # Keep both for compatibility
            "name": f"{user.first_name} {user.second_name}",
            "first_name": user.first_name,
            "last_name": user.second_name,
            "email": user.email,
            "username": user.username,
            "role": user.role or 'user',
            "status": "active",  # Default status for now
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_active": last_active.isoformat() if last_active else None,
            "progress": progress,
            "total_responses": total_responses,
            "correct_responses": correct_responses
        }
        
        return jsonify({"success": True, "user": user_data})
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route("/admin/api/users/<int:user_id>", methods=['PUT'])
@admin_required
def update_user(user_id):
    """Update user information"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        data = request.get_json()
        
        # Update user fields
        if 'firstName' in data:
            user.first_name = data['firstName']
        if 'lastName' in data:
            user.second_name = data['lastName']
        if 'email' in data:
            user.email = data['email']
        if 'username' in data:
            user.username = data['username']
        if 'role' in data:
            user.role = data['role']
        
        db.session.commit()
        
        return jsonify({"success": True, "message": "User updated successfully"})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route("/admin/api/users/<int:user_id>", methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete a user"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"success": False, "error": "User not found"}), 404
        
        # Prevent deleting admin users
        if user.role == 'admin':
            return jsonify({"success": False, "error": "Cannot delete admin users"}), 400
        
        # Delete user responses first (foreign key constraint)
        UserResponse.query.filter_by(user_id=user_id).delete()
        
        # Delete user badges
        Badge.query.filter_by(user_ID=user_id).delete()
        
        # Delete user question history
        UserQuestionHistory.query.filter_by(user_id=user_id).delete()
        
        # Delete the user
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({"success": True, "message": "User deleted successfully"})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 500

# =============================================================================
# ADVANCED ANALYTICS ENDPOINTS
# =============================================================================

@admin_bp.route("/admin/api/analytics/learning-effectiveness")
@admin_required
def learning_effectiveness_analytics():
    """Get learning effectiveness analytics"""
    try:
        stages = ['preconception', 'antenatal', 'birth', 'postnatal']
        learning_data = {}
        
        for stage in stages:
            # Get all users who attempted this stage
            stage_users = db.session.query(User).join(UserResponse).filter(
                UserResponse.stage == stage
            ).distinct().all()
            
            stage_analytics = {
                "total_learners": len(stage_users),
                "improvement_rate": 0,
                "mastery_rate": 0,
                "difficulty_progression": [],
                "retention_curve": []
            }
            
            if stage_users:
                improvements = []
                mastery_count = 0
                
                for user in stage_users:
                    # Get user's attempts for this stage, ordered by attempt number
                    user_attempts = UserResponse.query.filter_by(
                        user_id=user.user_ID, 
                        stage=stage
                    ).order_by(UserResponse.attempt_number).all()
                    
                    if len(user_attempts) >= 2:
                        # Calculate improvement from first to latest attempt
                        first_attempt = user_attempts[0]
                        latest_attempt = user_attempts[-1]
                        
                        first_score = 100 if first_attempt.is_correct else 0
                        latest_score = 100 if latest_attempt.is_correct else 0
                        
                        improvement = latest_score - first_score
                        improvements.append(improvement)
                        
                        # Check if user achieved mastery (80%+ in latest attempt)
                        if latest_score >= 80:
                            mastery_count += 1
                    
                    # Build retention curve data (attempt vs. score)
                    attempt_scores = []
                    for attempt in user_attempts:
                        score = 100 if attempt.is_correct else 0
                        attempt_scores.append({
                            "attempt": attempt.attempt_number,
                            "score": score
                        })
                    stage_analytics["retention_curve"].append(attempt_scores)
                
                if improvements:
                    stage_analytics["improvement_rate"] = round(sum(improvements) / len(improvements), 1)
                    stage_analytics["mastery_rate"] = round((mastery_count / len(stage_users)) * 100, 1)
            
            learning_data[stage] = stage_analytics
        
        return jsonify({
            "success": True,
            "learning_effectiveness": learning_data
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route("/admin/api/analytics/demographics")
@admin_required
def demographic_analytics():
    """Get demographic-based analytics"""
    try:
        # Age group performance
        age_groups = {
            "18-24": {"users": [], "avg_score": 0, "completion_rate": 0},
            "25-34": {"users": [], "avg_score": 0, "completion_rate": 0},
            "35-44": {"users": [], "avg_score": 0, "completion_rate": 0},
            "45+": {"users": [], "avg_score": 0, "completion_rate": 0}
        }
        
        # Gender performance
        gender_performance = {
            "female": {"count": 0, "avg_score": 0, "completion_rate": 0},
            "male": {"count": 0, "avg_score": 0, "completion_rate": 0},
            "other": {"count": 0, "avg_score": 0, "completion_rate": 0}
        }
        
        # Healthcare professional performance
        professional_performance = {
            "healthcare": {"count": 0, "avg_score": 0, "completion_rate": 0},
            "general": {"count": 0, "avg_score": 0, "completion_rate": 0}
        }
        
        users = User.query.filter(User.email != 'admin@funzamama.org').all()
        
        for user in users:
            # Calculate user's overall performance
            all_responses = UserResponse.query.filter_by(user_id=user.user_ID).all()
            if all_responses:
                correct_count = sum(1 for response in all_responses if response.is_correct)
                total_count = len(all_responses)
                avg_score = (correct_count / total_count) * 100 if total_count > 0 else 0
                
                # Count completed stages
                completed_stages = len(set(response.stage for response in all_responses))
                completion_rate = (completed_stages / 4) * 100  # 4 total stages
                
                # Age group categorization
                if user.age and user.age < 25:
                    age_group = "18-24"
                elif user.age and user.age < 35:
                    age_group = "25-34"
                elif user.age and user.age < 45:
                    age_group = "35-44"
                else:
                    age_group = "45+"
                
                age_groups[age_group]["users"].append(avg_score)
                
                # Gender categorization
                gender = user.gender.lower() if user.gender else "other"
                if gender not in gender_performance:
                    gender = "other"
                gender_performance[gender]["count"] += 1
                gender_performance[gender]["avg_score"] += avg_score
                gender_performance[gender]["completion_rate"] += completion_rate
                
                # Professional categorization
                is_healthcare = "dr_" in user.username.lower() or "nurse" in user.username.lower()
                prof_type = "healthcare" if is_healthcare else "general"
                professional_performance[prof_type]["count"] += 1
                professional_performance[prof_type]["avg_score"] += avg_score
                professional_performance[prof_type]["completion_rate"] += completion_rate
        
        # Calculate averages
        for age_group, data in age_groups.items():
            if data["users"]:
                data["avg_score"] = round(sum(data["users"]) / len(data["users"]), 1)
                data["completion_rate"] = round(sum(data["users"]) / len(data["users"]), 1)  # Simplified
        
        for gender, data in gender_performance.items():
            if data["count"] > 0:
                data["avg_score"] = round(data["avg_score"] / data["count"], 1)
                data["completion_rate"] = round(data["completion_rate"] / data["count"], 1)
        
        for prof_type, data in professional_performance.items():
            if data["count"] > 0:
                data["avg_score"] = round(data["avg_score"] / data["count"], 1)
                data["completion_rate"] = round(data["completion_rate"] / data["count"], 1)
        
        return jsonify({
            "success": True,
            "age_groups": age_groups,
            "gender_performance": gender_performance,
            "professional_performance": professional_performance
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@admin_bp.route("/admin/api/analytics/engagement")
@admin_required
def engagement_analytics():
    """Get engagement and retention analytics"""
    try:
        # User journey funnel
        stages = ['preconception', 'antenatal', 'birth', 'postnatal']
        funnel_data = {}
        
        for i, stage in enumerate(stages):
            if i == 0:
                # First stage - all users who started
                stage_users = db.session.query(User).join(UserResponse).filter(
                    UserResponse.stage == stage
                ).distinct().all()
            else:
                # Subsequent stages - users who completed previous stage
                prev_stage = stages[i-1]
                prev_stage_users = db.session.query(User).join(UserResponse).filter(
                    UserResponse.stage == prev_stage
                ).distinct().all()
                
                stage_users = db.session.query(User).join(UserResponse).filter(
                    UserResponse.stage == stage,
                    User.user_ID.in_([u.user_ID for u in prev_stage_users])
                ).distinct().all()
            
            funnel_data[stage] = len(stage_users)
        
        # Session analytics
        session_data = {
            "avg_session_duration": 0,
            "avg_questions_per_session": 0,
            "return_user_rate": 0,
            "drop_off_points": []
        }
        
        # Calculate average session duration (simulate based on responses)
        all_responses = UserResponse.query.all()
        if all_responses:
            session_data["avg_questions_per_session"] = len(all_responses) // len(set(r.user_id for r in all_responses))
            session_data["avg_session_duration"] = session_data["avg_questions_per_session"] * 2  # 2 min per question
        
        # Return user rate (users with multiple sessions)
        users_with_multiple_sessions = 0
        all_users = User.query.filter(User.email != 'admin@funzamama.org').all()
        
        for user in all_users:
            user_responses = UserResponse.query.filter_by(user_id=user.user_ID).all()
            if len(set(r.attempt_number for r in user_responses)) > 1:
                users_with_multiple_sessions += 1
        
        if all_users:
            session_data["return_user_rate"] = round((users_with_multiple_sessions / len(all_users)) * 100, 1)
        
        # Content effectiveness (most/least effective questions)
        content_effectiveness = {
            "most_effective": [],
            "least_effective": [],
            "difficulty_rankings": {}
        }
        
        # Get question effectiveness by stage
        for stage in stages:
            stage_responses = UserResponse.query.filter_by(stage=stage).all()
            if stage_responses:
                correct_rate = sum(1 for r in stage_responses if r.is_correct) / len(stage_responses)
                content_effectiveness["difficulty_rankings"][stage] = round(correct_rate * 100, 1)
        
        return jsonify({
            "success": True,
            "funnel_data": funnel_data,
            "session_data": session_data,
            "content_effectiveness": content_effectiveness
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
