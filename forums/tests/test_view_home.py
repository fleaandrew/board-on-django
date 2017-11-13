from django.core.urlresolvers import reverse
from django.urls import resolve
from django.test import TestCase

from .. import views
from .. import models

class HomeTests(TestCase):
    def setUp(self):
        self.board = models.Board.objects.create(name='Django', description='Django board.')
        url = reverse('home')
        self.response = self.client.get(url)

    def test_home_view_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_home_url_resolve_view(self):
        view = resolve('/')
        self.assertEquals(view.func.view_class, views.BoardListView)

    def test_home_view_contains_link_to_topics_page(self):
        board_topics_url = reverse('forums:board_topics', kwargs={'pk':self.board.pk})
        self.assertContains(self.response, 'href="{0}"'.format(board_topics_url))