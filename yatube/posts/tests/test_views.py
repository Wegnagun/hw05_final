import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Post, Group, Follow

User = get_user_model()
TEMP = tempfile.mktemp(dir=settings.TEMP_MEDIA_ROOT)


@override_settings(MEDIA_ROOT=TEMP)
class PostsPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Testometr')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.second_group = Group.objects.create(
            title='Недогруппа',
            slug='slugishe',
            description='группа для проверки туда ли все попало...'
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='тестовый текст поста',
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.follower = User.objects.create(
            username='follower'
        )
        self.not_follower = User.objects.create(
            username='followerknot'
        )
        cache.clear()

    def test_pages_show_correct_context(self):
        """Проверяем передаваемый контекст"""
        context = [(reverse('posts:index'), self.post),
                   (reverse('posts:group_list', args=[self.group.slug]),
                       self.post),
                   (reverse('posts:profile',
                            args=[self.user]), self.post),
                   ]
        for reverse_page, context_object in context:
            with self.subTest(reverse_page=reverse_page):
                response = self.authorized_client.get(reverse_page)
                self.assertIn(context_object, response.context['posts'])

        response = self.authorized_client.get(
            reverse('posts:post_detail', args=[self.post.id]))
        self.assertEqual(response.context['posts'].text, self.post.text)

    def test_group_for_vagrant_post(self):
        """Проверка, что второй пост не в первой группе"""
        response = self.authorized_client.get(
            reverse('posts:group_list', args=[self.second_group.slug]))
        page_object = response.context['posts']
        self.assertNotIn(self.post, page_object)

    def test_cashing(self):
        """Проверка кэширования"""
        content = self.authorized_client.get(reverse('posts:index')).content
        Post.objects.create(
            text='пост для кеши',
            author=self.user,
        )
        content_after_post = self.authorized_client.get(
            reverse('posts:index')).content
        self.assertEqual(content, content_after_post)
        cache.clear()
        content_after_clear = self.authorized_client.get(
            reverse('posts:index')).content
        self.assertNotEqual(content_after_post, content_after_clear)

    def test_follow_can_see_posts(self):
        """подписчик может видет посты автора а неподписчи - нет"""
        Follow.objects.create(
            user=self.follower,
            author=self.user
        )
        self.authorized_client.force_login(self.follower)
        response_follow = self.authorized_client.get(
            reverse('posts:follow_index'))
        objects_count_follow = len(
            response_follow.context['page_obj'].object_list)
        self.assertEqual(objects_count_follow, 1)
        cache.clear()
        self.authorized_client.force_login(self.user)
        user_response_follow = self.authorized_client.get(
            reverse('posts:follow_index'))
        objects_count_follow = len(
            user_response_follow.context['page_obj'].object_list)
        self.assertEqual(objects_count_follow, 0)

    def test_can_follow(self):
        """Авторизованный пользователь может подписываться на других"""
        follow_count = Follow.objects.filter(
            user=self.follower,
            author=self.user).count()
        self.assertEqual(0, follow_count)
        self.authorized_client.force_login(self.follower)
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            args=[self.user.username])
        )
        follow_count = Follow.objects.filter(
            user=self.follower,
            author=self.user).count()
        self.assertEqual(1, follow_count)
        self.authorized_client.get(reverse(
            'posts:profile_unfollow',
            args=[self.user.username])
        )
        follow_count = Follow.objects.filter(
            user=self.follower,
            author=self.user).count()
        self.assertEqual(0, follow_count)
