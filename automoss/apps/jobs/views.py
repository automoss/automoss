import os

from django.contrib.auth.decorators import login_required
from .tasks import process_job
from django.shortcuts import render
from django.template.defaulttags import register
from django.http.response import JsonResponse
from ...defaults import VIEWABLE_LANGUAGES
from ...defaults import STATUSES
from .models import Job

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@login_required
def index(request):
    context = {
        'jobs': request.user.mossuser.job_set.all(),
        'languages': VIEWABLE_LANGUAGES,
        'statuses':  STATUSES
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
        data = {'message': f'started job: {job_id}'}
        return JsonResponse(data, status=200)

    else:

        context = {}
        return render(request, "jobs/new.html", context)
