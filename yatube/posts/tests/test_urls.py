from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group

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
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа тестовая группа',
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/slug-slug/',
            'posts/profile.html': '/profile/auth/',
            'posts/post_detail.html': '/posts/1/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

        templates_url_names = {
            '/posts/1/edit/': 'posts/post_create.html',
            '/create/': 'posts/post_create.html'
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_unexisting_page_response(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_pages_response_guest(self):
        template_address = {
            '/': 200,
            '/group/slug-slug/': 200,
            '/profile/auth/': 200,
            '/posts/1/': 200,
            '/create/': 302,
            '/posts/1/edit/': 302
        }
        for address, code in template_address.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, code)

    def test_pages_response_authorized_user(self):
        template_address = {
            '/': 200,
            '/create/': 200,
            '/group/slug-slug/': 200,
            '/profile/auth/': 200,
            '/posts/1/': 200,
            '/posts/1/edit/': 200
        }
        for address, code in template_address.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, code)

    def test_edit_not_author(self):
        user_2 = User.objects.create_user(username='auth2')
        post = Post.objects.create(text='123', author=user_2)
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': post.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('posts:post_detail',
                                               kwargs={'post_id': post.pk}))

    def test_edit_guest_client(self):
        response = self.guest_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}))
        self.assertRedirects(response, '/auth/login/?next=/posts/1/edit/')
