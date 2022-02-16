from django.core.cache import cache
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from posts.models import Post

User = get_user_model()


class CacheCaseTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_cache_index(self):
        self.post = Post.objects.create(text='Тестовый пост', author=self.user)
        self.authorized_client.get('/')
        self.post.delete()
        response = self.authorized_client.get('/')
        self.assertContains(response, 'Тестовый пост')
        cache.clear()
        response = self.authorized_client.get('/')
        self.assertNotContains(response, 'Тестовый пост')
