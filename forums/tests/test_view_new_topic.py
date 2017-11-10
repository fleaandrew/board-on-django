from django.core.urlresolvers import reverse
from django.urls import resolve
from django.test import TestCase
from django.contrib.auth.models import User

from .. import views
from .. import models
from .. import forms


class NewTopicTests(TestCase):
    def setUp(self):
        self.board = models.Board.objects.create(name='Django', description='Django board.')
        User.objects.create_user(username='john', email='john@doe.com', password='123')
        self.client.login(username='john', password='123')

    def test_new_topic_view_success_status_code(self):
        url = reverse('forums:new_topic', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_new_topic_view_not_found_status_code(self):
        url = reverse('forums:new_topic', kwargs={'pk':99})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_new_topic_url_resolve_view(self):
        view = resolve('/boards/1/new/')
        self.assertEquals(view.func, views.new_topic)

    def test_new_topic_view_contains_link_to_board_topics_view(self):
        url = reverse('forums:new_topic', kwargs={'pk': 1})
        homepage_url = reverse('forums:board_topics', kwargs={'pk':1})
        response = self.client.get(url)
        self.assertContains(response, 'href="{0}"'.format(homepage_url))

    def test_csrf(self):
        url = reverse('forums:new_topic', kwargs={'pk':1})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_new_topic_valid_post_data(self):
        url = reverse('forums:new_topic', kwargs={'pk':1})
        data = {
            'subject': 'Test title',
            'message': 'Test message'
        }
        response = self.client.post(url, data)
        self.assertTrue(models.Topic.objects.exists)
        self.assertTrue(models.Post.objects.exists)

    def test_new_topic_invalid_post_data(self):
        '''
        Invalid post data should not redirect
        The expected behavior is to show the form again with validation errors
        :return:
        '''
        url = reverse('forums:new_topic', kwargs={'pk':1})
        response = self.client.post(url, {})
        form = response.context.get('form')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)

    def test_new_topic_invalid_post_data_empty_fields(self):
        '''
        Invalid post data should not redirect
        The expected behavior is to show the from again with validation erroes
        :return:
        '''
        url = reverse('forums:new_topic', kwargs={'pk':1})
        data = {
            'subject': '',
            'message': ''
        }
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(models.Topic.objects.exists())
        self.assertFalse(models.Post.objects.exists())

    def test_contains_form(self):
        url = reverse('forums:new_topic', kwargs={'pk': 1})
        response = self.client.get(url)
        form = response.context.get('form')
        self.assertIsInstance(form, forms.NewTopicForm)

class LoginRequiredNewTopicTests(TestCase):
    def setUp(self):
        models.Board.objects.create(name='Django', description='Django board.')
        self.url = reverse('forums:new_topic', kwargs={'pk': 1})
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))