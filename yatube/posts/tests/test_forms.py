from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from posts.models import Post, Group


User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
        )
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='auth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_create_post_guest_client(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый заголовок',
            'group_title': self.group.title
        }
        response_guest_client = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response_guest_client,
                             '/auth/login/?next=/create/')
        self.assertNotEqual(Post.objects.count(), post_count + 1)

    def test_create_post_authorized_client(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый заголовок',
            'group_title': self.group.title
        }
        response_authorized_client = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response_authorized_client, reverse(
            'posts:profile', kwargs={'username': 'auth'}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый заголовок',
            ).exists()
        )

    def test_edit_post(self):
        Post.objects.create(
            text='Текст',
            author=self.user,
            group=self.group
        )
        posts_count_before = Post.objects.count()
        form_data = {
            'text': 'Тестовый отредактированный',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': 1}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': 1}))
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый отредактированный',
            ).exists()
        )
        posts_count_after = Post.objects.count()
        self.assertEqual(posts_count_before, posts_count_after)
        self.assertFalse(Post.objects.filter(text='Текст'))
