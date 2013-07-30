# -*- coding: utf-8 -*-


class ViewerError(Exception):
    pass


class ResizeOptionsError(ViewerError):
    pass


class FileError(ViewerError):
    pass


class HttpError(ViewerError):
    pass