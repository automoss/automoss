
from ...defaults import (
    MOSS_LANGUAGES,
    PROCESSING_STATUS,
    COMPLETED_STATUS,
    FAILED_STATUS
)
from .models import Job
from ..reports.models import MOSSReport
from django.core.files.uploadedfile import UploadedFile
from ..core.moss import (
    MOSS,
    MossResult
)
import os
import time
from celery.decorators import task
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)


@task(name='Upload')
def process_job(job_id):
    """Basic interface for generating a report from MOSS"""

    job = Job.objects.get(job_id=job_id)

    job.status = PROCESSING_STATUS
    job.save()

    base_dir = os.path.join('media', str(job.job_id), 'uploads')

    paths = {
        'files': [],
        'base_files': []
    }
    for file_type in paths:
        path = os.path.join(base_dir, file_type)
        if os.path.isdir(path):
            paths[file_type] = [os.path.join(path, k)
                                for k in os.listdir(path)]

    result = MOSS(job.moss_user.moss_id).generate(
        language=MOSS_LANGUAGES.get(job.language),
        **paths,
        max_matches_until_ignore=job.max_until_ignored,
        num_to_show=job.max_displayed_matches,
        comment=job.comment,
        use_basename=True
    )

    # TODO do something with result, e.g., write to DB

    MOSSReport.objects.create(job=job, url=result.url)

    # job.status = FAILED_STATUS # TODO detect failure
    job.status = COMPLETED_STATUS
    job.save()

    return result.url
