from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group
from posts.forms import PostForm

User = get_user_model()


class PostURLTests(TestCase):
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
