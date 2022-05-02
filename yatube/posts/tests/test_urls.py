from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group

User = get_user_model()


class StaticUrlTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Testometr')
        cls.second_user = User.objects.create_user(username='Proveryator')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост длинной более 30 символов'
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_use_right_reverse(self):
        """ проверит соответствие /posts/.../ и reverse('posts:...')"""
        address_and_reverse = [
            (f'/group/{self.group.slug}/',
                reverse('posts:group_list', args=[self.group.slug])),
            (f'/profile/{self.user.username}/',
                reverse('posts:profile', args=[self.user.username])),
            (f'/posts/{self.post.id}/',
                reverse('posts:post_detail', args=[self.post.id])),
            ('/create/',
                reverse('posts:post_create')),
            (f'/posts/{self.post.id}/edit/',
                reverse('posts:post_edit', args=[self.post.id])),
            (f'/posts/{self.post.id}/comment/',
             reverse('posts:add_comment', args=[self.post.id])),
        ]

        for address, reverse_name in address_and_reverse:
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(address, reverse_name)

    def test_url_unauthorised_user_location(self):
        """Проверяем доступность неавторизованному пользователю страниц"""
        unauthoraized_pages_list = [
            '/',
            reverse('posts:group_list', args=[self.group.slug]),
            reverse('posts:profile', args=[self.user.username]),
            reverse('posts:post_detail', args=[self.post.id])]

        for page in unauthoraized_pages_list:
            with self.subTest(page=page):
                response = self.guest_client.get(f'{page}')
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_authorised_user_location(self):
        """Проверяем доступность авторизованному пользователю страниц"""
        authoraized_pages_list = [
            '/',
            reverse('posts:group_list', args=[self.group.slug]),
            reverse('posts:profile', args=[self.user.username]),
            reverse('posts:post_detail', args=[self.post.id]),
            reverse('posts:post_create'),
            reverse('posts:post_edit', args=[self.post.id]),
        ]

        for page in authoraized_pages_list:
            with self.subTest(page=page):
                response = self.authorized_client.get(f'{page}')
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_try_enter_unexisting_page(self):
        """Пробуем зайти на несуществующую страницу"""
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_right_redirect(self):
        """Проверяем переадресацию"""
        guest_pages_list = [
            reverse('posts:post_edit', args=[self.post.id]),
            reverse('posts:add_comment', args=[self.post.id])
        ]
        for page in guest_pages_list:
            with self.subTest(page=page):
                response = self.guest_client.get(page, follow=True)
                self.assertRedirects(
                    response, f'/auth/login/?next={page}')

        response = self.guest_client.get(reverse('posts:add_comment',
                                                 args=[self.post.id]),
                                         follow=True)
        self.assertRedirects(
            response, f'/auth/login/?next='
                      f'{reverse("posts:add_comment", args=[self.post.id])}')

    def test_urls_uses_correct_template(self):
        """Проверяем, что URL-адрес использует соответствующий шаблон."""
        templates_url_names = [
            ('/', 'posts/index.html'),
            (reverse('posts:group_list', args=[self.group.slug]),
                'posts/group_list.html'),
            (reverse('posts:profile', args=[self.user.username]),
                'posts/profile.html'),
            (reverse('posts:post_detail', args=[self.post.id]),
                'posts/post_detail.html'),
            (reverse('posts:post_create'), 'posts/create_post.html'),
            (reverse('posts:post_edit', args=[self.post.id]),
                'posts/create_post.html'),
        ]

        for address, template in templates_url_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_post_edit_by_not_author(self):
        """Проверяем не автора на изменение поста"""
        self.authorized_client.force_login(self.second_user)
        response = self.authorized_client.get(
            reverse('posts:post_edit', args=[self.post.id]), follow=True)
        self.assertRedirects(response,
                             reverse('posts:post_detail', args=[self.post.id]))
