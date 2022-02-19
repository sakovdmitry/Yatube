from django.db import models

from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200,
                             verbose_name='Название группы',
                             help_text='Максимальная длина 200 символов')
    slug = models.SlugField(unique=True,
                            max_length=100,
                            verbose_name='URL группы',
                            help_text='Максимальная длина 100 символов')
    description = models.TextField(verbose_name='Описание группы')

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name='Текст поста')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации поста')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='автор поста',
        help_text='Выберите автора поста'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='group_posts',
        verbose_name='группа',
        help_text='Выберите группу поста'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
        help_text='Поддерживаются только форматы картинки'
    )

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ['-pub_date']


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='пост',
        help_text='Выберите пост'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='автор комментария',
        help_text='Выберите автора комментария'
    )
    text = models.TextField(verbose_name='текст комментария')
    created = models.DateTimeField(auto_now_add=True,
                                   verbose_name='дата создания')

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['-created']


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь-подписчик',
        help_text='Выберите пользователя-подписчика'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор, на которого подписан',
        help_text='Выберите автора для подписки'
    )

    class Meta:
        unique_together = ('user', 'author')
