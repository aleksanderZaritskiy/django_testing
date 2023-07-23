from http import HTTPStatus

from django.urls import reverse

import pytest
from pytest_django.asserts import assertRedirects


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
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('client'), HTTPStatus.FOUND),
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
    ),
)
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('pk_for_args')),
        ('news:edit', pytest.lazy_fixture('slug_for_args')),
        ('news:delete', pytest.lazy_fixture('slug_for_args')),
        ('news:home', None),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    ),
)
def test_availability_pages_for_users(
    parametrized_client,
    expected_status,
    name,
    args,
):
    url = reverse(name, args=args)
    if name in ['news:delete', 'news:edit']:
        # Для url-ов name: (delete, edit) у каждого user-а разные HTTP статус.
        response = parametrized_client.get(url)
        assert response.status_code == expected_status
    else:
        # Для всех остальных url-ов у всех
        # 3-х типов user-ов одинаковый HTTP статус.
        response = parametrized_client.get(url)
        assert response.status_code == HTTPStatus.OK
