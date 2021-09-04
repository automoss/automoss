
import os
import json
from json.decoder import JSONDecodeError

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.template.defaulttags import register
from django.http.response import JsonResponse
from django.utils.datastructures import MultiValueDictKeyError
from django.core.serializers import serialize
from django.utils.safestring import mark_safe

from .tasks import process_job

from .models import (
    Job,
    Submission,
    get_default_comment
)
from ..results.models import Match
from ...settings import (
    STATUS_CONTEXT,
    SUBMISSION_CONTEXT,
    MOSS_CONTEXT,
    LANGUAGE_CONTEXT,
    UI_CONTEXT,

    READABLE_LANGUAGE_MAPPING,
    SUBMISSION_TYPES,

    SUBMISSION_UPLOAD_TEMPLATE
)


@register.filter(is_safe=True)
def js(obj):
    return mark_safe(json.dumps(obj))


@login_required
def index(request):
    context = {
        **STATUS_CONTEXT,
        **LANGUAGE_CONTEXT,
        **UI_CONTEXT,
        **SUBMISSION_CONTEXT,
        **MOSS_CONTEXT
    }
    return render(request, "jobs/jobs.html", context)


@login_required
def new(request):
    if request.method == 'POST':
        print(READABLE_LANGUAGE_MAPPING)
        print(request.POST.get('job-language'))
        # TODO validate form
        language = READABLE_LANGUAGE_MAPPING.get(
            request.POST.get('job-language'))  # TODO throw error if none
        max_until_ignored = request.POST.get('job-max-until-ignored')
        max_displayed_matches = request.POST.get('job-max-displayed-matches')
        comment = request.POST.get('job-name')

        # TODO validate options and reject if incorrect

        new_job = Job.objects.create(
            user=request.user,
            language=language,
            comment=comment,
            max_until_ignored=max_until_ignored,
            max_displayed_matches=max_displayed_matches
        )

        job_id = new_job.job_id

        # TODO get from database
        moss_user_id = request.user.moss_id

        for file_type in SUBMISSION_TYPES:
            for f in request.FILES.getlist(file_type):

                # TODO add validation (extensions, size, etc.)

                submission = Submission.objects.create(
                    job=new_job, name=f.name, file_type=file_type)

                file_path = SUBMISSION_UPLOAD_TEMPLATE.format(
                    job_id=job_id,
                    file_type=file_type,
                    file_id=submission.submission_id
                )

                # Ensure directory exists (only run once)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                print('Writing to', file_path)
                with open(file_path, 'wb') as fp:
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
    results = Job.objects.filter(user=request.user).values()
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
        user=request.user, job_id__in=job_ids)

    data = {j.job_id: j.status for j in results}
    return JsonResponse(data, status=200)
