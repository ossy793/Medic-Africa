from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import db
from models.queue import Queue
from datetime import datetime
from sqlalchemy import func

queue_bp = Blueprint('queue', __name__)


@queue_bp.route('', methods=['GET'])
def get_queue():
    """Get all active queue entries"""
    department = request.args.get('department')

    query = Queue.query.filter(Queue.status.in_(['waiting', 'in-progress']))

    if department:
        query = query.filter_by(department=department)

    queue_entries = query.order_by(Queue.priority.desc(), Queue.check_in_time).all()

    return jsonify([entry.to_dict() for entry in queue_entries]), 200


@queue_bp.route('/check-in', methods=['POST'])
@jwt_required()
def check_in():
    """Patient checks in and joins queue"""
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if 'department' not in data:
        return jsonify({'error': 'Department is required'}), 400

    # Generate queue number
    last_queue = Queue.query.filter_by(department=data['department']).order_by(Queue.queue_number.desc()).first()
    queue_number = (last_queue.queue_number + 1) if last_queue else 1

    # Calculate estimated wait (assuming 15 mins per patient)
    waiting_count = Queue.query.filter_by(
        department=data['department'],
        status='waiting'
    ).count()
    estimated_wait = waiting_count * 15

    queue_entry = Queue(
        user_id=user_id,
        appointment_id=data.get('appointment_id'),
        queue_number=queue_number,
        department=data['department'],
        priority=data.get('priority', 'normal'),
        estimated_wait=estimated_wait
    )

    db.session.add(queue_entry)
    db.session.commit()

    return jsonify({
        'message': 'Checked in successfully',
        'queue': queue_entry.to_dict()
    }), 201


@queue_bp.route('/<int:id>/status', methods=['PUT'])
def update_queue_status(id):
    """Update queue status (for admin/reception)"""
    queue_entry = Queue.query.get(id)

    if not queue_entry:
        return jsonify({'error': 'Queue entry not found'}), 404

    data = request.get_json()

    if 'status' in data:
        queue_entry.status = data['status']

    db.session.commit()

    # Recalculate wait times for remaining patients
    if queue_entry.status == 'completed':
        waiting_entries = Queue.query.filter_by(
            department=queue_entry.department,
            status='waiting'
        ).order_by(Queue.check_in_time).all()

        for idx, entry in enumerate(waiting_entries):
            entry.estimated_wait = idx * 5

        db.session.commit()

    return jsonify(queue_entry.to_dict()), 200


@queue_bp.route('/my-position', methods=['GET'])
@jwt_required()
def get_my_position():
    """Get current user's queue position"""
    user_id = int(get_jwt_identity())

    queue_entry = Queue.query.filter_by(
        user_id=user_id,
        status='waiting'
    ).order_by(Queue.check_in_time.desc()).first()

    if not queue_entry:
        return jsonify({'message': 'Not in queue'}), 404

    # Calculate position
    position = Queue.query.filter(
        Queue.department == queue_entry.department,
        Queue.status == 'waiting',
        Queue.check_in_time < queue_entry.check_in_time
    ).count() + 1

    return jsonify({
        'queue': queue_entry.to_dict(),
        'position': position
    }), 200


@queue_bp.route('/updates', methods=['GET'])
def get_queue_updates():
    """Simple endpoint for frontend to poll"""
    last_update = request.args.get('last_update')

    # Return all recent updates
    recent_queues = Queue.query.filter(
        Queue.status.in_(['waiting', 'in-progress'])
    ).order_by(Queue.check_in_time.desc()).all()

    return jsonify({
        'timestamp': datetime.utcnow().isoformat(),
        'queue': [q.to_dict() for q in recent_queues]
    }), 200
