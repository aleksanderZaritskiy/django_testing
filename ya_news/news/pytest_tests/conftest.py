# conftest.py
import pytest
from datetime import datetime, timedelta
from django.utils import timezone

# Импортируем модель заметки, чтобы создать экземпляр.
from news.models import Comment, News
from django.conf import settings


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
def create_comment(create_news, author):
    comment = Comment.objects.create(
        news=create_news,
        author=author,
        text='Текст комментария',
    )
    return comment


@pytest.fixture
def order_comment(create_news, author):
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=create_news,
            author=author,
            text=f'Текст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()


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
