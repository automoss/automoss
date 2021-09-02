
from ..results.models import MOSSResult, Match
from .models import Job, Submission
from django.utils.timezone import now
from django.core.files.uploadedfile import UploadedFile
from ..moss.moss import (
    MOSS,
    Result,
    MossException
)
from ...settings import (
    SUPPORTED_LANGUAGES,
    PROCESSING_STATUS,
    COMPLETED_STATUS,
    FAILED_STATUS,
    SUBMISSION_TYPES,
    FILES_NAME,
    JOB_UPLOAD_TEMPLATE,
    EXPONENTIAL_BACKOFF_BASE,
    MAX_RETRIES
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

    base_dir = JOB_UPLOAD_TEMPLATE.format(job_id=job.job_id)

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

    result = None

    for attempt in range(MAX_RETRIES + 1):
        try:
            result = MOSS(job.moss_user.moss_id).generate(
                language=get_moss_language(job.language),
                **paths,
                max_until_ignored=job.max_until_ignored,
                max_displayed_matches=job.max_displayed_matches,
                comment=job.comment,
                use_basename=True
            )
            break  # Success, do not retry

        except MossException as e:
            # An error on Moss' side occurred... retry
            print('Error:', e)  # TODO - log

        time.sleep(EXPONENTIAL_BACKOFF_BASE ** attempt)

    # Represents when no more processing of the job will occur
    job.completion_date = now()

    if result is None:  # No result
        job.status = FAILED_STATUS  # TODO detect failure
        job.save()
        return None

    # Success
    job.status = COMPLETED_STATUS
    job.save()

    moss_result = MOSSResult.objects.create(
        job=job,
        url=result.url
    )

    for match in result.matches:
        Match.objects.create(
            moss_result=moss_result,
            first_submission=Submission.objects.get(
                job=job, name=match.name_1),
            second_submission=Submission.objects.get(
                job=job, name=match.name_2),
            first_percentage=match.percentage_1,
            second_percentage=match.percentage_2,
            lines_matched=match.lines_matched,
            line_matches=match.line_matches
        )

    return result.url
