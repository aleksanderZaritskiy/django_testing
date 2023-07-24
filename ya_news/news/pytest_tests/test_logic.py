# test_logic.py
from http import HTTPStatus

import pytest
from django.urls import reverse
from news.forms import BAD_WORDS, WARNING
from news.models import Comment, News
from pytest_django.asserts import assertFormError, assertRedirects


def test_user_can_create_comment(
    admin_user, admin_client, form_data, create_news
):
    url = reverse('news:detail', args=(create_news.id,))
    comments_before = Comment.objects.count()
    response = admin_client.post(url, data=form_data)
    comments_after = Comment.objects.count()
    assertRedirects(response, f'{url}#comments')
    # Убеждаемся, что после отправки создание комментария
    # в б/д добавился новый
    assert comments_after - comments_before == 1
    # Получаем крайний комментрий из б/д
    new_comment = Comment.objects.last()
    comment_connect_news = create_news.comment_set.last()
    assert new_comment.text == form_data['text']
    assert new_comment.author == admin_user
    assert new_comment.author == comment_connect_news.author


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, create_news):
    url = reverse('news:detail', args=(create_news.id,))
    assert Comment.objects.count() == 0
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_cant_use_bad_words(admin_client, create_news):
    url = reverse('news:detail', args=(create_news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = admin_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING,
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_edit_comment(
    author_client,
    create_comment,
    create_news,
    form_data,
    author,
):
    url = reverse('news:detail', args=(create_news.id,))
    url_edit = reverse('news:edit', args=(create_comment.id,))
    response = author_client.post(url_edit, form_data)
    assertRedirects(response, f'{url}#comments')
    create_comment.refresh_from_db()
    news = News.objects.get()
    comment_connect_news = news.comment_set.get()
    assert create_comment.text == form_data['text']
    assert create_comment.author == author
    assert create_comment.author == comment_connect_news.author


def test_other_user_cant_edit_comment(admin_client, form_data, create_comment):
    url_edit = reverse('news:edit', args=(create_comment.id,))
    response = admin_client.post(url_edit, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_form_db = Comment.objects.get(id=create_comment.id)
    assert create_comment.text == comment_form_db.text


def test_author_can_delete_comment(author_client, create_news, create_comment):
    url = reverse('news:detail', args=(create_news.id,))
    url_delete = reverse('news:delete', args=(create_comment.id,))
    response = author_client.post(url_delete)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_note(admin_client, form_data, create_comment):
    url = reverse('news:delete', args=(create_comment.id,))
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
