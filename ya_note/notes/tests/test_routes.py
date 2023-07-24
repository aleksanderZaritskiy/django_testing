from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='тот ещё автор')
        cls.user = User.objects.create(username='залогиненый пользователь')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текс записи',
            slug='slug1',
            author=cls.author,
        )

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_pages_availability_for_users(self):
        # Содержит url, клиента и статус ответа.
        urls_optional_status_for_users = [
            (
                ('notes:home', None),
                [(self.client, HTTPStatus.OK)],
            ),
            (
                ('notes:add', None),
                [
                    (self.client, HTTPStatus.FOUND),
                    (self.auth_client, HTTPStatus.OK),
                ],
            ),
            (
                ('notes:list', None),
                [
                    (self.client, HTTPStatus.FOUND),
                    (self.auth_client, HTTPStatus.OK),
                ],
            ),
            (
                ('notes:success', None),
                [
                    (self.client, HTTPStatus.FOUND),
                    (self.auth_client, HTTPStatus.OK),
                ],
            ),
            (
                ('notes:edit', (self.note.slug,)),
                [
                    (self.client, HTTPStatus.FOUND),
                    (self.auth_client, HTTPStatus.NOT_FOUND),
                    (self.author_client, HTTPStatus.OK),
                ],
            ),
            (
                ('notes:delete', (self.note.slug,)),
                [
                    (self.client, HTTPStatus.FOUND),
                    (self.auth_client, HTTPStatus.NOT_FOUND),
                    (self.author_client, HTTPStatus.OK),
                ],
            ),
            (
                ('notes:detail', (self.note.slug,)),
                [
                    (self.client, HTTPStatus.FOUND),
                    (self.auth_client, HTTPStatus.NOT_FOUND),
                    (self.author_client, HTTPStatus.OK),
                ],
            ),
            (
                ('users:login', None),
                [
                    (self.client, HTTPStatus.OK),
                ],
            ),
            (
                ('users:logout', None),
                [
                    (self.client, HTTPStatus.OK),
                ],
            ),
            (
                ('users:signup', None),
                [
                    (self.client, HTTPStatus.OK),
                ],
            ),
        ]
        for urls, optional_status_for_users in urls_optional_status_for_users:
            name, args = urls
            for client_status in optional_status_for_users:
                client, status = client_status
                with self.subTest(client=client, name=name):
                    url = reverse(name, args=args)
                    response = client.get(url)
                    self.assertEqual(response.status_code, status)
