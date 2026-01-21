"""
Factories for testing Django 5.2 application
"""
import factory
from django.contrib.auth.models import User
from tlog.models import RadioProfile, QSO, ADIFUpload


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating User instances"""
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'testuser{n:03d}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True


class RadioProfileFactory(factory.django.DjangoModelFactory):
    """Factory for creating RadioProfile instances"""
    class Meta:
        model = RadioProfile

    user = factory.SubFactory(UserFactory)
    callsign = factory.Sequence(lambda n: f'RA{n:03d}XYZ')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    qth = factory.Faker('city')
    my_gridsquare = factory.LazyFunction(lambda: 'KO85UU')
    my_callsigns = factory.LazyFunction(lambda: [])


class QSOFactory(factory.django.DjangoModelFactory):
    """Factory for creating QSO instances"""
    class Meta:
        model = QSO

    user = factory.SubFactory(UserFactory)
    my_callsign = factory.Sequence(lambda n: f'RA{n:03d}XYZ')
    counterpart_callsign = factory.Sequence(lambda n: f'UA{n:03d}ABC')
    frequency = factory.Faker('pyfloat', left=1.8, right=30.0)
    mode = factory.Iterator(['SSB', 'CW', 'FT8', 'FM', 'AM'])
    band = factory.Iterator(['160m', '80m', '40m', '20m', '15m', '10m'])
    date = factory.Faker('date_this_year')
    time = factory.Faker('time')
    signal_report = factory.Iterator(['59', '59+', '599', 'RST'])
    my_gridsquare = factory.LazyFunction(lambda: 'KO85UU')
    counterpart_gridsquare = factory.LazyFunction(lambda: 'LO85AA')


class ADIFUploadFactory(factory.django.DjangoModelFactory):
    """Factory for creating ADIFUpload instances"""
    class Meta:
        model = ADIFUpload

    user = factory.SubFactory(UserFactory)
    file_name = factory.Sequence(lambda n: f'test_log_{n:03d}.adi')
    qso_count = factory.LazyFunction(lambda: 10)
    processed = True