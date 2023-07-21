import pytest

from django.urls import reverse
from django.conf import settings


@pytest.mark.django_db
def test_news_count(client, all_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, create_news, order_comment):
    url = reverse('news:detail', args=(create_news.id,))
    response = client.get(url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('admin_client'), True),
    ),
)
def test_comment_form_for_users(
    parametrized_client, expected_status, create_news
):
    url = reverse('news:detail', args=(create_news.id,))
    response = parametrized_client.get(url)
    assert ('form' in response.context) is expected_status
