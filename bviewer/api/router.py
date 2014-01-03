# -*- coding: utf-8 -*-
from rest_framework.routers import DefaultRouter, Route


class ExtraRouter(DefaultRouter):
    """
    Add extra router for actions.
    Allow to call `~action` not only on instance, but on model.
    Url sample /actions/slideshow/get_or_create/.
    """
    routes = DefaultRouter.routes + [
        Route(
            url=r'^actions/{prefix}/{methodname}{trailing_slash}$',
            mapping={
                '{httpmethod}': '{methodname}',
            },
            name='actions-{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
    ]

