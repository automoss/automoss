
from ..matches.models import Match
from .models import Job
from ..submissions.models import Submission
from django.utils.timezone import now
from django.core.files.uploadedfile import UploadedFile
from ..moss.moss import (
    MOSS,
    MossResult,
    MossException
)
from ...settings import (
    SUPPORTED_LANGUAGES,
    PROCESSING_STATUS,
    COMPLETED_STATUS,
    FAILED_STATUS,
    SUBMISSION_TYPES,
    FILES_NAME,
    JOB_UPLOAD_TEMPLATE
)
import os
import time
from celery.decorators import task
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)


def get_moss_language(language):
    return next((SUPPORTED_LANGUAGES[l][1] for l in SUPPORTED_LANGUAGES if l == language), None)


@task(name='Upload')
def process_job(job_id):
    """Basic interface for generating a report from MOSS"""

    job = Job.objects.get(job_id=job_id)
    job.status = PROCESSING_STATUS
    job.save()

    base_dir = JOB_UPLOAD_TEMPLATE.format(job.job_id)

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
            language=get_moss_language(job.language),
            **paths,
            max_until_ignored=job.max_until_ignored,
            max_displayed_matches=job.max_displayed_matches,
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
