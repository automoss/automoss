import os

from ..utils.encoding import base64_decode
from .tasks import process_job
from django.shortcuts import render
from django.http.response import JsonResponse

from .models import Job


def index(request):
    context = {"jobs": Job.objects.all()}
    return render(request, "jobs/index.html", context)


def new(request):
    if request.method == 'POST':

        # DB - Create job
        # TODO read params from request
        new_job = Job(language='PY', max_until_ignored=1000,
                      max_displayed_matches=1000)
        new_job.save()

        job_id = new_job.job_id

        # TODO get from database
        moss_user_id = 1

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
