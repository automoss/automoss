
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
    Match,
    Submission,
    get_default_comment
)

from ...settings import (
    STATUS_CONTEXT,
    SUBMISSION_CONTEXT,
    MOSS_CONTEXT,
    LANGUAGE_CONTEXT,
    UI_CONTEXT,

    READABLE_LANGUAGE_MAPPING,
    SUBMISSION_TYPES,

    JOB_UPLOAD_TEMPLATE
)


@register.filter(is_safe=True)
def js(obj):
    return mark_safe(json.dumps(obj))


@login_required
def result(request, job_id):
    context = {
        'matches': Match.objects.filter(moss_result__job__job_id=job_id)
    }
    return render(request, "results/index.html", context)

@login_required
def index(request):
    context = {
        **STATUS_CONTEXT,
        **LANGUAGE_CONTEXT,
        **UI_CONTEXT,
        **SUBMISSION_CONTEXT,
        **MOSS_CONTEXT
    }
    return render(request, "jobs/index.html", context)


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
            moss_user=request.user.mossuser,
            language=language,
            comment=comment,
            max_until_ignored=max_until_ignored,
            max_displayed_matches=max_displayed_matches
        )

        job_id = new_job.job_id

        # TODO get from database
        moss_user_id = request.user.mossuser.moss_id

        base_dir = JOB_UPLOAD_TEMPLATE.format(job_id)

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

                Submission.objects.create(
                    job=new_job, name=file_name, file_type=file_type)

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
