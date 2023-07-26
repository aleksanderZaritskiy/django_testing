from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNotes(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='залогиненый пользователь')
        cls.author = User.objects.create(username='тот ещё автор')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текс записи',
            slug='slugo',
            author=cls.author,
        )
        cls.form_data = {
            'title': 'Заголовок1',
            'text': 'Текс записи1',
            'slug': 'slug3',
        }

    def test_user_can_create_note(self):
        url = reverse('notes:add')
        url_redirect = reverse('notes:success')
        response = self.auth_client.post(url, data=self.form_data)
        self.assertRedirects(response, url_redirect)
        get_note = Note.objects.get(slug=self.form_data['slug'])
        self.assertEqual(get_note.title, self.form_data['title'])
        self.assertEqual(get_note.text, self.form_data['text'])
        self.assertEqual(get_note.author, self.user)

    def test_anonymous_user_cant_create_note(self):
        url = reverse('notes:add')
        self.client.post(url, data=self.form_data)
        # Поиск созданной записи анонимом по slug, должен быть пустой список.
        get_note = Note.objects.filter(slug=self.form_data['slug']).exists()
        # Такой ассерт сработает только,
        # если в списке note будет содержимое(т.е. б/д вернёт объект)
        self.assertFalse(get_note)

    def test_not_unique_slug(self):
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текс записи',
            slug='slug1',
            author=self.author,
        )
        url = reverse('notes:add')
        self.form_data['slug'] = self.note.slug
        response = self.auth_client.post(url, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=(self.note.slug + WARNING),
        )

    def test_empty_slug(self):
        url = reverse('notes:add')
        self.form_data.pop('slug')
        self.auth_client.post(url, data=self.form_data)
        expected_slug = slugify(self.form_data['title'])
        # Получаем из б/д созданую запись и заодно убеждаемся,
        # что slug добавлен в соотвествии с функцией транслитерации
        get_note = Note.objects.filter(slug=expected_slug).exists()
        # Вернет True если запись существует в б/д
        self.assertTrue(get_note)

    def test_author_can_edit_note(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        self.client.force_login(self.author)
        response = self.client.post(url, self.form_data)
        new_note = Note.objects.get(slug=self.form_data['slug'])
        self.assertRedirects(response, reverse('notes:success'))
        # Убеждаемся что поля измененной заметки в бд соотвествуют форме.
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        # Убеждаемся что автор не изменился.
        self.assertEqual(self.note.author, new_note.author)
        # Убеждаемся, что старая заметка не идентична новой.
        self.assertIsNot(self.note, new_note)

    def test_other_user_cant_edit_note(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.auth_client.post(url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)
        self.assertEqual(self.note.author, note_from_db.author)

    def test_author_can_delete_note(self):
        url = reverse('notes:delete', args=(self.note.slug,))
        self.client.force_login(self.author)
        response = self.client.post(url)
        # Распаковал Queryset через List comp.,
        # если заметка успешно удалена список будет пустой.
        note = Note.objects.filter(slug=self.note.slug).exists()
        self.assertRedirects(response, reverse('notes:success'))
        # Такой ассерт сработает только,
        # если в списоке note будет содержимое(т.е. б/д вернёт объект)
        self.assertFalse(note)

    def test_other_user_cant_delete_note(self):
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.auth_client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        # Проверяем, что заметка по прежнему существует
        self.assertTrue(Note.objects.filter(slug=self.note.slug).exists())
