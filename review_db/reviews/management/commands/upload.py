import csv
import os

from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth import get_user_model

from reviews.models import (
    Category,
    Genre,
    GenreTitle,
    Title,
    Review,
    Comment
)

User = get_user_model()


def category_create(row):
    Category.objects.get_or_create(
        name=row[0],
        slug=row[1],
    )


def genre_create(row):
    Genre.objects.get_or_create(
        name=row[0],
        slug=row[1],
    )


def titles_create(row):
    Title.objects.get_or_create(
        name=row[0],
        year=row[1],
        description=row[2],
        category_id=row[3],
    )


def genre_title_create(row):
    GenreTitle.objects.get_or_create(
        genre_id=row[1],
        title_id=row[0],
    )


def users_create(row):
    User.objects.get_or_create(
        username=row[0],
        email=row[1],
    )


def review_create(row):
    Review.objects.get_or_create(
        title_id=row[0],
        text=row[1],
        author_id=row[2],
        score=row[3],
        pub_date=row[4]
    )


def comment_create(row):
    Comment.objects.get_or_create(
        review_id=row[0],
        text=row[1],
        author_id=row[2],
        pub_date=row[3],
    )


action = {
    'category.csv': category_create,
    'genre.csv': genre_create,
    'titles.csv': titles_create,
    'genre_title.csv': genre_title_create,
    'users.csv': users_create,
    'review.csv': review_create,
    'comments.csv': comment_create,
}


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            'filename',
            nargs='+',
            type=str
        )

    def handle(self, *args, **options):
        for filename in options['filename']:
            path = os.path.join(settings.BASE_DIR, "static/data/") + filename
            with open(path, 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)
                for row in reader:
                    action[filename](row)
