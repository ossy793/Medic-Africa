"""
Models package initialization
Centralizes all database models for easy importing
"""

from models.user import db, User
from models.appointment import Appointment
from models.queue import Queue
from models.news import News

# Export all models and db instance
__all__ = [
    'db',
    'User',
    'Appointment',
    'Queue',
    'News'
]
