"""
Tests for views in Django 5.2
"""
import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from tlog.models import RadioProfile
from tlog.tests.factories import UserFactory, RadioProfileFactory


@pytest.mark.django_db
class TestDashboardView:
    """Tests for dashboard view"""

    def test_dashboard_requires_login(self):
        """Test that dashboard requires authentication"""
        client = Client()
        response = client.get(reverse('dashboard'))

        assert response.status_code == 302  # Redirect to login

    def test_dashboard_authenticated(self):
        """Test dashboard for authenticated user"""
        user = UserFactory(username='RA9XYZ', password='testpass123')
        client = Client()
        client.force_login(user)

        response = client.get(reverse('dashboard'))

        assert response.status_code == 200


@pytest.mark.django_db
class TestProfileUpdateView:
    """Tests for profile update view (Django 5.2)"""

    def test_profile_update_requires_login(self):
        """Test that profile update requires authentication"""
        client = Client()
        response = client.get(reverse('dashboard'))

        assert response.status_code == 302

    def test_profile_update_post(self):
        """Test profile update via POST"""
        user = UserFactory(
            username='RA9XYZ',
            first_name='Ivan',
            last_name='Ivanov'
        )
        RadioProfileFactory(user=user)

        client = Client()
        client.force_login(user)

        response = client.post(reverse('profile_update'), {
            'callsign': 'RA9XYZ',
            'first_name': 'Petr',
            'last_name': 'Petrov',
            'qth': 'Moscow',
            'my_gridsquare': 'KO85UU'
        })

        # Should redirect to dashboard
        assert response.status_code == 302

        # Verify profile was updated
        user.radio_profile.refresh_from_db()
        assert user.radio_profile.first_name == 'Petr'
        assert user.radio_profile.last_name == 'Petrov'


@pytest.mark.django_db
class TestAuthViews:
    """Tests for authentication views"""

    def test_login_page(self):
        """Test login page renders correctly"""
        client = Client()
        response = client.get(reverse('login_page'))

        assert response.status_code == 200

    def test_register_page(self):
        """Test register page renders correctly"""
        client = Client()
        response = client.get(reverse('register_page'))

        assert response.status_code == 200

    def test_logout(self):
        """Test logout redirects to home"""
        user = UserFactory()
        client = Client()
        client.force_login(user)

        response = client.get(reverse('logout'))

        assert response.status_code == 302
        assert response.url == reverse('home')