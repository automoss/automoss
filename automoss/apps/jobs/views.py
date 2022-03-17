
import os
import json

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.template.defaulttags import register
from django.http.response import JsonResponse
from django.core.serializers import serialize
from django.utils.safestring import mark_safe
from django.views import View
from django.utils.timezone import now

from .tasks import process_job

from .models import (
    Job,
    Submission,
    JobEvent
)
from ...settings import (
    STATUS_CONTEXT,
    SUBMISSION_CONTEXT,
    MOSS_CONTEXT,
    LANGUAGE_CONTEXT,
    ARCHIVE_CONTEXT,
    UI_CONTEXT,

    READABLE_LANGUAGE_MAPPING,
    SUBMISSION_TYPES,

    SUBMISSION_UPLOAD_TEMPLATE,

    INQUEUE_EVENT,
    CREATED_EVENT,
    FILES_NAME,

    MAX_UNTIL_IGNORED_RANGE,
    MAX_DISPLAYED_MATCHES_RANGE,

    CANCELLED_STATUS,
    INQUEUE_STATUS,
    CANCELLED_EVENT
)
from ...celery import app
from ..utils.core import in_range


@register.filter(is_safe=True)
def js(obj):
    """Helper method for safely rendering JSON to a webpage"""
    return mark_safe(json.dumps(obj))


@method_decorator(login_required, name='dispatch')
class Index(View):
    """ Index view for Jobs """
    template = 'jobs/index.html'
    context = {
        **STATUS_CONTEXT,
        **LANGUAGE_CONTEXT,
        **ARCHIVE_CONTEXT,
        **UI_CONTEXT,
        **SUBMISSION_CONTEXT,
        **MOSS_CONTEXT
    }

    def get(self, request):
        """ Get jobs """
        return render(request, self.template, self.context)


@method_decorator(login_required, name='dispatch')
class New(View):
    """ Job creation view """

    def post(self, request):
        """ Post new job """
        posted_language = request.POST.get('job-language')
        language = READABLE_LANGUAGE_MAPPING.get(posted_language)

        if language is None:
            data = {
                'message': f'Unsupported language selected ({language})'
            }
            return JsonResponse(data, status=400)

        max_until_ignored = request.POST.get('job-max-until-ignored')
        if not in_range(max_until_ignored, MAX_UNTIL_IGNORED_RANGE):
            data = {
                'message': 'Invalid parameter: Max until ignored'
            }
            return JsonResponse(data, status=400)

        max_displayed_matches = request.POST.get('job-max-displayed-matches')
        if not in_range(max_displayed_matches, MAX_DISPLAYED_MATCHES_RANGE):
            data = {
                'message': 'Invalid parameter: Max displayed matches'
            }
            return JsonResponse(data, status=400)

        if not request.FILES.getlist(FILES_NAME):
            data = {
                'message': 'No files submitted'
            }
            return JsonResponse(data, status=400)

        comment = request.POST.get('job-name')

        num_students = len(request.FILES.getlist(FILES_NAME))

        new_job = Job.objects.create(
            user=request.user,
            language=language,
            num_students=num_students,
            comment=comment,
            max_until_ignored=max_until_ignored,
            max_displayed_matches=max_displayed_matches
        )
        JobEvent.objects.create(job=new_job, type=CREATED_EVENT,
                                message=f'Created job for {num_students} students with language=\'{posted_language}\', {max_until_ignored=} and {max_displayed_matches=}')

        job_id = new_job.job_id

        for file_type in SUBMISSION_TYPES:
            for f in request.FILES.getlist(file_type):

                submission = Submission.objects.create(
                    job=new_job, name=f.name, file_type=file_type)

                file_path = SUBMISSION_UPLOAD_TEMPLATE.format(
                    user_id=request.user.user_id,
                    job_id=job_id,
                    file_type=file_type,
                    file_id=submission.submission_id
                )

                # Ensure directory exists (only run once)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                with open(file_path, 'wb') as fp:
                    fp.write(f.read())

        JobEvent.objects.create(
            job=new_job, type=INQUEUE_EVENT, message='Placed in the processing queue')

        process_job.delay(job_id)

        data = json.loads(serialize('json', [new_job]))[0]['fields']
        return JsonResponse(data, status=200, safe=False)


@method_decorator(login_required, name='dispatch')
class Cancel(View):

    def post(self, request):
        """ Cancel a user's job """
        job_id = json.loads(request.body.decode("UTF-8")).get('job_id')
        try:
            job = Job.objects.user_jobs(request.user).get(job_id=job_id)
        except Job.DoesNotExist:
            data = {
                'message': f'Job does not exist ({job_id})'
            }
            return JsonResponse(data, status=404, safe=False)

        def get_task_id(job_id):  # Find task currently being processed by celery
            i = app.control.inspect()
            for job_list in (i.active, i.scheduled, i.reserved):
                for jobs in job_list().values():
                    for job in jobs:
                        if job['args'][0] == job_id:
                            return job['id']
            return None

        task_id = get_task_id(job_id)

        if task_id is not None:
            app.control.revoke(task_id, terminate=True)

        job.status = CANCELLED_STATUS
        job.completion_date = now()
        job.save()

        JobEvent.objects.create(
            job=job, type=CANCELLED_EVENT, message='Job cancelled by user')

        return JsonResponse(job.job_id, status=200, safe=False)


@method_decorator(login_required, name='dispatch')
class Remove(View):

    def post(self, request):
        """ Remove a user's job """
        job_id = json.loads(request.body.decode("UTF-8")).get('job_id')

        try:
            job = Job.objects.user_jobs(request.user).get(job_id=job_id)
        except Job.DoesNotExist:
            data = {
                'message': f'Job does not exist ({job_id})'
            }
            return JsonResponse(data, status=404, safe=False)

        job.delete()
        return JsonResponse({
            'message': 'Success'
        }, status=200, safe=False)


@method_decorator(login_required, name='dispatch')
class Retry(View):

    def post(self, request):
        """ Retry a user's job """
        job_id = json.loads(request.body.decode("UTF-8")).get('job_id')

        try:
            job = Job.objects.user_jobs(request.user).get(job_id=job_id)
        except Job.DoesNotExist:
            data = {
                'message': f'Job does not exist ({job_id})'
            }
            return JsonResponse(data, status=404, safe=False)
     
        job.status = INQUEUE_STATUS
        job.save()
        JobEvent.objects.create(
            job=job, type=INQUEUE_EVENT, message='Restarting... Placed in processing queue')
        process_job.delay(job_id)

        return JsonResponse({
            'message': 'Success'
        }, status=200, safe=False)


@method_decorator(login_required, name='dispatch')
class JSONJobs(View):
    """ JSON view of Jobs """

    def get(self, request):
        """ Get user's jobs """
        results = Job.objects.user_jobs(request.user).values()
        return JsonResponse(list(results), status=200, safe=False)


@method_decorator(login_required, name='dispatch')
class JSONStatuses(View):
    """ JSON view of statuses """

    def get(self, request):
        """ Get statuses of requested jobs (by ID) """
        job_ids = request.GET.get('job_ids', '').split(',')
        results = Job.objects.user_jobs(
            request.user).filter(job_id__in=job_ids)

        data = {j.job_id: j.status for j in results}
        return JsonResponse(data, status=200)


@method_decorator(login_required, name='dispatch')
class JSONJobEvents(View):
    """ JSON view of job events """

    def get(self, request):
        """ Get statuses of requested jobs (by ID) """
        job_ids = request.GET.get('job_ids', '').split(',')
        results = Job.objects.user_jobs(
            request.user).filter(job_id__in=job_ids)

        data = {
            j.job_id: [{'type': x.type, 'str': str(
                x)} for x in JobEvent.objects.filter(job=j)]
            for j in results
        }

        return JsonResponse(data, status=200)
