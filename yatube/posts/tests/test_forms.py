import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Post, Group, Comment

User = get_user_model()
TEMP = tempfile.mktemp(dir=settings.TEMP_MEDIA_ROOT)


@override_settings(MEDIA_ROOT=TEMP)
class TestCreatePost(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Balthazar')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='тестовый текст поста',
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(settings.TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Проверка создается ли пост и коммент к нему"""
        post_count = Post.objects.count()
        comment_count = Comment.objects.count()
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

        form_data = {
            'author': self.user,
            'text': 'Тестовый текст нового поста',
            'group': self.group.id,
            'image': uploaded,
        }
        comment_data = {
            'text': 'текстулька коммента'
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            author=self.user,
            follow=True
        )
        comment_response = self.authorized_client.post(
            reverse('posts:add_comment', args=[self.post.id]),
            data=comment_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile',
                                               args=[self.user]))
        self.assertRedirects(comment_response, reverse('posts:post_detail',
                                                       args=[self.post.id]))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(Post.objects.filter(
            text=form_data['text'],
            image='posts/small.gif',
            author=self.user,
            group=self.group,
        ).exists())
        self.assertTrue(Comment.objects.filter(
            text=comment_data['text'],
            author=self.user,
        ).exists())

    def test_post_edit(self):
        """Проверка на изменение поста"""
        form_data = {
            'text': 'совершенно новый текст',
            'group': self.group.id,
        }

        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id}))
        self.assertTrue(Post.objects.filter(
            text=form_data['text'],
            author=self.user,
            id=self.post.id
        ).exists())
