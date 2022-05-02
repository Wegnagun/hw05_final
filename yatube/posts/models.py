from django.contrib.auth import get_user_model
from django.db import models
from core.models import CreatedModel

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


class Post(models.Model):
    text = models.TextField(verbose_name='текст поста',
                            help_text='Добавьте текст поста!')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='дата публикации')
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
        ordering = ('-pub_date',)
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

    def __str__(self):
        return self.text[:30]
