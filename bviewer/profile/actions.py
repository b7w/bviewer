# -*- coding: utf-8 -*-
import logging
from django.contrib import admin
from django.db.models import F
from django.shortcuts import redirect, render

from bviewer.core.utils import set_time_from_exif
from bviewer.core.files.storage import ImageStorage
from bviewer.profile.forms import BulkTimeUpdateForm


logger = logging.getLogger(__name__)


def bulk_time_update(model_admin, request, queryset):
    form = None
    if 'apply' in request.POST:
        form = BulkTimeUpdateForm(request.POST)
        if form.is_valid():
            method = form.cleaned_data['method']
            interval = form.cleaned_data['interval']
            if interval and method == BulkTimeUpdateForm.ADD:
                queryset.update(time=F('time') + interval)
            if interval and method == BulkTimeUpdateForm.SUBTRACT:
                queryset.update(time=F('time') - interval)

            model_admin.message_user(request, '{0} {1}'.format(method.capitalize(), interval))
            return redirect(request.get_full_path())

    if not form:
        form = BulkTimeUpdateForm(initial={'_selected_action': request.POST.getlist(admin.ACTION_CHECKBOX_NAME)})
    return render(request, 'profile/bulk_time_update.html', {
        'title': 'Bulk time update',
        'form': form,
        'dimensions': BulkTimeUpdateForm.DIMENSIONS,
    })


def update_time_from_exif(model_admin, request, queryset):
    for image in queryset:
        storage = ImageStorage(image.album.gallery)
        set_time_from_exif(storage, image, save=True)
