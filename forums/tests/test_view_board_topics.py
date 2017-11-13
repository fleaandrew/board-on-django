from django.core.urlresolvers import reverse
from django.urls import resolve
from django.test import TestCase

from .. import views
from .. import models


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
        self.assertEquals(view.func.view_class, views.TopicListView)

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
