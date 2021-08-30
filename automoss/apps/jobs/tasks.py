
from django.conf import settings
from ...defaults import (
    MOSS_LANGUAGES,
    PROCESSING_STATUS,
    COMPLETED_STATUS,
    FAILED_STATUS,
    SUBMISSION_TYPES,
    FILES_NAME
)
from ..matches.models import Match
from .models import (
    Job,
    Submission
)
from django.utils.timezone import now
from django.core.files.uploadedfile import UploadedFile
from ..core.moss import (
    MOSS,
    MossResult,
    MossException
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

    base_dir = os.path.join(settings.MEDIA_ROOT, str(job.job_id), 'uploads')

    paths = {}

    for file_type in SUBMISSION_TYPES:
        path = os.path.join(base_dir, file_type)
        if os.path.isdir(path):
            paths[file_type] = [os.path.join(path, k)
                                for k in os.listdir(path)]

    if not paths.get(FILES_NAME):
        # TODO raise exception : no files supplied
        job.status = FAILED_STATUS  # TODO detect failure
        job.save()
        return None
    try:
        result = MOSS(job.moss_user.moss_id).generate(
            language=MOSS_LANGUAGES.get(job.language),
            **paths,
            max_matches_until_ignore=job.max_until_ignored,
            num_to_show=job.max_displayed_matches,
            comment=job.comment,
            use_basename=True
        )
    except MossException as e:
        job.status = FAILED_STATUS  # TODO detect failure
        job.save()
        return None

    job.completion_date = now()
    job.status = COMPLETED_STATUS
    job.save()

    # TODO do something with result, e.g., write to DB

    for match in result.matches:
        Match.objects.create(
            first_submission=Submission.objects.get(
                job=job, name=match.name_1),
            second_submission=Submission.objects.get(
                job=job, name=match.name_2),
            first_percentage=match.percentage_1,
            second_percentage=match.percentage_2,
            lines_matched=match.lines_matched,
            line_matches=match.line_matches
        )

    # TODO Save MossResult for backup?

    return result.url
