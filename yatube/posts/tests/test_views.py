import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache

from django import forms

from posts.models import Post, Group
from posts.forms import PostForm

User = get_user_model()


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='auth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            group=cls.group,
            author=cls.user,
            text='Тестовая группа тестовая группа',
        )

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            (reverse('posts:group_posts', kwargs={'slug': self.group.slug})):
            'posts/group_list.html',
            (reverse('posts:profile',
                     kwargs={'username': self.user.username})):
            'posts/profile.html',
            (reverse('posts:post_detail', kwargs={'post_id': self.post.pk})):
            'posts/post_detail.html',
            (reverse('posts:post_edit', kwargs={'post_id': self.post.pk})):
            'posts/post_create.html',
            reverse('posts:post_create'): 'posts/post_create.html'
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """Шаблоны сформированы с правильным контекстом."""
        response_index = self.authorized_client.get(reverse('posts:index'))
        context_index = response_index.context['page_obj'][0]
        contexts = {
            context_index.group.title: self.group.title,
            context_index.author.username: self.user.username,
            context_index.text: self.post.text
        }
        for template_context, instanse_context in contexts.items():
            with self.subTest(template_context=template_context):
                self.assertEqual(template_context, instanse_context)

    def test_group_list_show_correct_context(self):
        response_group_list = self.authorized_client.get(reverse(
            'posts:group_posts', kwargs={'slug': self.group.slug}))
        context_group_list = response_group_list.context['page_obj'][0]
        contexts = {
            context_group_list.group.title: self.group.title,
            context_group_list.author.username: self.user.username,
            context_group_list.text: self.post.text
        }
        for template_context, instanse_context in contexts.items():
            with self.subTest(template_context=template_context):
                self.assertEqual(template_context, instanse_context)

    def test_profile_show_correct_context(self):
        response_profile = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.user.username}))
        context_profile = response_profile.context['page_obj'][0]
        contexts = {
            context_profile.group.title: self.group.title,
            context_profile.author.username: self.user.username,
            context_profile.text: self.post.text
        }
        for template_context, instanse_context in contexts.items():
            with self.subTest(template_context=template_context):
                self.assertEqual(template_context, instanse_context)

    def test_index_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}))
        self.assertEqual(response.context.get(
            'post').author.username, self.user.username)
        self.assertEqual(response.context.get(
            'post').text, self.post.text)
        self.assertEqual(response.context.get('post').pk, self.post.pk)

    def test_create_edit_show_correct_context(self):
        """Шаблоны create и post edit сформированы с правильным контекстом."""
        response_create = self.authorized_client.get(
            reverse('posts:post_create'))
        response_edit = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field_create = response_create.context.get(
                    'form').fields.get(value)
                self.assertIsInstance(form_field_create, expected)
                form_field_edit = response_edit.context.get(
                    'form').fields.get(value)
                self.assertIsInstance(form_field_edit, expected)

        context = response_edit.context.get('is_edit')
        self.assertIsInstance(context, bool)
        context = response_edit.context.get('form')
        self.assertIsInstance(context, PostForm)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug-slug',)
        objs = [
            Post(
                author=cls.user, text=i, group=cls.group
            )
            for i in range(13)]
        Post.objects.bulk_create(objs)

    def test_first_page_contains_ten_records(self):
        """Проверка paginator, 10 постов на первой странице."""
        templates = {
            reverse('posts:index'): 'page_obj',
            reverse('posts:group_posts',
                    kwargs={'slug': self.group.slug}): 'page_obj',
            reverse('posts:profile',
                    kwargs={'username': self.user.username}): 'page_obj',
        }
        for reverse_name, obj in templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(len(response.context[obj]), 10)

    def test_second_page_contains_three_records(self):
        """Проверка paginator, 3 поста на второй странице."""
        templates = {
            reverse('posts:index') + '?page=2': 'page_obj',
            reverse('posts:group_posts',
                    kwargs={'slug': self.group.slug}) + '?page=2': 'page_obj',
            reverse('posts:profile',
                    kwargs={'username': self.user.username}) + '?page=2':
                                                               'page_obj'
        }
        for reverse_name, obj in templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(len(response.context[obj]), 3)


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ImageTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='test',
            author=cls.user,
            group=cls.group
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'group_title': self.group.title,
            'text': 'Тестовый текст',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'auth'}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст',
                image='posts/small.gif'
            ).exists()
        )

    def test_img_index(self):
        """Картинки отображаются на главной странице"""
        response_index = self.authorized_client.get(reverse('posts:index'))
        context_index = response_index.context['page_obj'][0]
        self.assertEqual(context_index.image, self.post.image)

    def test_img_profile(self):
        """Картинки отображаются на странице профиля"""
        response_profile = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.user.username}))
        context_profile = response_profile.context['page_obj'][0]
        self.assertEqual(context_profile.image, self.post.image)

    def test_img_group(self):
        """Картинки отображаются на странице группы"""
        response_group_list = self.authorized_client.get(reverse(
            'posts:group_posts', kwargs={'slug': self.group.slug}))
        context_group_list = response_group_list.context['page_obj'][0]
        self.assertEqual(context_group_list.image, self.post.image)

    def test_img_post(self):
        """Картинки отображаются на странице с постом"""
        response_post = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}))
        self.assertEqual(response_post.context.get(
            'post').image, self.post.image)


class FollowingCaseTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='auth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.user_2 = User.objects.create(username='dmitry')
        cls.post = Post.objects.create(text='Тестовый пост', author=cls.user_2)
        cls.user_3 = User.objects.create(username='andrew')

    def test_auth_client_follow(self):
        """авторизованный пользователь может подписаться на автора"""
        self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user_2.username}))
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertContains(response, 'Тестовый пост')

    def test_auth_client_unfollow(self):
        """авторизованный пользователь может отписаться от автора"""
        self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user_2.username}))
        self.authorized_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.user_2.username}))
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertNotContains(response, 'Тестовый пост')

    def test_new_post(self):
        """Новый пост появляется только у подписчиков"""
        self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user_2.username}))
        Post.objects.create(text='Тестовый пост 2', author=self.user_2)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertContains(response, 'Тестовый пост 2')
        self.authorized_client.logout()
        self.authorized_client.force_login(self.user_3)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertNotContains(response, 'Тестовый пост 2')

    def test_guest_client_follow(self):
        """Неавторизованный пользователь не может подписаться"""
        response = self.guest_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user_2.username}))
        self.assertEqual(response.status_code, 302)


class CacheCaseTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_cache_index(self):
        """Пост остается в кэше до очистки кэша"""
        cache.clear()
        self.post = Post.objects.create(text='Тестовый пост', author=self.user)
        self.authorized_client.get(reverse('posts:index'))
        self.post.delete()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertContains(response, 'Тестовый пост')
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertNotContains(response, 'Тестовый пост')


class CommentCaseTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='auth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.post = Post.objects.create(text='Тестовый пост', author=cls.user)

    def test_comment_authorized(self):
        """Авторизованный пользователь может комментировать записи"""
        self.authorized_client.post(reverse('posts:add_comment',
                                    kwargs={'post_id': self.post.pk}),
                                    {'text': 'Тестовый комментарий'})
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.pk}))
        self.assertContains(response, 'Тестовый комментарий')

    def test_comment_guest_client(self):
        """Неавторизованный пользователь не может комментировать записи"""
        self.guest_client.post(reverse('posts:add_comment',
                                       kwargs={'post_id': self.post.pk}),
                               {'text': 'Тестовый комментарий'})
        response = self.guest_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}))
        self.assertNotContains(response, 'Тестовый комментарий')
