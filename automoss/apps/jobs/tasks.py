
from ...defaults import (
    MOSS_LANGUAGES
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

    result = MOSS(job.mossuser.moss_id).generate(
        language=MOSS_LANGUAGES.get(job.language),
        **paths,
        max_matches_until_ignore=job.max_until_ignored,
        num_to_show=job.max_displayed_matches,
        comment=job.comment,
        use_basename=True
    )

    # TODO do something with result, e.g., write to DB

    MOSSReport.objects.create(job=job, url=result.url)

    job.status = 'COM'
    job.save()

    return result.url
