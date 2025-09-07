import pytest

from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.test.client import Client

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):  
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def reader(django_user_model):  
    return django_user_model.objects.create(username='Читатель')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    client = Client()
    client.force_login(reader) 
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст',
    )
    return news

@pytest.fixture
def id_for_args(news):
    return (news.id,)

@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment

@pytest.fixture
def comment_id_for_args(comment):
    return (comment.id,)

@pytest.fixture
def create_news():
    today = timezone.now()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    return News.objects.bulk_create(all_news)

@pytest.fixture
def create_comments(news, author):
    today = timezone.now()
    all_comments = [
        Comment(
            news=news,
            author=author,
            text='Текст комментария',
            created=today + timedelta(days=index)
        )
        for index in range(10)
    ]
    return Comment.objects.bulk_create(all_comments)
