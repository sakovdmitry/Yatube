from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from posts.models import Post


User = get_user_model()


class CacheCaseTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.user_2 = User.objects.create(username='dmitry')
        cls.post = Post.objects.create(text='Тестовый пост', author=cls.user_2)
        cls.user_3 = User.objects.create(username='andrew')

    def test_auth_client_follow(self):
        self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user_2.username}))
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertContains(response, 'Тестовый пост')

    def test_auth_client_unfollow(self):
        self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.user_2.username}))
        self.authorized_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.user_2.username}))
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertNotContains(response, 'Тестовый пост')

    def test_new_post(self):
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
