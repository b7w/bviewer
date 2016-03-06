# -*- coding: utf-8 -*-
from rest_framework.routers import DefaultRouter, DynamicDetailRoute


class ExtraRouter(DefaultRouter):
    """
    Add extra router for actions.
    Allow to call `~action` not only on instance, but on model.
    Url sample /actions/slideshow/get_or_create/.
    """
    routes = DefaultRouter.routes + [
        DynamicDetailRoute(
            url=r'^actions/{prefix}/{methodname}{trailing_slash}$',
            name='actions-{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
    ]

