import factory
from django.contrib.auth.hashers import make_password
from factory.django import DjangoModelFactory
from faker import Faker

from api.tests import constants
from users.models import CustomUser

faker = Faker()


class CustomUserFactory(DjangoModelFactory):
    class Meta:
        model = CustomUser

    username = factory.Sequence(lambda n: f'username_{n + 1}')
    email = faker.email()
    password = factory.LazyFunction(lambda: make_password(constants.TEST_PASSWORD))
