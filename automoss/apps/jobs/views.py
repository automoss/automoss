import os
import json
from json.decoder import JSONDecodeError

from django.contrib.auth.decorators import login_required
from .tasks import process_job
from django.shortcuts import render
from django.template.defaulttags import register
from django.http.response import JsonResponse
from django.utils.datastructures import MultiValueDictKeyError
from django.core.serializers import serialize
from django.utils.safestring import mark_safe

from ...defaults import (
    VIEWABLE_LANGUAGES,
    STATUSES,
    COMPLETED_STATUS,
    POLLING_TIME
)
from .models import Job

@register.filter(is_safe=True)
def js(obj):
    return mark_safe(json.dumps(obj))


@login_required
def index(request):
    context = {
        'languages': VIEWABLE_LANGUAGES,
        'statuses':  STATUSES,
        'completed': COMPLETED_STATUS,
        'poll': POLLING_TIME
    }
    return render(request, "jobs/index.html", context)


@login_required
def new(request):
    if request.method == 'POST':

        # TODO read params from request
        # DB - Create job
        new_job = Job.objects.create(moss_user=request.user.mossuser, language='PY', max_until_ignored=1000,
                                     max_displayed_matches=1000)

        job_id = new_job.job_id

        # TODO get from database
        moss_user_id = request.user.mossuser.moss_id

        base_dir = os.path.join('media', str(job_id), 'uploads')

        for file_type in ('files', 'base_files'):
            for f in request.FILES.getlist(file_type):
                parent = os.path.join(base_dir, file_type)
                os.makedirs(parent, exist_ok=True)
                f_path = os.path.join(parent, f.name)

                # TODO add validation (extensions, size, etc.)

                print('Writing to', f_path)
                with open(f_path, 'wb') as fp:
                    fp.write(f.read())

        process_job.delay(job_id)

        # Return useful information
        data = json.loads(serialize('json', [new_job]))[0]['fields']
        return JsonResponse(data, status=200, safe=False)

    else:

        context = {}
        return render(request, "jobs/new.html", context)


@login_required
def get_jobs(request):
    # Return jobs of user
    results = Job.objects.filter(moss_user=request.user.mossuser).values()
    return JsonResponse(list(results), status=200, safe=False)


@login_required
def get_statuses(request):

    job_ids = []
    try:
        if request.method == 'POST':
            body = json.loads(request.body)
            job_ids = body['job_ids']
        else:
            job_ids = request.GET['job_ids'].split(',')

    except (JSONDecodeError, IndexError, MultiValueDictKeyError) as e:
        pass  # Invalid request - TODO return error

    if not isinstance(job_ids, list):
        job_ids = []

    results = Job.objects.filter(
        moss_user=request.user.mossuser, job_id__in=job_ids)

    data = {j.job_id: j.status for j in results}
    return JsonResponse(data, status=200)
