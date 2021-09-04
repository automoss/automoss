
from ..results.models import MOSSResult, Match
from .models import Job, Submission
from django.utils.timezone import now
from django.core.files.uploadedfile import UploadedFile
from ..moss.moss import (
    MOSS,
    Result,
    MossException,
    is_valid_moss_url
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
    MAX_RETRIES,
    DEBUG
)
import os
import json
import time
from celery.decorators import task
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)


def get_moss_language(language):
    return next((SUPPORTED_LANGUAGES[l][1] for l in SUPPORTED_LANGUAGES if l == language), None)


LOG_FILE = 'jobs.log'


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
        if not os.path.isdir(path):
            continue  # Ignore if none of these files were submitted

        paths[file_type] = []
        for f in os.listdir(path):
            file_path = os.path.join(path, f)
            if os.path.getsize(file_path) > 0:
                # Only add non-empty files
                paths[file_type].append(file_path)

    if not paths.get(FILES_NAME):
        # TODO raise exception : no files supplied
        job.status = FAILED_STATUS  # TODO detect failure
        job.save()
        return None

    moss = MOSS(job.user.moss_id)

    url = None
    result = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            if not is_valid_moss_url(url):
                # Keep retrying until valid url has been generated
                # Do not restart whole job if this succeeds but parsing fails
                url = moss.generate_url(
                    language=get_moss_language(job.language),
                    **paths,
                    max_until_ignored=job.max_until_ignored,
                    max_displayed_matches=job.max_displayed_matches,
                    use_basename=True
                )
                print(f'Generated url: "{url}"')

            # TODO set status to parsing?

            print('Start parsing report')
            # Parsing and extraction
            result = moss.generate_report(url)
            print('Result finished parsing:', len(
                result.matches), 'matches detected.')

            break  # Success, do not retry

        except MossException as e:
            # An error on Moss' side occurred... retry
            time_to_sleep = EXPONENTIAL_BACKOFF_BASE ** attempt
            # TODO - log
            print(
                f'(Attempt {attempt}) Error: {e}. Retrying in {time_to_sleep} seconds')
            time.sleep(time_to_sleep)

    # Represents when no more processing of the job will occur
    job.completion_date = now()

    if result is None:  # No result
        job.status = FAILED_STATUS  # TODO detect failure
        job.save()
        return None

    # Success
    job.status = COMPLETED_STATUS
    job.save()

    if DEBUG:
        # Calculate average file_size
        num_files = len(paths[FILES_NAME])
        avg_file_size = sum([os.path.getsize(x)
                            for x in paths[FILES_NAME]])/num_files

        log_info = vars(job).copy()
        log_info.pop('_state', None)
        log_info.update({
            'num_files': num_files,
            'avg_file_size': avg_file_size
        })

        with open(LOG_FILE, 'a+') as fp:
            log_info['duration'] = (
                log_info['completion_date'] - log_info['start_date']).total_seconds()
            json.dump(log_info, fp, sort_keys=True, default=str)
            print(file=fp)

    moss_result = MOSSResult.objects.create(
        job=job,
        url=result.url
    )

    for match in result.matches:
        Match.objects.create(
            moss_result=moss_result,
            first_submission=Submission.objects.get(
                job=job, submission_id=match.name_1),
            second_submission=Submission.objects.get(
                job=job, submission_id=match.name_2),
            first_percentage=match.percentage_1,
            second_percentage=match.percentage_2,
            lines_matched=match.lines_matched,
            line_matches=match.line_matches
        )

    return result.url
