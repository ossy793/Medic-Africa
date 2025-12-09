from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import db
from models.appointment import Appointment
from datetime import datetime

appointments_bp = Blueprint('appointments', __name__)


@appointments_bp.route('', methods=['GET'])
@jwt_required()
def get_appointments():
    user_id = int(get_jwt_identity())
    appointments = Appointment.query.filter_by(user_id=user_id).order_by(Appointment.appointment_date.desc()).all()
    return jsonify([apt.to_dict() for apt in appointments]), 200


@appointments_bp.route('', methods=['POST'])
@jwt_required()
def create_appointment():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    required_fields = ['doctor_name', 'department', 'appointment_date']
    if not all(k in data for k in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    appointment = Appointment(
        user_id=user_id,
        doctor_name=data['doctor_name'],
        department=data['department'],
        appointment_date=datetime.fromisoformat(data['appointment_date'].replace('Z', '+00:00')),
        symptoms=data.get('symptoms')
    )

    db.session.add(appointment)
    db.session.commit()

    return jsonify({
        'message': 'Appointment created successfully',
        'appointment': appointment.to_dict()
    }), 201


@appointments_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_appointment(id):
    user_id = int(get_jwt_identity())
    appointment = Appointment.query.filter_by(id=id, user_id=user_id).first()

    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404

    data = request.get_json()

    if 'status' in data:
        appointment.status = data['status']
    if 'appointment_date' in data:
        appointment.appointment_date = datetime.fromisoformat(data['appointment_date'].replace('Z', '+00:00'))

    db.session.commit()

    return jsonify(appointment.to_dict()), 200


@appointments_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_appointment(id):
    user_id = int(get_jwt_identity())
    appointment = Appointment.query.filter_by(id=id, user_id=user_id).first()

    if not appointment:
        return jsonify({'error': 'Appointment not found'}), 404

    db.session.delete(appointment)
    db.session.commit()

    return jsonify({'message': 'Appointment deleted successfully'}), 200

