"""Test fixtures for pytest"""
import pytest
from uuid import uuid4


@pytest.fixture
def sample_case():
    """Sample case for testing"""
    return {
        'id': str(uuid4()),
        'type': 'homeless',
        'title': 'Personne sans-abri dans le froid',
        'description': 'Homme seul, environ 50 ans, besoin d\'aide urgente',
        'location': {
            'latitude': 48.8566,
            'longitude': 2.3522
        },
        'urgency_level': 8,
        'ai_classification': {
            'confidence': 0.95,
            'skills_needed': ['medical', 'shelter']
        },
        'status': 'open'
    }


@pytest.fixture
def sample_volunteer():
    """Sample volunteer for testing"""
    return {
        'id': str(uuid4()),
        'user_id': str(uuid4()),
        'user': {
            'full_name': 'Jean Dupont',
            'email': 'jean@example.com'
        },
        'location': {
            'latitude': 48.8606,
            'longitude': 2.3376
        },
        'skills': ['medical', 'transport', 'shelter'],
        'languages': ['fr', 'en'],
        'certifications': {
            'medical_certified': True,
            'first_aid': True,
            'driver_license': True
        },
        'availability_status': True,
        'verification_status': 'verified',
        'reliability_score': 95.5,
        'total_cases_completed': 15,
        'total_hours_volunteered': 45,
        'average_rating': 4.8,
        'max_distance_km': 10
    }


@pytest.fixture
def sample_volunteers_list():
    """List of sample volunteers for testing"""
    volunteers = []
    
    # Volunteer 1: High match - close, skilled
    volunteers.append({
        'id': str(uuid4()),
        'user': {'full_name': 'Marie Martin'},
        'location': {'latitude': 48.8606, 'longitude': 2.3376},
        'skills': ['medical', 'shelter'],
        'certifications': {'medical_certified': True},
        'availability_status': True,
        'reliability_score': 95.0
    })
    
    # Volunteer 2: Medium match - farther, different skills
    volunteers.append({
        'id': str(uuid4()),
        'user': {'full_name': 'Pierre Durand'},
        'location': {'latitude': 48.9000, 'longitude': 2.4000},
        'skills': ['transport', 'food'],
        'certifications': {},
        'availability_status': True,
        'reliability_score': 85.0
    })
    
    # Volunteer 3: Low match - far, not available
    volunteers.append({
        'id': str(uuid4()),
        'user': {'full_name': 'Sophie Bernard'},
        'location': {'latitude': 48.9500, 'longitude': 2.5000},
        'skills': ['legal', 'psychological'],
        'certifications': {},
        'availability_status': False,
        'reliability_score': 75.0
    })
    
    return volunteers
