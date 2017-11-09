from django.core.urlresolvers import reverse
from django.urls import resolve
from django.test import TestCase
from django.contrib.auth.models import User

from .. import views
from .. import models
from .. import forms

class HomeTests(TestCase):
    def setUp(self):
        self.board = models.Board.objects.create(name='Django', description='Django board.')
        url = reverse('home')
        self.response = self.client.get(url)

    def test_home_view_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_home_url_resolve_view(self):
        view = resolve('/')
        self.assertEquals(view.func, views.home)

    def test_home_view_contains_link_to_topics_page(self):
        board_topics_url = reverse('forums:board_topics', kwargs={'pk':self.board.pk})
        self.assertContains(self.response, 'href="{0}"'.format(board_topics_url))


class BoardTopicsTests(TestCase):
    def setUp(self):
        board = models.Board.objects.create(name='Django', description='Django board.')

    def test_board_topics_view_success_status_code(self):
        url = reverse('forums:board_topics', kwargs={'pk':1})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_board_topics_view_not_found_status_code(self):
        url = reverse('forums:board_topics', kwargs={'pk':90})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_board_topics_url_resolve_view(self):
        view = resolve('/boards/1/')
        self.assertEquals(view.func, views.board_topics)

    def test_board_topics_view_contains_link_back_to_homepage(self):
        homepage_url = reverse('home')
        url = reverse('forums:board_topics', kwargs={'pk':1})
        response = self.client.get(url)
        self.assertContains(response, 'href="{0}"'.format(homepage_url))

    def test_board_topics_view_contains_navigation_links(self):
        board_topics_url = reverse('forums:board_topics', kwargs={'pk':1})
        new_topic_url = reverse('forums:new_topic', kwargs={'pk': 1})
        response = self.client.get(board_topics_url)
        self.assertContains(response, 'href="{0}"'.format(new_topic_url))


class NewTopicTests(TestCase):
    def setUp(self):
        self.board = models.Board.objects.create(name='Django', description='Django board.')
        User.objects.create_user(username='john', email='john@doe.com', password='123')

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

