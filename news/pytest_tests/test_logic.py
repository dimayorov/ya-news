import pytest
from pytest_django.asserts import assertRedirects, assertFormError
from http import HTTPStatus

from django.urls import reverse

from news.forms import WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client, form_data, news_id_for_args
):
    """Тест на создание комментария к новости анонимным пользователем."""
    url = reverse('news:detail', args=news_id_for_args)
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0

@pytest.mark.django_db
def test_user_can_create_comment(
    author_client, form_data, news_id_for_args, comment
):
    """Тест на создание комментария к новости авторизованным пользователем."""
    url = reverse('news:detail', args=news_id_for_args)
    expected_url = url + '#comments'
    response = author_client.post(url, data=form_data)
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 2
    comment_from_db = Comment.objects.get(id=comment.id)
    comment.refresh_from_db()
    assert comment.text == comment_from_db.text
    assert comment.news == comment_from_db.news
    assert comment.author == comment_from_db.author

def test_user_cant_use_bad_words(
    author_client, news_id_for_args, bad_words_data,
):
        """Тест на невозможность создания комментария с плохими словами."""
        url = reverse('news:detail', args=news_id_for_args)
        response = author_client.post(url, data=bad_words_data)
        form = response.context['form']
        assertFormError(
            form=form,
            field='text',
            errors=WARNING
        )
        comments_count = Comment.objects.count()
        assert comments_count == 0

def test_author_can_delete_comment(
        author_client, form_data, comment_id_for_args
):
    """Тест на возможность удаления комментария автором."""
    url = reverse('news:delete', args=comment_id_for_args)
    url_to_comments = reverse('news:detail', args=comment_id_for_args) + '#comments'
    response = author_client.post(url, data=form_data)
    assertRedirects(response, url_to_comments)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0

def test_author_can_edit_comment(
        author_client, form_data, comment, comment_id_for_args
):
    """Тест на возможность изменения комментария автором."""
    url = reverse('news:edit', args=comment_id_for_args)
    url_to_comments = reverse('news:detail', args=comment_id_for_args) + '#comments'
    response = author_client.post(url, data=form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text

def test_user_cant_delete_comment_of_another_user(
        reader_client, form_data, comment_id_for_args
):
    """Тест на невозможность удаления чужого комментария пользователем."""
    url = reverse('news:delete', args=comment_id_for_args)
    response = reader_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1

def test_user_cant_edit_comment_of_another_user(
        reader_client, form_data, comment_id_for_args, comment
):
    """Тест на возможность изменения чужого комментария пользователем."""
    url = reverse('news:edit', args=comment_id_for_args)
    response = reader_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
