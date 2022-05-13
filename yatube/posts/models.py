from core.models import CreatedModel
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200,
                             verbose_name='имя группы',
                             help_text='Укажите название группы')
    slug = models.SlugField(unique=True, max_length=10)
    description = models.TextField(verbose_name='описание',
                                   help_text='О чем Ваша группа?')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Группы'
        verbose_name_plural = 'Группы'


class Post(CreatedModel):
    text = models.TextField(verbose_name='текст поста',
                            help_text='Добавьте текст поста!')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа'
    )
    image = models.ImageField(
        'Изображение',
        upload_to='posts/',
        blank=True,
        help_text='Добавьте изображение'
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Посты'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:30]


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Cтатья с комментариями',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
    )
    text = models.TextField(
        verbose_name='Комментарий',
        help_text='Добавьте текст комментария'
    )

    class Meta:
        ordering = ('post',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:30]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь'
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        models.UniqueConstraint(fields=('user', 'author'),
                                name='unique_follow')

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
