from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects

from django.urls import reverse

# 3. Страницы удаления и редактирования комментария доступны автору комментария.
# 4. При попытке перейти на страницу редактирования или удаления комментария анонимный пользователь перенаправляется на страницу авторизации.
# 5. Авторизованный пользователь не может зайти на страницу редактирования или удаления чужих комментариев (возвращается ошибка 404).
# 6. Страницы регистрации пользователей, входа в учётную запись и выхода из неё доступны анонимным пользователям.

@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None), 
        ('news:detail', pytest.lazy_fixture('id_for_args')), 
        ('users:login', None), 
        ('users:signup', None),
    )
)
def test_pages_availability_for_anonymous_user(client, name, args):
    """Тест доступа анонимного пользователя к страницам.

    Доступ проверяется к страницам:
    1. Главная страница.
    2. Страница отдельной новости.
    3. Страница логирования.
    4. Страница регистрации.
    """
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK

@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('id_for_args')), 
        ('users:login', None), 
        ('users:signup', None),
    )
)
def test_pages_availability_for_auth_user(reader_client, name, args):
    """Тест доступа авторизованного пользователя к страницам.

    Доступ проверяется к страницам:
    1. Страница отдельной новости.
    2. Страница логирования.
    3. Страница регистрации.
    """
    url = reverse(name, args=args)
    response = reader_client.get(url)
    assert response.status_code == HTTPStatus.OK

@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_comment_pages_availability_for_different_users(
        parametrized_client, name, comment_id_for_args, expected_status
):
    """Тест доступности автора к удалению и редактированию комментария."""
    url = reverse(name, args=comment_id_for_args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status

@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('id_for_args')),
        ('news:delete', pytest.lazy_fixture('id_for_args')),
    ),
)
def test_redirects(client, name, args):
    """Тест переадресации анонимного пользователя.

    При попытке перейти на страницу редактирования или удаления комментария 
    анонимный пользователь перенаправляется на страницу авторизации.
    """
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
