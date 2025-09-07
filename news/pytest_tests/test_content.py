import pytest

from django.urls import reverse
from django.conf import settings

from news.forms import CommentForm


@pytest.mark.django_db
def test_news_count(client, create_news):
    """Тестирование количества новостей на главной странице."""
    home_url = reverse('news:home')
    response = client.get(home_url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE

@pytest.mark.django_db
def test_news_order(client, create_news):
        """Тестирование очередности новостей на главной странице."""
        home_url = reverse('news:home')
        response = client.get(home_url)
        object_list = response.context['object_list']
        all_dates = [news.date for news in object_list]
        sorted_dates = sorted(all_dates, reverse=True)
        assert all_dates == sorted_dates

@pytest.mark.django_db
def test_comments_order(client, create_comments, id_for_args):
        """Тестирование очередности комментариев под новостью."""
        detail_url = reverse('news:detail', args=id_for_args)
        response = client.get(detail_url)
        assert 'news' in response.context
        # Получаем объект новости.
        news = response.context['news']
        # Получаем все комментарии к новости.
        all_comments = news.comment_set.all()
        # Собираем временные метки всех комментариев.
        all_timestamps = [comment.created for comment in all_comments]
        # Сортируем временные метки, менять порядок сортировки не надо.
        sorted_timestamps = sorted(all_timestamps)
        # Проверяем, что временные метки отсортированы правильно.
        assert all_timestamps == sorted_timestamps

@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('id_for_args')),
    )
)
def test_pages_contains_form(author_client, name, args):
    """Тестирование формы на страницах создания и редактирования заметки."""
    # Формируем URL.
    url = reverse(name, args=args)
    # Запрашиваем нужную страницу:
    response = author_client.get(url)
    # Проверяем, есть ли объект формы в словаре контекста:
    assert 'form' in response.context
    # Проверяем, что объект формы относится к нужному классу.
    assert isinstance(response.context['form'], CommentForm) 
