# -*- coding: utf-8 -*-
from bviewer.core.tests import BaseViewTest


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
        self.assertContent(url_first, 'Waite')
        self.assertContent(url_second, 'Waite')