from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        label = {'text': 'Текст поста',
                 'group': 'Группа',
                 'image': 'Изображение'}
        help_texts = {'text': 'Добавьте текст поста!',
                      'group': 'Группа, к которой будет относиться пост',
                      'image': 'Загруженное изображение'}


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        help_texts = {
            'text': 'Напишите свой комментарий'
        }
