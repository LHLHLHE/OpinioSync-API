import datetime as dt

import pytest
from django.core.management import call_command
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from api.tests import constants
from api.tests.factories import CustomUserFactory
from reviews.models import Review, Title, Comment

pytestmark = pytest.mark.django_db


@pytest.fixture(scope='session')
def user_client():
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION='Token ' + constants.TEST_USER_TOKEN)

    return client


@pytest.fixture
@pytest.mark.django_db
def create_user():
    user = CustomUserFactory.create(
        id=constants.TEST_USER_ID,
        username=constants.TEST_USER_USERNAME,
        email=constants.TEST_USER_EMAIL,
        is_active=True
    )
    Token.objects.create(key=constants.TEST_USER_TOKEN, user=user)


@pytest.fixture
@pytest.mark.django_db
def create_title(fill_db_categories):
    return Title.objects.create(
        id=constants.TEST_TITLE_ID,
        category_id=1,
        name='test_title',
        year=1999
    )


@pytest.fixture
@pytest.mark.django_db
def create_review():
    return Review.objects.create(
        id=constants.TEST_REVIEW_ID,
        title_id=constants.TEST_TITLE_ID,
        author_id=constants.TEST_USER_ID,
        pub_date=dt.datetime.now(),
        score=5,
        text='test text test text test text test text test text test text'
    )


@pytest.fixture
@pytest.mark.django_db
def create_comment():
    return Comment.objects.create(
        author_id=constants.TEST_USER_ID,
        review_id=constants.TEST_REVIEW_ID,
        text='test text test text test text test text test text test text'
    )


@pytest.fixture
def create_test_user_data():
    return {
        'email': 'test@example.com',
        'username': 'test_user',
        'password': 'SuperTestPass123',
        're_password': 'SuperTestPass123'
    }


@pytest.fixture
def login_test_user_data():
    return {
        'username': constants.TEST_USER_USERNAME,
        'password': constants.TEST_PASSWORD
    }


@pytest.fixture
def set_username_test_data():
    return {'new_username': 'new_username'}


@pytest.fixture
def set_email_test_data():
    return {'new_email': 'new@mail.ru'}


@pytest.fixture
def set_password_test_data():
    return {
        'current_password': constants.TEST_PASSWORD,
        'new_password': 'newSuperPass123',
        're_new_password': 'newSuperPass123'
    }


@pytest.fixture
def create_test_review_data():
    return {
        'score': 5,
        'text': 'efsdvsewfsfsevssevsfcsvds\nsfsfsfsfsdfsdfsdfsdfsdf'
    }


@pytest.fixture
def patch_test_review_data():
    return {
        'score': 1,
        'text': 'shit'
    }


@pytest.fixture
def create_test_comment_data():
    return {'text': 'efsdvsewfsfsevssevsfcsvds\nsfsfsfsfsdfsdfsdfsdfsdf'}


@pytest.fixture
def patch_test_comment_data():
    return {'text': 'shit'}


@pytest.fixture
@pytest.mark.django_db
def fill_db_categories():
    call_command('test_upload', 'category.csv')


@pytest.fixture
@pytest.mark.django_db
def fill_db_genres():
    call_command('test_upload', 'genre.csv')


@pytest.fixture
@pytest.mark.django_db
def fill_db_titles():
    call_command('test_upload', 'titles.csv')


@pytest.fixture
@pytest.mark.django_db
def add_genres_to_titles():
    call_command('test_upload', 'genre_title.csv')


@pytest.fixture
@pytest.mark.django_db
def fill_db_users():
    call_command('test_upload', 'users.csv')


@pytest.fixture
@pytest.mark.django_db
def fill_db_reviews():
    call_command('test_upload', 'review.csv')


@pytest.fixture
@pytest.mark.django_db
def fill_db_comments():
    call_command('test_upload', 'comments.csv')
