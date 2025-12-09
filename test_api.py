import requests
import random
import string

BASE_URL = 'http://localhost:5000/api'


# --- Helper Functions ---

def random_email():
    """Generate a random email to avoid duplicates on each run."""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6)) + '@example.com'


def register_user():
    """Register a new user and return the JWT access token."""
    email = random_email()
    data = {
        'email': email,
        'password': 'password123',
        'full_name': 'John Doe',
        'phone': '+234123456789'
    }
    response = requests.post(f'{BASE_URL}/auth/register', json=data)
    print("Register:", response.json())
    return response.json().get('access_token')


def create_appointment(token):
    """Create an appointment using the JWT token."""
    headers = {'Authorization': f'Bearer {token}'}
    data = {
        'doctor_name': 'Dr. Smith',
        'department': 'Cardiology',
        'appointment_date': '2025-12-10T10:00:00',
        'symptoms': 'Chest pain'
    }
    response = requests.post(f'{BASE_URL}/appointments', json=data, headers=headers)
    print("Create Appointment:", response.json())
    return response.json().get('appointment', {}).get('id')


def check_in_queue(token, appointment_id=None):
    """Check in patient to the queue."""
    headers = {'Authorization': f'Bearer {token}'}
    data = {
        'department': 'Cardiology',
        'priority': 'normal'
    }
    if appointment_id:
        data['appointment_id'] = appointment_id

    response = requests.post(f'{BASE_URL}/queue/check-in', json=data, headers=headers)
    print("Check-in:", response.json())
    return response.json().get('queue', {}).get('id')


def get_queue():
    """Get current queue list."""
    response = requests.get(f'{BASE_URL}/queue')
    print("Queue:", response.json())


def get_my_position(token):
    """Get current user's position in the queue."""
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{BASE_URL}/queue/my-position', headers=headers)
    print("My Queue Position:", response.json())


# --- Run Tests ---
if __name__ == '__main__':
    token = register_user()

    if token:
        appointment_id = create_appointment(token)
        queue_id = check_in_queue(token, appointment_id)
        get_queue()
        get_my_position(token)
    else:
        print("Registration failed. Cannot run further tests.")

