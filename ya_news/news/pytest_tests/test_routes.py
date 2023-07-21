import pytest
from http import HTTPStatus

from pytest_django.asserts import assertRedirects
from django.urls import reverse


@pytest.mark.django_db
def test_home_availability_for_anonymous_user(client):
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_detail_availability_for_anonymous_user(client, create_news):
    url = reverse('news:detail', args=(create_news.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
    ),
)
@pytest.mark.parametrize('name', ('news:delete', 'news:edit'))
def test_pages_availability_for_author(
    parametrized_client, expected_status, name, create_comment
):
    url = reverse(name, args=(create_comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize('name', ('news:delete', 'news:edit'))
def test_redirects_anonimous_user(client, name, create_comment):
    login_url = reverse('users:login')
    url = reverse(name, args=(create_comment.id,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'name', ('users:login', 'users:logout', 'users:signup')
)
def test_pages_availability_for_anonymous_user(client, name):
    url = reverse(name)  # Получаем ссылку на нужный адрес.
    response = client.get(url)  # Выполняем запрос.
    assert response.status_code == HTTPStatus.OK
