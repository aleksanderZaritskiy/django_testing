# conftest.py
from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone

import pytest

# Импортируем модель заметки, чтобы создать экземпляр.
from news.models import Comment, News


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор комментария')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def create_news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст заметки',
    )
    return news


@pytest.fixture
def pk_for_args(create_news):
    return (create_news.id,)


@pytest.fixture
def create_comment(create_news, author):
    comment = Comment.objects.create(
        news=create_news,
        author=author,
        text='Текст комментария',
    )
    return comment


@pytest.fixture
def slug_for_args(create_comment):
    return (create_comment.id,)


@pytest.fixture
def order_comment(create_news, author):
    now = timezone.now()
    comments = [
        Comment(
            news=create_news,
            author=author,
            text=f'Текст{index}',
            created=now + timedelta(days=index),
        )
        for index in range(2)
    ]
    return Comment.objects.bulk_create(comments)


@pytest.fixture
def all_news():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index),
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    return News.objects.bulk_create(all_news)


@pytest.fixture
def form_data():
    return {
        'text': 'Новый комментарий',
    }
