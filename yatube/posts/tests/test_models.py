from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post, Comment

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUp(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост длинной более 30 символов'
        )
        cls.comment = Comment.objects.create(
            post=PostModelTest.post,
            author=PostModelTest.user,
            text='обычный комментарий'
        )

    def test_models_have_correct_objects_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        model_and_name = [
            (str(self.group), self.group.title),
            (str(self.post), self.post.text[:30]),
            (str(self.comment), self.comment.text[:30])
        ]

        for test, expected in model_and_name:
            with self.subTest(test=test):
                self.assertEqual(test, expected, '__str__ имя не совпадает')

    def test_models_have_correct_verbose_names(self):
        """Проверяем, что у модели post корректное отражение verbose_name."""
        field_verboses = [
            ('text', 'текст поста', self.post),
            ('pub_date', 'дата публикации', self.post),
            ('author', 'Автор', self.post),
            ('group', 'Группа', self.post),
            ('image', 'Изображение', self.post),
            ('title', 'имя группы', self.group),
            ('description', 'описание', self.group),
            ('post', 'Cтатья с комментариями', self.comment),
            ('author', 'Автор комментария', self.comment),
            ('text', 'Комментарий', self.comment),
            ('created', 'Дата создания', self.comment),
        ]

        for field, expected_value, test_object in field_verboses:
            with self.subTest(field=field):
                self.assertEqual(
                    test_object._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_group_and_post_models_have_correct_help_text(self):
        """Проверяем, что у поля text модели Group
        корректное отражение help_text."""
        help_text = [
            ('title', 'Укажите название группы', self.group),
            ('description', 'О чем Ваша группа?', self.group),
            ('text', 'Добавьте текст поста!', self.post),
            ('text', 'Добавьте текст комментария', self.comment),
        ]
        for name, expected_value, test_object in help_text:
            with self.subTest():
                self.assertEqual(test_object._meta.get_field(name).help_text,
                                 expected_value,
                                 'не совпадает с ожидаемым значением')
