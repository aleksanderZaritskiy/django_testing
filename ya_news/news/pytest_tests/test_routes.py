from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

PK_FOR_URL = 1


@pytest.mark.django_db
@pytest.mark.parametrize('name', ('news:delete', 'news:edit'))
def test_redirects_anonymous_user(client, name, create_comment):
    login_url = reverse('users:login')
    url = reverse(name, args=(create_comment.id,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'path, parametrize_client, expected_status',
    [
        (reverse('users:login'), pytest.lazy_fixture('client'), HTTPStatus.OK),
        (
            reverse('users:logout'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK,
        ),
        (
            reverse('users:signup'),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK,
        ),
        (reverse('news:home'), pytest.lazy_fixture('client'), HTTPStatus.OK),
        (
            reverse('news:detail', args=(PK_FOR_URL,)),
            pytest.lazy_fixture('client'),
            HTTPStatus.OK,
        ),
        (
            reverse('news:edit', args=(PK_FOR_URL,)),
            pytest.lazy_fixture('client'),
            HTTPStatus.FOUND,
        ),
        (
            reverse('news:delete', args=(PK_FOR_URL,)),
            pytest.lazy_fixture('client'),
            HTTPStatus.FOUND,
        ),
        (
            reverse('news:edit', args=(PK_FOR_URL,)),
            pytest.lazy_fixture('admin_client'),
            HTTPStatus.NOT_FOUND,
        ),
        (
            reverse('news:delete', args=(PK_FOR_URL,)),
            pytest.lazy_fixture('admin_client'),
            HTTPStatus.NOT_FOUND,
        ),
        (
            reverse('news:edit', args=(PK_FOR_URL,)),
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK,
        ),
        (
            reverse('news:delete', args=(PK_FOR_URL,)),
            pytest.lazy_fixture('author_client'),
            HTTPStatus.OK,
        ),
    ],
)
def test_availability_pages_for_users(
    create_news,
    create_comment,
    path,
    parametrize_client,
    expected_status,
):
    url = path
    response = parametrize_client.get(url)
    assert response.status_code == expected_status
