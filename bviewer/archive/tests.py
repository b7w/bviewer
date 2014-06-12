# -*- coding: utf-8 -*-
from bviewer.core.tests.base import BaseViewTestCase


class ArchiveViewsTestCase(BaseViewTestCase):
    """
    Create private album and not.
    Test that only owner have access to private.
    """

    def test_album(self):
        url_first = self.reverse('archive.archive', self.data.album1.id)
        self.assertContent(url_first, 'Waite')
        url_second = self.reverse('archive.archive', self.data.album2.id)
        self.assertContent(url_second, 'Error')

        self.login()
        resp = self.client.get(url_first)
        self.assertEqual(resp.status_code, 302)

        self.assertContent(url_second, 'Waite')