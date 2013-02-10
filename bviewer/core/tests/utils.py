# -*- coding: utf-8 -*-

from django.test import TestCase

from bviewer.core.models import ProxyUser
from bviewer.core.utils import domain_match, get_gallery_user


class RequestMock(object):
    def __init__(self, host):
        self.user = None
        self.host = host

    def get_host(self):
        return self.host

    def set_user(self, name, url, is_auth=True):
        self.user = ProxyUser.objects.safe_get(username=name, url=url)
        #self.user.save( )
        if not is_auth:
            self.user.is_authenticated = lambda: False


class UtilsTest(TestCase):
    def test_re_domain(self):
        """
        Tests domain match
        """
        match = domain_match.match('demo.test.local')
        assert match
        assert match.groups() == (None, 'demo', 'test', 'local', '')

        match = domain_match.match('www.demo.test.local')
        assert match
        assert match.groups() == ('www', 'demo', 'test', 'local', '')

        match = domain_match.match('demo.test.local:8000')
        assert match
        assert match.groups() == (None, 'demo', 'test', 'local', '8000')

        match = domain_match.match('172.17.1.10:80')
        assert match is None

    def test_gallery_user(self):
        """
        Tests get_gallery_user
        """
        ProxyUser.objects.create(username='User')
        ProxyUser.objects.create(username='User2')
        ProxyUser.objects.create(username='User3')

        holder, url = get_gallery_user(RequestMock('user.test.com'))
        assert holder.username == 'User'
        assert url == ''

        holder, url = get_gallery_user(RequestMock('www.user.test.com:8000'))
        assert holder.username == 'User'
        assert url == ''

        holder, url = get_gallery_user(RequestMock('www.user.test.com'))
        assert holder.username == 'User'
        assert url == ''

        holder, url = get_gallery_user(RequestMock('user.test.com'), 'user')
        assert holder.username == 'User'
        assert url == ''

        holder, url = get_gallery_user(RequestMock('user.test.com'), 'user')
        assert holder.username == 'User'
        assert url == ''

        holder, url = get_gallery_user(RequestMock('user.test.com'), 'user2')
        assert holder.username == 'User'
        assert url == ''

        holder, url = get_gallery_user(RequestMock('test.com'), 'user')
        assert holder.username == 'User'
        assert url == 'user/'

        request = RequestMock('user.test.com')
        request.set_user('User2', 'user2')
        holder, url = get_gallery_user(request, 'user3')
        assert holder.username == 'User'
        assert url == ''

        request = RequestMock('test.com')
        request.set_user('User2', 'user2')
        holder, url = get_gallery_user(request, 'user3')
        assert holder.username == 'User3'
        assert url == 'user3/'

        request = RequestMock('test.com')
        request.set_user('User2', 'user2')
        holder, url = get_gallery_user(request)
        assert holder.username == 'User2'
        assert url == 'user2/'

        request = RequestMock('test.com')
        request.set_user('User2', 'user2', is_auth=False)
        holder, url = get_gallery_user(request)
        assert not holder
        assert url == ''


