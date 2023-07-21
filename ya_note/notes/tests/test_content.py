from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestNotesList(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='тот ещё автор')
        cls.user = User.objects.create(username='залогиненый пользователь')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текс записи',
            slug='slug1',
            author=cls.author,
        )
        cls.form_data = {
            'title': 'Заголовок1',
            'text': 'Текс записи1',
            'slug': 'slug3',
        }

    def test_notes_list_for_different_users(self):
        users_statuses = (
            (self.author, True),
            (self.user, False),
        )
        for type_user, status in users_statuses:
            self.client.force_login(type_user)
            with self.subTest(type_user=type_user):
                url = reverse('notes:list')
                response = self.client.get(url)
                object_list = response.context['object_list']
                self.assertEqual(self.note in object_list, status)

    def test_pages_contains_form(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                self.client.force_login(self.author)
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
