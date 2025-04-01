from app import db
from app.models import ClubLeader, Club

# Sample data for clubs
club1 = Club(club_name='Science Club', coordinator_name='Alice Smith', coordinator_contact='1234567890')
club2 = Club(club_name='Art Club', coordinator_name='Bob Johnson', coordinator_contact='0987654321')

# Sample data for club leaders
leader1 = ClubLeader(full_name='John Doe', department='Science', email='john@example.com', password='password', assigned_club=1)
leader2 = ClubLeader(full_name='Jane Smith', department='Arts', email='jane@example.com', password='password', assigned_club=2)

# Add to session and commit
db.session.add_all([club1, club2, leader1, leader2])
db.session.commit()
