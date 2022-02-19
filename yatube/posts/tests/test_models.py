from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post, Comment, Follow

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_2 = User.objects.create_user(username='dmitry')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа тестовая группа',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='asd'
        )
        cls.follow = Follow.objects.create(
            author=cls.user,
            user=cls.user_2
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        self.assertEqual(str(self.group), self.group.title)
        self.assertEqual(str(self.post), self.post.text[:15])

    def test_post_model_verbose_help_fields(self):
        """verbose_name и help_fields модели post совпадают с ожидаемыми."""
        post = PostModelTest.post
        verbose_names_expected = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации поста',
            'author': 'автор поста',
            'group': 'группа',
        }
        for field_name, text in verbose_names_expected.items():
            with self.subTest(field_name=field_name):
                verbose = post._meta.get_field(field_name).verbose_name
                self.assertEqual(verbose, text)
        help_text_expected = {
            'author': 'Выберите автора поста',
            'group': 'Выберите группу поста',
            'image': 'Поддерживаются только форматы картинки',
        }
        for field_name, text in help_text_expected.items():
            with self.subTest(field_name=field_name):
                verbose = post._meta.get_field(field_name).help_text
                self.assertEqual(verbose, text)

    def test_group_model_verbose_help_fields(self):
        """verbose_name и help_fields модели group совпадают с ожидаемыми."""
        group = PostModelTest.group
        verbose_names_expected = {
            'title': 'Название группы',
            'slug': 'URL группы',
            'description': 'Описание группы',
        }
        for field_name, text in verbose_names_expected.items():
            with self.subTest(field_name=field_name):
                verbose = group._meta.get_field(field_name).verbose_name
                self.assertEqual(verbose, text)
        help_text_expected = {
            'title': 'Максимальная длина 200 символов',
            'slug': 'Максимальная длина 100 символов',
        }
        for field_name, text in help_text_expected.items():
            with self.subTest(field_name=field_name):
                verbose = group._meta.get_field(field_name).help_text
                self.assertEqual(verbose, text)

    def test_comment_model_verbose_help_fields(self):
        """verbose_name и help_fields модели comment совпадают с ожидаемыми."""
        comment = PostModelTest.comment
        verbose_names_expected = {
            'post': 'пост',
            'author': 'автор комментария',
            'text': 'текст комментария',
            'created': 'дата создания',
        }
        for field_name, text in verbose_names_expected.items():
            with self.subTest(field_name=field_name):
                verbose = comment._meta.get_field(field_name).verbose_name
                self.assertEqual(verbose, text)
        help_text_expected = {
            'post': 'Выберите пост',
            'author': 'Выберите автора комментария',
        }
        for field_name, text in help_text_expected.items():
            with self.subTest(field_name=field_name):
                verbose = comment._meta.get_field(field_name).help_text
                self.assertEqual(verbose, text)

    def test_follow_model_verbose_help_fields(self):
        """verbose_name и help_fields модели follow совпадают с ожидаемыми."""
        follow = PostModelTest.follow
        verbose_names_expected = {
            'user': 'Пользователь-подписчик',
            'author': 'Автор, на которого подписан',
        }
        for field_name, text in verbose_names_expected.items():
            with self.subTest(field_name=field_name):
                verbose = follow._meta.get_field(field_name).verbose_name
                self.assertEqual(verbose, text)
        help_text_expected = {
            'user': 'Выберите пользователя-подписчика',
            'author': 'Выберите автора для подписки',
        }
        for field_name, text in help_text_expected.items():
            with self.subTest(field_name=field_name):
                verbose = follow._meta.get_field(field_name).help_text
                self.assertEqual(verbose, text)
