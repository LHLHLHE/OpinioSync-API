import pytest
from django.contrib.auth.hashers import check_password
from rest_framework import status
from rest_framework.test import APIClient

from api.tests import constants
from api.tests.constants import TEST_USER_ID
from users.models import CustomUser
from reviews.models import Title, Review, Comment


@pytest.mark.django_db
class TestUserEndpoint:
    def test_get_user_me(self, create_user, user_client):
        expected_fields = {
            'id',
            'email',
            'username',
            'photo'
        }

        response = user_client.get('/api/v1/users/me/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('id') == TEST_USER_ID
        assert set(response.data.keys()) == expected_fields

    def test_create_user(self, create_test_user_data):
        expected_fields = {
            'id',
            'email',
            'username',
            'photo'
        }

        response = APIClient().post(
            '/api/v1/users/',
            data=create_test_user_data,
            format='json'
        )
        user = CustomUser.objects.filter(
            username=create_test_user_data.get('username')
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert user.exists()
        assert set(response.data.keys()) == expected_fields

    def test_login_user(self, create_user, login_test_user_data):
        expected_fields = {'auth_token'}

        response = APIClient().post(
            '/api/v1/auth/token/login/',
            data=login_test_user_data,
            format='json'
        )

        assert response.status_code == status.HTTP_200_OK
        assert set(response.data.keys()) == expected_fields

    def test_set_username(self, create_user, user_client, set_username_test_data):
        response = user_client.post(
            '/api/v1/users/set_username/',
            data=set_username_test_data,
            format='json'
        )
        updated_user = CustomUser.objects.get(id=constants.TEST_USER_ID)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert updated_user.username == set_username_test_data.get('new_username')

    def test_set_email(self, create_user, user_client, set_email_test_data):
        response = user_client.post(
            '/api/v1/users/set_email/',
            data=set_email_test_data,
            format='json'
        )
        updated_user = CustomUser.objects.get(id=constants.TEST_USER_ID)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert updated_user.email == set_email_test_data.get('new_email')

    def test_set_pasword(self, create_user, user_client, set_password_test_data):
        response = user_client.post(
            '/api/v1/users/set_password/',
            data=set_password_test_data,
            format='json'
        )
        updated_user = CustomUser.objects.get(id=constants.TEST_USER_ID)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert check_password(
            set_password_test_data.get('new_password'),
            updated_user.password
        )


@pytest.mark.django_db
class TestReviewsEndpoint:
    def test_get_categories(self, fill_db_categories):
        expected_fields = {'name', 'slug'}

        response = APIClient().get('/api/v1/categories/')

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert set(response.data[0].keys()) == expected_fields

    def test_get_genres(self, fill_db_genres):
        expected_fields = {'name', 'slug'}

        response = APIClient().get('/api/v1/genres/')

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert set(response.data[0].keys()) == expected_fields

    def test_get_titles(
        self,
        fill_db_categories,
        fill_db_genres,
        fill_db_titles,
        add_genres_to_titles
    ):
        expected_fields = {
            'id',
            'genre',
            'category',
            'rating',
            'name',
            'year',
            'description',
            'photo'
        }
        expected_category_genre_fields = {'name', 'slug'}

        response = APIClient().get('/api/v1/titles/')

        first_title = response.data[0]
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert set(first_title.keys()) == expected_fields
        assert set(first_title.get('category')) == expected_category_genre_fields
        assert isinstance(first_title.get('genre'), list)
        assert set(first_title.get('genre')[0]) == expected_category_genre_fields

    def test_get_title_by_id(
        self,
        fill_db_categories,
        fill_db_genres,
        fill_db_titles,
        add_genres_to_titles
    ):
        expected_fields = {
            'id',
            'genre',
            'category',
            'rating',
            'name',
            'year',
            'description',
            'photo'
        }
        expected_category_genre_fields = {'name', 'slug'}
        title = Title.objects.first()

        response = APIClient().get(f'/api/v1/titles/{title.id}/')

        response_data = response.data
        assert response.status_code == status.HTTP_200_OK
        assert set(response_data.keys()) == expected_fields
        assert response_data.get('id') == title.id
        assert set(response_data.get('category')) == expected_category_genre_fields
        assert isinstance(response_data.get('genre'), list)
        assert set(response_data.get('genre')[0]) == expected_category_genre_fields


@pytest.mark.django_db
class TestReviewsEndpoint:
    def test_get_title_reviews(
        self,
        fill_db_categories,
        fill_db_titles,
        fill_db_users,
        fill_db_reviews
    ):
        expected_fields = {
            'id',
            'author',
            'title',
            'score',
            'pub_date',
            'text',
        }
        title_id = Review.objects.first().title.id

        response = APIClient().get(f'/api/v1/titles/{title_id}/reviews/')

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert set(response.data[0].keys()) == expected_fields

    def test_get_review_by_id(
        self,
        fill_db_categories,
        fill_db_titles,
        fill_db_users,
        fill_db_reviews
    ):
        expected_fields = {
            'id',
            'author',
            'title',
            'score',
            'pub_date',
            'text',
        }
        review = Review.objects.first()
        title_id = review.title.id
        review_id = review.id

        response = APIClient().get(f'/api/v1/titles/{title_id}/reviews/{review_id}/')

        assert response.status_code == status.HTTP_200_OK
        assert set(response.data.keys()) == expected_fields
        assert response.data.get('id') == review_id
        assert response.data.get('title') == title_id

    def test_create_review(
        self,
        fill_db_categories,
        fill_db_titles,
        create_user,
        user_client,
        create_test_review_data
    ):
        expected_fields = {
            'id',
            'author',
            'title',
            'score',
            'pub_date',
            'text',
        }
        title_id = Title.objects.first().id

        response = user_client.post(
            f'/api/v1/titles/{title_id}/reviews/',
            data=create_test_review_data,
            format='json'
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert Review.objects.filter(
            title_id=title_id,
            author_id=constants.TEST_USER_ID,
            score=create_test_review_data.get('score'),
            text=create_test_review_data.get('text')
        ).exists()
        assert set(response.data.keys()) == expected_fields
        assert response.data.get('title') == title_id
        assert response.data.get('score') == create_test_review_data.get('score')
        assert response.data.get('text') == create_test_review_data.get('text')

    def test_patch_review(
        self,
        create_title,
        create_user,
        user_client,
        create_review,
        patch_test_review_data
    ):
        expected_fields = {
            'id',
            'author',
            'title',
            'score',
            'pub_date',
            'text',
        }
        review = create_review
        title_id = review.title.id
        review_id = review.id

        response = user_client.patch(
            f'/api/v1/titles/{title_id}/reviews/{review_id}/',
            data=patch_test_review_data,
            format='json'
        )
        patched_review = Review.objects.get(id=review_id)

        assert response.status_code == status.HTTP_200_OK
        assert patched_review.score == patch_test_review_data.get('score')
        assert patched_review.text == patch_test_review_data.get('text')
        assert set(response.data.keys()) == expected_fields

    def test_delete_review(
        self,
        create_title,
        create_user,
        user_client,
        create_review
    ):
        review = create_review
        title_id = review.title.id
        review_id = review.id

        response = user_client.delete(
            f'/api/v1/titles/{title_id}/reviews/{review_id}/'
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Review.objects.filter(id=review_id).exists()


@pytest.mark.django_db
class TestCommentsEndpoint:
    def test_get_review_comments(
        self,
        fill_db_categories,
        fill_db_titles,
        fill_db_users,
        fill_db_reviews,
        fill_db_comments
    ):
        expected_fields = {
            'id',
            'author',
            'review',
            'pub_date',
            'text',
        }

        review = Comment.objects.first().review
        title_id = review.title.id
        review_id = review.id

        response = APIClient().get(
            f'/api/v1/titles/{title_id}/reviews/{review_id}/comments/'
        )

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert set(response.data[0].keys()) == expected_fields
        assert response.data[0].get('review') == review_id

    def test_create_comment(
        self,
        create_title,
        create_user,
        user_client,
        create_review,
        create_test_comment_data
    ):
        expected_fields = {
            'id',
            'author',
            'review',
            'pub_date',
            'text',
        }
        title_id = create_title.id
        review_id = create_review.id

        response = user_client.post(
            f'/api/v1/titles/{title_id}/reviews/{review_id}/comments/',
            data=create_test_comment_data,
            format='json'
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert Comment.objects.filter(
            author_id=constants.TEST_USER_ID,
            review_id=review_id,
            text=create_test_comment_data.get('text')
        ).exists()
        assert set(response.data.keys()) == expected_fields
        assert response.data.get('review') == review_id
        assert response.data.get('text') == create_test_comment_data.get('text')

    def test_patch_comment(
        self,
        create_title,
        create_user,
        user_client,
        create_review,
        create_comment,
        patch_test_comment_data
    ):
        expected_fields = {
            'id',
            'author',
            'review',
            'pub_date',
            'text',
        }
        comment = create_comment
        comment_id = comment.id
        review = comment.review
        title_id = review.title.id
        review_id = review.id

        response = user_client.patch(
            f'/api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/',
            data=patch_test_comment_data,
            format='json'
        )
        patched_comment = Comment.objects.get(id=comment_id)

        assert response.status_code == status.HTTP_200_OK
        assert patched_comment.text == patch_test_comment_data.get('text')
        assert set(response.data.keys()) == expected_fields

    def test_delete_comment(
        self,
        create_title,
        create_user,
        user_client,
        create_review,
        create_comment
    ):
        comment = create_comment
        comment_id = comment.id
        review = comment.review
        title_id = review.title.id
        review_id = review.id

        response = user_client.delete(
            f'/api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}/'
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Comment.objects.filter(id=comment_id).exists()
