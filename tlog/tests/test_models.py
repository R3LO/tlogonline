"""
Tests for Django 5.2 compatibility
"""
import pytest
from django.contrib.auth.models import User
from tlog.models import RadioProfile, QSO
from tlog.tests.factories import UserFactory, RadioProfileFactory, QSOFactory


@pytest.mark.django_db
class TestUserModel:
    """Tests for User model in Django 5.2"""

    def test_create_user(self):
        """Test creating a user"""
        user = UserFactory(username='test_callsign')
        user.set_password('testpass123')
        user.save()

        assert user.username == 'test_callsign'
        assert user.is_active is True

    def test_user_first_name_last_name(self):
        """Test user first_name and last_name fields (Django 5.2)"""
        user = UserFactory(
            username='RA9XYZ',
            first_name='Ivan',
            last_name='Ivanov'
        )
        user.save()

        assert user.first_name == 'Ivan'
        assert user.last_name == 'Ivanov'


@pytest.mark.django_db
class TestRadioProfileModel:
    """Tests for RadioProfile model in Django 5.2"""

    def test_create_profile(self):
        """Test creating a radio profile"""
        profile = RadioProfileFactory(
            callsign='RA9XYZ',
            first_name='Ivan',
            last_name='Ivanov',
            qth='Moscow',
            my_gridsquare='KO85UU'
        )

        assert profile.callsign == 'RA9XYZ'
        assert profile.first_name == 'Ivan'
        assert profile.last_name == 'Ivanov'
        assert profile.my_gridsquare == 'KO85UU'

    def test_profile_str(self):
        """Test profile string representation"""
        profile = RadioProfileFactory(callsign='RA9XYZ')

        assert str(profile) == 'Profile - testuser000 (RA9XYZ)'


@pytest.mark.django_db
class TestQSO:
    """Tests for QSO model"""

    def test_create_qso(self):
        """Test creating a QSO record"""
        qso = QSOFactory(
            my_callsign='RA9XYZ',
            counterpart_callsign='UA1ABC',
            frequency=14.205,
            mode='SSB'
        )

        assert qso.my_callsign == 'RA9XYZ'
        assert qso.counterpart_callsign == 'UA1ABC'
        assert qso.frequency == 14.205
        assert qso.mode == 'SSB'

    def test_qso_str(self):
        """Test QSO string representation"""
        qso = QSOFactory(
            my_callsign='RA9XYZ',
            counterpart_callsign='UA1ABC'
        )

        assert 'RA9XYZ' in str(qso)
        assert 'UA1ABC' in str(qso)


@pytest.mark.django_db
class TestProfileUpdate:
    """Tests for profile update functionality (Django 5.2)"""

    def test_profile_update_first_name_last_name(self):
        """Test updating first_name and last_name"""
        profile = RadioProfileFactory(
            first_name='Ivan',
            last_name='Ivanov'
        )

        # Update profile
        profile.first_name = 'Petr'
        profile.last_name='Petrov'
        profile.save()

        # Verify User model was also updated
        profile.user.refresh_from_db()
        assert profile.user.first_name == 'Petr'
        assert profile.user.last_name == 'Petrov'