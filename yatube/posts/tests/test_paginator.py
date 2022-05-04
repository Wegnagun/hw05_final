from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group

User = get_user_model()


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.TEST_POST_PAGES = 13
        cls.user = User.objects.create(username='Chupacabra')
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='test-slug',
            description='Тестовое описание группы',
        )
        cls.posts = Post.objects.bulk_create(
            [Post(text=f'Пост номер {test_post}',
                  author=cls.user,
                  group=cls.group) for test_post in range(
                cls.TEST_POST_PAGES)])

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_paginator(self):
        """Проверяем пагинатор - нагибатор"""
        remains_pages = len(self.posts) - settings.MAX_PAGES
        last_page = self.authorized_client.get(
            reverse('posts:index')).context.get('page_obj').paginator.num_pages
        context = [
            (reverse('posts:index'), settings.MAX_PAGES),
            (f"{reverse('posts:index')}?page={last_page}", remains_pages),
            (reverse('posts:group_list',
                     args=[self.group.slug]), settings.MAX_PAGES),
            (f"{reverse('posts:group_list', args = [self.group.slug])}?page="
             f"{last_page}", remains_pages),
            (reverse('posts:profile', args=[self.user]), settings.MAX_PAGES),
            (f"{reverse('posts:profile', args=[self.user])}?page={last_page}",
                remains_pages)
        ]
        cache.clear()  # в сетапе не достаточно очищает, выскакивает ошибка...
        for reverse_page, len_posts in context:
            with self.subTest(reverse=reverse):
                self.assertEqual(
                    len(self.authorized_client.
                        get(reverse_page).context.get('page_obj')), len_posts)
