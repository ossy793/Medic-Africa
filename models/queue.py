from models.user import db
from datetime import datetime


class Queue(db.Model):
    __tablename__ = 'queue'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'))
    queue_number = db.Column(db.Integer, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='waiting')  # waiting, in-progress, completed
    priority = db.Column(db.String(20), default='normal')  # urgent, normal
    check_in_time = db.Column(db.DateTime, default=datetime.utcnow)
    estimated_wait = db.Column(db.Integer)  # in minutes

    # Relationships
    user = db.relationship('User', backref='queue_entries')
    appointment = db.relationship('Appointment', backref='queue_entry')

    def to_dict(self):
        return {
            'id': self.id,
            'queue_number': self.queue_number,
            'patient_name': self.user.full_name if self.user else 'Unknown',
            'department': self.department,
            'status': self.status,
            'priority': self.priority,
            'check_in_time': self.check_in_time.isoformat(),
            'estimated_wait': self.estimated_wait
        }

