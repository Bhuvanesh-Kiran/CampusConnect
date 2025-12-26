from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from flask_login import login_required, current_user
from .models import (
    ClubMember, db, Administrator, Student, ClubLeader, Club, 
    Feedback, JoiningRequest, Gallery, News, Event, Activity, Interested, Notification
)
import csv
from io import TextIOWrapper
from datetime import datetime

# Create a Blueprint for the routes
main = Blueprint('main', __name__)

# Home Route - Index Page
@main.route('/')
def index():
    # Fetch clubs and events from the database
    clubs = Club.query.all()
    events = Event.query.filter(Event.event_date >= datetime.today()).order_by(Event.event_date).all()
    
    # Pass the Notification model to the template context
    return render_template('index.html', clubs=clubs, events=events, Notification=Notification)
# Login Route
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']

        if user_type == '1':  # Administrator
            admin = Administrator.query.filter_by(email=email).first()
            if admin and admin.password == password:
                session['user_type'] = 'admin'
                session['user_id'] = admin.admin_id
                return redirect(url_for('main.admin_home'))
            else:
                flash('Invalid email or password for Administrator')
                return redirect(url_for('main.login'))

        elif user_type == '2':  # Club Leader
            club_leader = ClubLeader.query.filter_by(email=email).first()
            if club_leader and club_leader.password == password:
                session['user_type'] = 'club_leader'
                session['user_id'] = club_leader.leader_id
                return redirect(url_for('main.index'))  # Redirect to index after login
            else:
                flash('Invalid email or password for Club Leader')
                return redirect(url_for('main.login'))

        elif user_type == '3':  # Student
            student = Student.query.filter_by(email=email).first()
            if student and student.password == password:
                session['user_type'] = 'student'
                session['user_id'] = student.student_id
                return redirect(url_for('main.index'))  # Redirect to index after login
            else:
                flash('Invalid email or password for Student')
                return redirect(url_for('main.login'))

        else:
            flash('Invalid user type')
            return redirect(url_for('main.login'))

    return render_template('login.html')

# Admin Dashboard
@main.route('/admin_home')
def admin_home():
    if session.get('user_type') != 'admin':
        return redirect(url_for('main.login'))
    
    # Get total students and clubs count
    total_students = Student.query.count()
    total_clubs = Club.query.count()
    total_club_leaders = ClubLeader.query.count()
    
    return render_template('admin_home.html', total_students=total_students, total_clubs=total_clubs, total_club_leaders=total_club_leaders)

# Admin Club Leaders Page
@main.route('/adclubleaders')
def adclubleaders():
    if session.get('user_type') != 'admin':
        return redirect(url_for('main.login'))
    
    club_leaders = ClubLeader.query.join(Club, ClubLeader.leader_id == Club.club_leader).all()
    
    return render_template('adclubleaders.html', club_leaders=club_leaders)

# Admin Students Page
@main.route('/adstudents', methods=['GET', 'POST'])
def adstudents():
    if session.get('user_type') != 'admin':
        return redirect(url_for('main.login'))
    
    students = []
    batch_year = request.args.get('batchYear')
    
    if batch_year:
        students = Student.query.filter_by(batch=int(batch_year)).all()
    
    return render_template('adstudents.html', students=students)

# Add Students Route (CSV Upload)
@main.route('/add_students', methods=['POST'])
def add_students():
    if session.get('user_type') != 'admin':
        return redirect(url_for('main.login'))
    
    if request.method == 'POST':
        batch = request.form['batch']
        csv_file = request.files['csvFile']
        
        if not csv_file:
            flash('No file uploaded!')
            return redirect(url_for('main.adstudents'))
        
        try:
            # Read the CSV file
            csv_data = TextIOWrapper(csv_file, encoding='utf-8')
            csv_reader = csv.DictReader(csv_data)
            
            # Iterate over each row in the CSV
            for row in csv_reader:
                # Create a new Student object
                new_student = Student(
                    type_id=3,  # Type ID for students
                    regd_number=row['regd_number'],
                    full_name=row['full_name'],
                    department=row['department'],
                    academic_year=int(row['academic_year']),
                    batch=int(batch),
                    gender=row['gender'],
                    email=row['email'],
                    password=row['password'],
                    phone_number=row['phone_number']
                )
                
                # Add the new student to the session
                db.session.add(new_student)
            
            # Commit the session to save all students to the database
            db.session.commit()
            
            flash('Students added successfully!')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding students: {str(e)}')
        
        return redirect(url_for('main.adstudents'))

# Admin Clubs Page
@main.route('/adclubs')
def adclubs():
    if session.get('user_type') != 'admin':
        return redirect(url_for('main.login'))
    
    clubs = Club.query.all()
    all_students = Student.query.all()
    
    return render_template('adclubs.html', clubs=clubs, all_students=all_students)

# Add Club Route
@main.route('/add_club', methods=['POST'])
def add_club():
    if session.get('user_type') != 'admin':
        return redirect(url_for('main.login'))
    
    if request.method == 'POST':
        club_name = request.form['clubname']
        description = request.form['description']
        coordinator_name = request.form['coordinator']
        coordinator_contact = request.form['coord-contact']
        student_id = request.form['student_id']
        
        # Get the selected student
        student = Student.query.get(student_id)
        
        if not student:
            flash('Selected student not found!')
            return redirect(url_for('main.adclubs'))
        
        # Create a new club leader
        new_club_leader = ClubLeader(
            type_id=2,
            regd_number=student.regd_number,
            full_name=student.full_name,
            department=student.department,
            gender=student.gender,
            email=student.email,
            password=student.password,
            phone_number=student.phone_number,
            batch=student.batch
        )
        
        db.session.add(new_club_leader)
        db.session.commit()
        
        # Create the new club
        new_club = Club(
            club_name=club_name,
            club_leader=new_club_leader.leader_id,
            coordinator_name=coordinator_name,
            coordinator_contact=coordinator_contact,
            description=description
        )
        
        db.session.add(new_club)
        db.session.commit()
        
        flash('Club added successfully!')
        return redirect(url_for('main.adclubs'))

# Delete Club Route
@main.route('/delete_club/<int:club_id>', methods=['DELETE'])
def delete_club(club_id):
    if session.get('user_type') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    club = Club.query.get(club_id)
    if not club:
        return jsonify({'error': 'Club not found'}), 404
    
    try:
        # Delete related records in other tables
        Activity.query.filter_by(club_id=club_id).delete()
        Interested.query.filter_by(club_id=club_id).delete()
        Feedback.query.filter_by(club_id=club_id).delete()
        JoiningRequest.query.filter_by(club_id=club_id).delete()
        Gallery.query.filter_by(club_id=club_id).delete()
        News.query.filter_by(club_id=club_id).delete()
        Event.query.filter_by(club_id=club_id).delete()
        
        # Delete club members associated with the club
        ClubMember.query.filter_by(club_id=club_id).delete()
        
        # Delete the club leader associated with the club
        ClubLeader.query.filter_by(leader_id=club.club_leader).delete()
        
        # Finally, delete the club
        db.session.delete(club)
        db.session.commit()
        
        return jsonify({'message': 'Club deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Profile Route (for Students and Club Leaders)
@main.route('/profile')
def profile():
    if not session.get('user_id'):
        return redirect(url_for('main.login'))
    
    user_id = session.get('user_id')
    user_type = session.get('user_type')
    
    if user_type == 'student':
        user = Student.query.get_or_404(user_id)
    elif user_type == 'club_leader':
        user = ClubLeader.query.get_or_404(user_id)
    
    return render_template('profile.html', user=user, user_type=user_type)

# Change Password Route (for Students and Club Leaders)
@main.route('/change_password', methods=['POST'])
def change_password():
    if session.get('user_type') not in ['student', 'club_leader']:
        return redirect(url_for('main.login'))
    
    user_id = session.get('user_id')
    user_type = session.get('user_type')
    
    if user_type == 'student':
        user = Student.query.get_or_404(user_id)
    elif user_type == 'club_leader':
        user = ClubLeader.query.get_or_404(user_id)
    
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        # Verify current password
        if user.password != current_password:
            flash('Current password is incorrect.')
            return redirect(url_for('main.profile'))
        
        # Check if new password matches confirmation
        if new_password != confirm_password:
            flash('New password and confirmation do not match.')
            return redirect(url_for('main.profile'))
        
        # Update password
        user.password = new_password
        db.session.commit()
        
        flash('Password changed successfully!')
        return redirect(url_for('main.profile'))

# Clubs Page (For Students & Club Leaders)
@main.route('/clubs')
def clubs():
    if not session.get('user_id'):
        return redirect(url_for('main.login'))
    
    # Fetch all clubs from the database
    clubs = Club.query.all()
    return render_template('clubs.html', clubs=clubs, ClubMember=ClubMember)

# Club Dashboard Route
@main.route('/club_dashboard/<int:club_id>')
def club_dashboard(club_id):
    if session.get('user_type') not in ['student', 'club_leader']:
        return redirect(url_for('main.login'))
    
    # Fetch club details from the database
    club = Club.query.get_or_404(club_id)
    is_club_leader = False
    if session.get('user_type') == 'club_leader':
        club_leader = ClubLeader.query.get(session['user_id'])
        is_club_leader = club_leader.assigned_club == club_id

    return render_template('club_dashboard.html', club=club, is_club_leader=is_club_leader, ClubMember=ClubMember)

# Description Route
@main.route('/description/<int:club_id>', methods=['GET', 'POST'])
def description(club_id):
    if session.get('user_type') not in ['student', 'club_leader']:
        return redirect(url_for('main.login'))
    
    club = Club.query.get_or_404(club_id)
    is_club_leader = False
    if session.get('user_type') == 'club_leader':
        club_leader = ClubLeader.query.get(session['user_id'])
        is_club_leader = club_leader.assigned_club == club_id

    if request.method == 'POST' and is_club_leader:
        new_description = request.form['description']
        club.description = new_description
        db.session.commit()
        flash('Description updated successfully!')
        return redirect(url_for('main.description', club_id=club_id))

    return render_template('description.html', club=club, is_club_leader=is_club_leader, ClubMember=ClubMember)

# News & Events Route
@main.route('/news_events/<int:club_id>', methods=['GET', 'POST'])
def news_events(club_id):
    if session.get('user_type') not in ['student', 'club_leader']:
        return redirect(url_for('main.login'))
    
    club = Club.query.get_or_404(club_id)
    is_club_leader = False
    if session.get('user_type') == 'club_leader':
        club_leader = ClubLeader.query.get(session['user_id'])
        is_club_leader = club_leader.assigned_club == club_id

    if request.method == 'POST' and is_club_leader:
        if 'add_news' in request.form:
            headline = request.form['headline']
            news_date = request.form['news_date']
            news_content = request.form['news_content']
            new_news = News(club_id=club_id, club_name=club.club_name, headline=headline, news_date=news_date, news=news_content)
            db.session.add(new_news)
            db.session.commit()

            # Notify all club members
            members = ClubMember.query.filter_by(club_id=club_id).all()
            for member in members:
                notification = Notification(
                    student_id=member.student_id,
                    message=f"New news added to {club.club_name}: {headline}"
                )
                db.session.add(notification)
            db.session.commit()

            flash('News added successfully!')
        elif 'add_event' in request.form:
            event_name = request.form['event_name']
            event_date = request.form['event_date']
            event_details = request.form['event_details']
            new_event = Event(club_id=club_id, club_name=club.club_name, headline=event_name, event_date=event_date, event_details=event_details)
            db.session.add(new_event)
            db.session.commit()

            # Notify all club members
            members = ClubMember.query.filter_by(club_id=club_id).all()
            for member in members:
                notification = Notification(
                    student_id=member.student_id,
                    message=f"New event added to {club.club_name}: {event_name}"
                )
                db.session.add(notification)
            db.session.commit()

            flash('Event added successfully!')

    news = News.query.filter_by(club_id=club_id).all()
    events = Event.query.filter_by(club_id=club_id).all()
    return render_template('news_events.html', club=club, news=news, events=events, is_club_leader=is_club_leader, ClubMember=ClubMember)

# Gallery Route
@main.route('/gallery/<int:club_id>', methods=['GET', 'POST'])
def gallery(club_id):
    if session.get('user_type') not in ['student', 'club_leader']:
        return redirect(url_for('main.login'))
    
    club = Club.query.get_or_404(club_id)
    is_club_leader = False
    if session.get('user_type') == 'club_leader':
        club_leader = ClubLeader.query.get(session['user_id'])
        is_club_leader = club_leader.assigned_club == club_id

    if request.method == 'POST' and is_club_leader:
        if 'add_photo' in request.form:
            photo_name = request.form['photo_name']
            photo_url = request.form['photo_url']
            new_photo = Gallery(club_id=club_id, photo_name=photo_name, photo_url=photo_url)
            db.session.add(new_photo)
            db.session.commit()
            flash('Photo added successfully!')
        elif 'add_video' in request.form:
            video_name = request.form['video_name']
            video_url = request.form['video_url']
            new_video = Gallery(club_id=club_id, video_name=video_name, video_url=video_url)
            db.session.add(new_video)
            db.session.commit()
            flash('Video added successfully!')

    gallery = Gallery.query.filter_by(club_id=club_id).all()
    return render_template('gallery.html', club=club, gallery=gallery, is_club_leader=is_club_leader, ClubMember=ClubMember)

# Feedback Route
# Feedback Route
@main.route('/feedback/<int:club_id>', methods=['GET', 'POST'])
def feedback(club_id):
    if session.get('user_type') not in ['student', 'club_leader']:
        return redirect(url_for('main.login'))
    
    club = Club.query.get_or_404(club_id)
    is_club_leader = False
    if session.get('user_type') == 'club_leader':
        club_leader = ClubLeader.query.get(session['user_id'])
        is_club_leader = club_leader.assigned_club == club_id

    if is_club_leader:
        # Club Leader: View Feedbacks
        feedbacks = Feedback.query.filter_by(club_id=club_id).all()
        return render_template('view_feedbacks.html', club=club, feedbacks=feedbacks, is_club_leader=is_club_leader, ClubMember=ClubMember)
    else:
        # Student: Submit Feedback
        if request.method == 'POST':
            feedback_text = request.form['feedback']
            student_id = session.get('user_id')
            new_feedback = Feedback(student_id=student_id, club_id=club_id, feedback_text=feedback_text)
            db.session.add(new_feedback)
            db.session.commit()
            flash('Feedback submitted successfully!')
            return redirect(url_for('main.feedback', club_id=club_id))

        return render_template('feedback.html', club=club, is_club_leader=is_club_leader, ClubMember=ClubMember)

# Join Route
@main.route('/join/<int:club_id>', methods=['GET', 'POST'])
def join(club_id):
    if session.get('user_type') != 'student':
        return redirect(url_for('main.login'))
    
    club = Club.query.get_or_404(club_id)
    student_id = session.get('user_id')

    # Check if the student is already a member
    is_member = ClubMember.query.filter_by(club_id=club_id, student_id=student_id).first()
    if is_member:
        flash('You are already a member of this club!')
        return redirect(url_for('main.club_dashboard', club_id=club_id))

    # Check if a join request already exists
    join_request = JoiningRequest.query.filter_by(club_id=club_id, student_id=student_id).first()
    if join_request:
        flash('Your join request is already pending.')
        return render_template('join.html', club=club, join_request=join_request, ClubMember=ClubMember)

    if request.method == 'POST':
        # Create a new join request
        new_request = JoiningRequest(club_id=club_id, student_id=student_id)
        db.session.add(new_request)
        db.session.commit()
        flash('Join request submitted successfully!')
        return redirect(url_for('main.join', club_id=club_id))

    return render_template('join.html', club=club, ClubMember=ClubMember)

# Handle Join Request Route
@main.route('/handle_join_request/<int:request_id>/<action>')
def handle_join_request(request_id, action):
    if session.get('user_type') != 'club_leader':
        return redirect(url_for('main.login'))
    
    join_request = JoiningRequest.query.get_or_404(request_id)
    club_leader = ClubLeader.query.get(session['user_id'])
    is_club_leader = club_leader.assigned_club == join_request.club_id

    if not is_club_leader:
        flash('You are not authorized to handle this join request.')
        return redirect(url_for('main.club_dashboard', club_id=club_leader.assigned_club))

    if action == 'approve':
        # Add the student as a club member
        new_member = ClubMember(club_id=join_request.club_id, student_id=join_request.student_id)
        db.session.add(new_member)
        join_request.status = 'Approved'
        db.session.commit()
        flash('Join request approved successfully!')
    elif action == 'reject':
        join_request.status = 'Rejected'
        db.session.commit()
        flash('Join request rejected successfully!')

    return redirect(url_for('main.join_requests', club_id=club_leader.assigned_club))

# Activities Route
@main.route('/activities/<int:club_id>', methods=['GET', 'POST'])
def activities(club_id):
    if session.get('user_type') not in ['student', 'club_leader']:
        return redirect(url_for('main.login'))
    
    club = Club.query.get_or_404(club_id)
    student_id = session.get('user_id')
    is_club_leader = False

    if session.get('user_type') == 'club_leader':
        club_leader = ClubLeader.query.get(session['user_id'])
        is_club_leader = club_leader.assigned_club == club_id

    # Fetch activities for the club
    activities = Activity.query.filter_by(club_id=club_id).all()

    if request.method == 'POST':
        if 'add_activity' in request.form and is_club_leader:
            # Add new activity
            activity_name = request.form['activity_name']
            activity_date = request.form['activity_date']
            activity_time = request.form['activity_time']
            description = request.form['description']
            venue = request.form['venue']

            new_activity = Activity(
                club_id=club_id,
                activity_name=activity_name,
                activity_date=activity_date,
                activity_time=activity_time,
                description=description,
                venue=venue
            )
            db.session.add(new_activity)
            db.session.commit()
            flash('Activity added successfully!')
            return redirect(url_for('main.activities', club_id=club_id))

        elif 'interested' in request.form and session.get('user_type') == 'student':
            # Mark interest in an activity
            activity_id = request.form['activity_id']
            student_id = session.get('user_id')

            # Check if the student is already interested
            existing_interest = Interested.query.filter_by(activity_id=activity_id, student_id=student_id).first()
            if existing_interest:
                flash('You have already shown interest in this activity!')
                return redirect(url_for('main.activities', club_id=club_id))

            new_interest = Interested(activity_id=activity_id, student_id=student_id, club_id=club_id)
            db.session.add(new_interest)
            db.session.commit()
            flash('Interest marked successfully!')
            return redirect(url_for('main.activities', club_id=club_id))

        elif 'delete_activity' in request.form and is_club_leader:
            # Delete an activity
            activity_id = request.form['activity_id']
            activity = Activity.query.get(activity_id)
            if activity:
                # Delete all related entries in the interested table
                Interested.query.filter_by(activity_id=activity_id).delete()
                db.session.delete(activity)
                db.session.commit()
                flash('Activity deleted successfully!')
            return redirect(url_for('main.activities', club_id=club_id))

    return render_template(
        'activities.html',
        club=club,
        activities=activities,
        is_club_leader=is_club_leader,
        Interested=Interested,
        ClubMember=ClubMember
    )

# Notifications Route
@main.route('/notifications')
def notifications():
    if session.get('user_type') != 'student':
        return redirect(url_for('main.login'))
    
    student_id = session.get('user_id')
    notifications = Notification.query.filter_by(student_id=student_id).order_by(Notification.timestamp.desc()).all()
    return render_template('notifications.html', notifications=notifications)

# Mark Notification as Read Route
@main.route('/mark_notification_as_read/<int:notification_id>')
def mark_notification_as_read(notification_id):
    if session.get('user_type') != 'student':
        return redirect(url_for('main.login'))
    
    notification = Notification.query.get_or_404(notification_id)
    notification.status = 'read'
    db.session.commit()
    flash('Notification marked as read!')
    return redirect(url_for('main.notifications'))

# Club Members Route (For Club Leaders)
@main.route('/club_members/<int:club_id>')
def club_members(club_id):
    if session.get('user_type') != 'club_leader':
        return redirect(url_for('main.login'))
    
    club = Club.query.get_or_404(club_id)
    club_leader = ClubLeader.query.get(session['user_id'])
    is_club_leader = club_leader.assigned_club == club_id

    if not is_club_leader:
        flash('You are not authorized to view members of this club.')
        return redirect(url_for('main.club_dashboard', club_id=club_id))

    # Fetch all members of the club
    members = ClubMember.query.filter_by(club_id=club_id).all()
    students = [member.student for member in members]

    return render_template('club_members.html', club=club, students=students, is_club_leader=is_club_leader, ClubMember=ClubMember)

# Join Requests Route (For Club Leaders)
@main.route('/join_requests/<int:club_id>')
def join_requests(club_id):
    if session.get('user_type') != 'club_leader':
        return redirect(url_for('main.login'))
    
    club_leader = ClubLeader.query.get(session['user_id'])
    is_club_leader = club_leader.assigned_club == club_id

    if not is_club_leader:
        flash('You are not authorized to view join requests for this club.')
        return redirect(url_for('main.club_dashboard', club_id=club_leader.assigned_club))
    
    # Fetch the club details
    club = Club.query.get_or_404(club_id)
    
    # Fetch all pending join requests for the club
    join_requests = JoiningRequest.query.filter_by(club_id=club_id, status='Pending').all()
    
    return render_template('join_requests.html', club=club, join_requests=join_requests, is_club_leader=is_club_leader)

# Logout Route
@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))
