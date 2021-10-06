from django.apps import AppConfig

from ...settings import COMPLETED_STATUS, FAILED_STATUS


class JobsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'automoss.apps.jobs'

    def ready(self):
        # Must import models here to avoid AppRegistryNotReady exception
        from .tasks import process_job
        from .models import Job
        from ..utils.core import is_main_thread
        from ...celery import app
        from ...settings import INQUEUE_STATUS

        if is_main_thread():  # pragma: no cover
            num_purged = app.control.purge()
            print('Purged', num_purged, 'tasks.')
            unfinished_jobs = Job.objects.exclude(
                status__in=[COMPLETED_STATUS, FAILED_STATUS])
            for job in unfinished_jobs:
                print(' * Restarting unfinished job',
                      job.job_id, 'with status', job.status)
                job.status = INQUEUE_STATUS
                job.save()
                process_job.delay(job.job_id)
