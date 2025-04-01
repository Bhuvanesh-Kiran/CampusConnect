from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from flask_login import login_required, current_user
from .models import (ClubMember, db, Administrator, Student, ClubLeader, Club, 
    Feedback, JoiningRequest, Gallery, News, Event, Activity, Interested)

# Create a Blueprint for the routes
main = Blueprint('main', __name__)

# Home Route - Index Page
@main.route('/')
def index():
    return render_template('index.html')

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
                print(f"Session State after login: {session}")  # Log session state after login
                print(f"User Type after login: {session.get('user_type')}")  # Log user type after login

                return redirect(url_for('main.admin_home'))

            else:
                flash('Invalid email or password for Administrator')
                return redirect(url_for('main.login'))

        elif user_type == '2':  # Club Leader
            club_leader = ClubLeader.query.filter_by(email=email).first()
            if club_leader and club_leader.password == password:
                session['user_type'] = 'club_leader'
                session['user_id'] = club_leader.leader_id
                return redirect(url_for('main.clubs'))
            else:
                flash('Invalid email or password for Club Leader')
                return redirect(url_for('main.login'))

        elif user_type == '3':  # Student
            student = Student.query.filter_by(email=email).first()
            if student and student.password == password:
                session['user_type'] = 'student'
                session['user_id'] = student.student_id
                return redirect(url_for('main.clubs'))
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
    
    # Get counts for overview panel
    total_students = Student.query.count()
    total_clubs = Club.query.count()
    total_club_leaders = ClubLeader.query.count()
    
    # Get recent join activities
    recent_activities = db.session.query(
        Student.full_name,
        Student.email,  # Added email to the query
        Club.club_name
    ).join(ClubMember, ClubMember.student_id == Student.student_id)\
     .join(Club, Club.club_id == ClubMember.club_id)\
     .limit(10)\
     .all()

    return render_template(
        'admin_home.html',
        total_students=total_students,
        total_clubs=total_clubs,
        total_club_leaders=total_club_leaders,
        recent_activities=recent_activities,
    )

# Clubs Page (For Students & Club Leaders)
@main.route('/clubs')
def clubs():
    if session.get('user_type') not in ['student', 'club_leader']:
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
            new_news = News(club_id=club_id, headline=headline, news_date=news_date, news=news_content)
            db.session.add(new_news)
            db.session.commit()
            flash('News added successfully!')
        elif 'add_event' in request.form:
            event_name = request.form['event_name']
            event_date = request.form['event_date']
            event_details = request.form['event_details']
            new_event = Event(club_id=club_id, headline=event_name, event_date=event_date, event_details=event_details)
            db.session.add(new_event)
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
@main.route('/feedback/<int:club_id>', methods=['GET', 'POST'])
def feedback(club_id):
    if session.get('user_type') not in ['student', 'club_leader']:
        return redirect(url_for('main.login'))
    
    club = Club.query.get_or_404(club_id)
    is_club_leader = session.get('user_type') == 'club_leader'

    if is_club_leader:
        # Club Leader: View Feedbacks
        feedbacks = Feedback.query.filter_by(club_id=club_id).all()
        return render_template('view_feedbacks.html', club=club, feedbacks=feedbacks, ClubMember=ClubMember)
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

        return render_template('feedback.html', club=club, ClubMember=ClubMember)

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

# Join Requests Route (For Club Leaders)
@main.route('/join_requests/<int:club_id>')
def join_requests(club_id):
    if session.get('user_type') != 'club_leader':
        return redirect(url_for('main.login'))
    
    club = Club.query.get_or_404(club_id)
    club_leader = ClubLeader.query.get(session['user_id'])
    if club_leader.assigned_club != club_id:
        flash('You are not authorized to view join requests for this club.')
        return redirect(url_for('main.club_dashboard', club_id=club_id))

    # Fetch all pending join requests for the club
    join_requests = JoiningRequest.query.filter_by(club_id=club_id, status='Pending').all()
    return render_template('join_requests.html', club=club, join_requests=join_requests, ClubMember=ClubMember)

# Approve/Reject Join Request Route
@main.route('/handle_join_request/<int:request_id>/<action>')
def handle_join_request(request_id, action):
    if session.get('user_type') != 'club_leader':
        return redirect(url_for('main.login'))
    
    join_request = JoiningRequest.query.get_or_404(request_id)
    club_leader = ClubLeader.query.get(session['user_id'])
    if club_leader.assigned_club != join_request.club_id:
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

# Club Members Route (For Club Leaders)
@main.route('/club_members/<int:club_id>')
def club_members(club_id):
    if session.get('user_type') != 'club_leader':
        return redirect(url_for('main.login'))
    
    club = Club.query.get_or_404(club_id)
    club_leader = ClubLeader.query.get(session['user_id'])
    if club_leader.assigned_club != club_id:
        flash('You are not authorized to view members of this club.')
        return redirect(url_for('main.club_dashboard', club_id=club_id))

    # Fetch all members of the club
    members = ClubMember.query.filter_by(club_id=club_id).all()
    students = [member.student for member in members]

    return render_template('club_members.html', club=club, students=students, ClubMember=ClubMember)

# Logout Route
@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))

# Admin Students Route
@main.route('/adstudents')
def adstudents():
    if session.get('user_type') != 'admin':
        return redirect(url_for('main.login'))
    students = Student.query.all()
    return render_template('adstudents.html', students=students)

# Admin Clubs Route
@main.route('/adclubs')
def adclubs():
    if session.get('user_type') != 'admin':
        return redirect(url_for('main.login'))
    clubs = Club.query.all()
    return render_template('adclubs.html', clubs=clubs)

# Admin Club Leaders Route
@main.route('/adclubleaders')
def adclubleaders():
    if session.get('user_type') != 'admin':
        return redirect(url_for('main.login'))
    club_leaders = ClubLeader.query.all()
    return render_template('adclubleaders.html', club_leaders=club_leaders)

# Add New Club Route
@main.route('/add_club', methods=['POST'])
def add_club():
    print(f"Session State: {session}")  # Log the session state
    print(f"User Type: {session.get('user_type')}")  # Log the user type

    if session.get('user_type') != 'admin':
        print("Redirecting to login due to invalid user type.")  # Log redirection reason
        print(f"Current Session State before redirect: {session}")  # Log current session state before redirect

        print(f"Current Session State: {session}")  # Log current session state before redirect


        return redirect(url_for('main.login'))

    club_name = request.form['clubName']
    club_id = request.form['clubId']
    club_leader_id = request.form['clubLeaderId']
    description = request.form['description']
    coordinator = request.form['coordinator']
    coordinator_contact = request.form['coordinatorContact']

    try:
        # Check if club with same ID already exists
        existing_club = Club.query.filter_by(club_id=club_id).first()
        if existing_club:
            flash('A club with this ID already exists!')
            return redirect(url_for('main.adclubs'))

        # Validate club leader exists
        club_leader = ClubLeader.query.get(club_leader_id)
        if not club_leader:
            flash('Invalid Club Leader ID!')
            return redirect(url_for('main.adclubs'))

        new_club = Club(
            club_id=club_id,
            club_name=club_name,
            club_leader=club_leader_id,
            description=description,
            coordinator_name=coordinator,
            coordinator_contact=coordinator_contact
        )

        db.session.add(new_club)
        db.session.commit()
        print(f"Club created: {new_club.club_name} with ID: {new_club.club_id}")
        flash('Club created successfully!', 'success')

        return redirect(url_for('main.adclubs', _external=True))

    except Exception as e:
        db.session.rollback()
        print(f"Error creating club: {str(e)}")
        flash('Failed to create club. Please check the details and try again.')
        return redirect(url_for('main.adclubs'))
