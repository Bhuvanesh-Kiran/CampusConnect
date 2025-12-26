from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from app import db, login_manager

# User Types Table
class UserTypes(db.Model):
    __tablename__ = 'usertypes'
    type_id = db.Column(db.Integer, primary_key=True)
    user_type = db.Column(db.String(50), nullable=False)

# Administrator Table
class Administrator(db.Model, UserMixin):
    __tablename__ = 'administrator'
    admin_id = db.Column(db.Integer, primary_key=True)
    type_id = db.Column(db.Integer, db.ForeignKey('usertypes.type_id'), default=1, unique=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(15), unique=True, nullable=False)

    def get_id(self):
        return str(self.admin_id)  # Required by Flask-Login

    @property
    def is_active(self):
        return True

# Club Leader Table
class ClubLeader(db.Model, UserMixin):
    __tablename__ = 'club_leaders'
    leader_id = db.Column(db.Integer, primary_key=True)
    type_id = db.Column(db.Integer, db.ForeignKey('usertypes.type_id'))
    full_name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    regd_number = db.Column(db.String(20), nullable=False)
    batch = db.Column(db.Integer, nullable=False)  # Added batch column
    gender = db.Column(db.Enum('Male', 'Female', 'Other'), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    assigned_club = db.Column(db.Integer, db.ForeignKey('clubs.club_id'))  # Added assigned_club column

    # Relationships
    club = db.relationship('Club', foreign_keys=[assigned_club], backref='club_leader_rel', uselist=False)  # Specify foreign_keys and unique backref

    def get_id(self):
        return str(self.leader_id)

    @property
    def is_active(self):
        return True

# Student Table
class Student(db.Model, UserMixin):
    __tablename__ = 'students'
    student_id = db.Column(db.Integer, primary_key=True)
    type_id = db.Column(db.Integer, db.ForeignKey('usertypes.type_id'))
    full_name = db.Column(db.String(100), nullable=False)
    regd_number = db.Column(db.String(20), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    academic_year = db.Column(db.Integer, nullable=False)
    batch = db.Column(db.Integer, nullable=False)  # Added batch column
    gender = db.Column(db.Enum('Male', 'Female', 'Other'), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(15), unique=True, nullable=False)

    def get_id(self):
        return str(self.student_id)

    @property
    def is_active(self):
        return True

# Clubs Table
class Club(db.Model):
    __tablename__ = 'clubs'
    club_id = db.Column(db.Integer, primary_key=True)
    club_name = db.Column(db.String(100), nullable=False, unique=True)
    club_leader = db.Column(db.Integer, db.ForeignKey('club_leaders.leader_id'), unique=True)
    coordinator_name = db.Column(db.String(100), nullable=False)
    coordinator_contact = db.Column(db.String(100), nullable=False)
    total_members = db.Column(db.Integer, default=0)
    total_feedbacks = db.Column(db.Integer, default=0)
    events_hosted = db.Column(db.Integer, default=0)
    description = db.Column(db.Text)

    # Relationships
    leader = db.relationship('ClubLeader', foreign_keys=[club_leader], backref='assigned_club_rel', uselist=False)  # Specify foreign_keys and unique backref

# Club Members Table
class ClubMember(db.Model):
    __tablename__ = 'club_members'
    membership_id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.club_id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)

    # Relationships
    club = db.relationship('Club', backref='members')
    student = db.relationship('Student', backref='club_memberships')

# News Table
class News(db.Model):
    __tablename__ = 'news'
    news_id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.club_id'))
    club_name = db.Column(db.String(100), nullable=False)
    headline = db.Column(db.String(255), nullable=False)
    news_date = db.Column(db.Date, nullable=False)
    news = db.Column(db.Text, nullable=False)

    # Relationships
    club = db.relationship('Club', backref='news')

# Events Table
class Event(db.Model):
    __tablename__ = 'events'
    event_id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.club_id'))
    club_name = db.Column(db.String(100), nullable=False)
    headline = db.Column(db.String(255), nullable=False)
    event_date = db.Column(db.Date, nullable=False)
    event_details = db.Column(db.Text, nullable=False)
    photos = db.Column(db.Text)  # Can store image URLs or paths

    # Relationships
    club = db.relationship('Club', backref='events')
# Gallery Table
class Gallery(db.Model):
    __tablename__ = 'gallery'
    media_id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.club_id'))
    club_name = db.Column(db.String(100), nullable=False)
    photo_name = db.Column(db.String(255))  # Alternative text for the photo
    photo_url = db.Column(db.Text)  # Stores the image URL or file path
    video_name = db.Column(db.String(255))  # Alternative text for the video
    video_url = db.Column(db.Text)  # Stores the video URL or file path

    # Relationships
    club = db.relationship('Club', backref='gallery')

# Feedback Table
class Feedback(db.Model):
    __tablename__ = 'feedback'
    feedback_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'))
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.club_id'))
    club_name = db.Column(db.String(100), nullable=False)
    feedback_text = db.Column(db.Text, nullable=False)
    feedback_date = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

    # Relationships
    student = db.relationship('Student', backref='feedbacks')
    club = db.relationship('Club', backref='feedbacks')

# Joining Requests Table
class JoiningRequest(db.Model):
    __tablename__ = 'joining_requests'
    request_id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.club_id'))
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'))
    request_date = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    status = db.Column(db.Enum('Pending', 'Approved', 'Rejected'), default='Pending')

    # Relationships
    club = db.relationship('Club', backref='joining_requests')
    student = db.relationship('Student', backref='joining_requests')

# Activities Table
class Activity(db.Model):
    __tablename__ = 'activities'
    activity_id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.club_id'), nullable=False)
    activity_name = db.Column(db.String(255), nullable=False)
    activity_date = db.Column(db.Date, nullable=False)
    activity_time = db.Column(db.Time, nullable=False)
    description = db.Column(db.Text)
    venue = db.Column(db.String(255), nullable=False)
    interested_count = db.Column(db.Integer, default=0)

    # Relationships
    club = db.relationship('Club', backref='activities')

# Interested Table
class Interested(db.Model):
    __tablename__ = 'interested'
    interested_id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.club_id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.activity_id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)

    # Relationships
    club = db.relationship('Club', backref='interested')
    activity = db.relationship('Activity', backref='interested')
    student = db.relationship('Student', backref='interested')

# Notifications Table
class Notification(db.Model):
    __tablename__ = 'notifications'
    notification_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum('unread', 'read'), default='unread')
    timestamp = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

    # Relationships
    student = db.relationship('Student', backref='notifications')

# User Loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    user = Administrator.query.get(int(user_id)) or ClubLeader.query.get(int(user_id)) or Student.query.get(int(user_id))
    return user