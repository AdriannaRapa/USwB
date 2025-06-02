import json
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class WebhookLog(db.Model):
    """
    Model for storing GitHub webhook data
    """
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(64), nullable=False)  # Type of GitHub event (push, pull_request, etc.)
    repository = db.Column(db.String(255), nullable=False)  # Repository name
    sender = db.Column(db.String(255))  # GitHub username of the sender
    branch = db.Column(db.String(255))  # Branch name (for push events)
    commit_count = db.Column(db.Integer, default=0)  # Number of commits (for push events)
    payload = db.Column(db.Text, nullable=False)  # Full JSON payload
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # When the webhook was received
    
    def __repr__(self):
        return f"<WebhookLog {self.id}: {self.event_type} to {self.repository}>"
    
    def to_dict(self):
        """Convert object to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'event_type': self.event_type,
            'repository': self.repository,
            'sender': self.sender,
            'branch': self.branch,
            'commit_count': self.commit_count,
            'payload': json.loads(self.payload) if self.payload else None,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }
    
    def get_summary(self):
        """Return a human-readable summary of the webhook"""
        if self.event_type == 'push':
            return f"{self.sender} pushed {self.commit_count} commit(s) to {self.branch} in {self.repository}"
        else:
            return f"{self.event_type} event from {self.sender} in {self.repository}"
