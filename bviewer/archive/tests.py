# -*- coding: utf-8 -*-
from bviewer.core.tests.base import BaseViewTest


class ArchiveViewsTest(BaseViewTest):
    """
    Create private gallery and not.
    Test that only owner have access to private.
    """

    def test_gallery(self):
        url_first = self.reverse('archive.archive', self.data.gallery1.id)
        self.assertContent(url_first, 'Waite')
        url_second = self.reverse('archive.archive', self.data.gallery2.id)
        self.assertContent(url_second, 'Error')

        self.login()
        resp = self.client.get(url_first)
        self.assertEqual(resp.status_code, 302)

        self.assertContent(url_second, 'Waite')