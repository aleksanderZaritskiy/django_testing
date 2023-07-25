# test_logic.py
from http import HTTPStatus

import pytest
from django.urls import reverse
from news.forms import BAD_WORDS, WARNING
from news.models import Comment, News
from pytest_django.asserts import assertFormError, assertRedirects

COMMENTS_OBJ_IN_DATABASE = 1


def test_user_can_create_comment(
    admin_user, admin_client, form_data, create_news
):
    url = reverse('news:detail', args=(create_news.id,))
    # Если до отправки формы были какие-то комментарии в бд их удалим.
    Comment.objects.all().delete()
    # обновим актуальность данных в бд
    response = admin_client.post(url, data=form_data)
    # получаем кол-во комментариев
    comment_after = Comment.objects.count()
    # проверяю создалась ли запись
    assert comment_after == COMMENTS_OBJ_IN_DATABASE
    assertRedirects(response, f'{url}#comments')
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == admin_user


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, create_news):
    url = reverse('news:detail', args=(create_news.id,))
    # Получаем количество комментариев до отправки формы.
    comments_before = Comment.objects.count()
    response = client.post(url, data=form_data)
    # Получаем количество комментариев после отправки формы.
    comments_after = Comment.objects.count()
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    # Убеждаемся, что после отправки формы
    # Количество комментариев в б/д не изменилось.
    assert comments_before == comments_after


def test_user_cant_use_bad_words(admin_client, create_news):
    url = reverse('news:detail', args=(create_news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    comments_before = Comment.objects.count()
    response = admin_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING,
    )
    comments_after = Comment.objects.count()
    # По аналогии с тестом test_anonymous_user_cant_create_comment -
    # количество комментариев не должно измениться.
    assert comments_before == comments_after


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
    news = News.objects.get(id=create_news.id)
    # Получаем комментарий из б/д уже с изменениями.
    comment_connect_news = news.comment_set.get(id=create_comment.id)
    # Убеждаемся, что текст комментария изменился.
    assert create_comment.text != comment_connect_news.text
    assert comment_connect_news.text == form_data['text']
    assert comment_connect_news.author == author
    # Проверяем что автор комментария не изменялся в процессе редактирования.
    assert create_comment.author == comment_connect_news.author


def test_other_user_cant_edit_comment(admin_client, form_data, create_comment):
    url_edit = reverse('news:edit', args=(create_comment.id,))
    response = admin_client.post(url_edit, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_form_db = Comment.objects.get(id=create_comment.id)
    assert create_comment.text == comment_form_db.text
    assert create_comment.author == comment_form_db.author
    # Через fk убеждаемся, что после отправки формы.
    # комментарий принадлежит той же новости.
    assert create_comment.news.id == comment_form_db.news.id


def test_author_can_delete_comment(author_client, create_news, create_comment):
    url = reverse('news:detail', args=(create_news.id,))
    # Получаем объект комментария, котроый будем удалять
    comment_before = Comment.objects.filter(id=create_comment.id)
    url_delete = reverse('news:delete', args=(create_comment.id,))
    response = author_client.post(url_delete)
    assertRedirects(response, f'{url}#comments')
    # Проверяем пустой ли QuerySet т.к. данные комментария удалены.
    assert not comment_before


def test_other_user_cant_delete_note(admin_client, form_data, create_comment):
    url = reverse('news:delete', args=(create_comment.id,))
    comment_before = Comment.objects.filter(id=create_comment.id)
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    # Делаем по аналогии с test_other_user_cant_delete_note,
    # но в этот раз QuerySet не должен быть пустым.
    assert comment_before
