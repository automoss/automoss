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

from .models import get_default_comment

from ...defaults import (
    LANGUAGES,
    READABLE_TO_CODE_LANGUAGES,
    STATUSES,
    COMPLETED_STATUS,
    UPLOADING_STATUS,
    PROCESSING_STATUS,
    FAILED_STATUS,
    POLLING_TIME,
    DEFAULT_LANGUAGE,
    MAX_DISPLAYED_MATCHES,
    MAX_UNTIL_IGNORED,
    SUBMISSION_TYPES
)
from .models import (
    Job,
    Submission
)


@register.filter(is_safe=True)
def js(obj):
    return mark_safe(json.dumps(obj))


@login_required
def index(request):
    context = {
        'languages': LANGUAGES,
        'statuses':  STATUSES,
        'completed': COMPLETED_STATUS,
        'uploading': UPLOADING_STATUS,
        'processing': PROCESSING_STATUS,
        'failed': FAILED_STATUS,
        'poll': POLLING_TIME,
        'max_until_ignored': MAX_UNTIL_IGNORED,
        'max_displayed_matches': MAX_DISPLAYED_MATCHES
    }
    return render(request, "jobs/index.html", context)


@login_required
def new(request):
    if request.method == 'POST':
        language = READABLE_TO_CODE_LANGUAGES.get(
            request.POST.get('job-language', DEFAULT_LANGUAGE))
        max_until_ignored = request.POST.get(
            'job-max-until-ignored', MAX_UNTIL_IGNORED)
        max_displayed_matches = request.POST.get(
            'job-max-displayed-matches', MAX_DISPLAYED_MATCHES)
        comment = request.POST.get('job-name', get_default_comment())

        # TODO validate options and reject if incorrect

        info = {
            'moss_user': request.user.mossuser,
            'language': language,
            'comment': comment,
            'max_until_ignored': max_until_ignored,
            'max_displayed_matches': max_displayed_matches
        }
        new_job = Job.objects.create(**info)

        job_id = new_job.job_id

        # TODO get from database
        moss_user_id = request.user.mossuser.moss_id

        base_dir = os.path.join('media', str(job_id), 'uploads')

        for file_type in SUBMISSION_TYPES:
            for f in request.FILES.getlist(file_type):
                parent = os.path.join(base_dir, file_type)
                os.makedirs(parent, exist_ok=True)
                file_name = f.name
                f_path = os.path.join(parent, file_name)

                # TODO add validation (extensions, size, etc.)

                print('Writing to', f_path)
                with open(f_path, 'wb') as fp:
                    fp.write(f.read())

                Submission.objects.create(job=new_job, name=file_name, file_type=file_type)

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
