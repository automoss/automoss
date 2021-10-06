
from ..results.models import MOSSResult, Match
from .models import Job, Submission, JobEvent
from django.utils.timezone import now
from ..moss.pinger import Pinger, LoadStatus
from ..moss.moss import (
    MOSS,
    RecoverableMossException,
    ReportParsingError,
    EmptyResponse,
    FatalMossException,
    MossConnectionError,
    is_valid_moss_url
)
from ...settings import (
    SUPPORTED_LANGUAGES,
    PROCESSING_STATUS,
    UPLOADING_STATUS,
    PARSING_STATUS,
    INQUEUE_STATUS,
    COMPLETED_STATUS,
    FAILED_STATUS,
    SUBMISSION_TYPES,
    FILES_NAME,
    STATUSES,
    JOB_UPLOAD_TEMPLATE,
    DEBUG,

    MIN_RETRIES_COUNT,
    MIN_RETRY_TIME,
    MAX_RETRY_TIME,
    MAX_RETRY_DURATION,
    EXPONENTIAL_BACKOFF_BASE,
    FIRST_RETRY_INSTANT,

    # Events
    UPLOADING_EVENT,
    PROCESSING_EVENT,
    PARSING_EVENT,
    COMPLETED_EVENT,
    FAILED_EVENT,
    RETRY_EVENT,

    HOSTNAME
)
from ..utils.core import retry
import os
import json
import time
import socket
from celery.decorators import task
from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

subject_template = "jobs/email/job-status-subject.txt"
body_template = "jobs/email/job-status.txt"
html_template = "jobs/email/job-status.html"


def send_email_notification(job):
    """ Sends job notification to all emails associated with a job """
    job.user.send_email(
        subject_template,
        body_template,
        html_template,
        {
            "job": job,
            "status": STATUSES.get(job.status),
            "host": HOSTNAME,
            "log": job.jobevent_set.all(),
            "has_link" : job.status == COMPLETED_STATUS
        },
        broadcast=True
    )


@task(name='Upload')
def process_job(job_id):
    """Process a job, given its ID"""

    try:
        job = Job.objects.get(job_id=job_id)
    except Job.DoesNotExist:
        return

    if job.status != INQUEUE_STATUS:
        # A job will only be started if it is in the queue.
        # Prevents jobs from being processed more than once.
        # Necessary because redis and celery store their own caches/lists
        # of jobs, which may cause process_job to be run more than once.
        return

    job.start_date = now()
    logger.info(f'Starting job {job_id} with status {job.status}')

    base_dir = JOB_UPLOAD_TEMPLATE.format(
        user_id=job.user.user_id, job_id=job.job_id)

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
        job.status = FAILED_STATUS
        job.save()

        JobEvent.objects.create(
            job=job, type=FAILED_EVENT, message='No files supplied')

        send_email_notification(job)
        return None

    num_attempts = 0
    url = None
    result = None
    error = None

    for attempt, time_to_sleep in retry(MIN_RETRY_TIME, MAX_RETRY_TIME, EXPONENTIAL_BACKOFF_BASE, MAX_RETRY_DURATION, FIRST_RETRY_INSTANT):
        num_attempts = attempt

        try:
            error = None  # Reset error
            if not is_valid_moss_url(url):
                # Keep retrying until valid url has been generated
                # Do not restart whole job if this succeeds but parsing fails

                def on_upload_start():
                    job.status = UPLOADING_STATUS
                    job.save()
                    JobEvent.objects.create(
                        job=job, type=UPLOADING_EVENT, message='Started uploading files to MOSS')

                def on_upload_finish():
                    JobEvent.objects.create(
                        job=job, type=UPLOADING_EVENT, message='Finished uploading')

                def on_processing_start():
                    job.status = PROCESSING_STATUS
                    job.save()
                    JobEvent.objects.create(
                        job=job, type=PROCESSING_EVENT, message='MOSS started processing files')

                def on_processing_finish():
                    JobEvent.objects.create(
                        job=job, type=PROCESSING_EVENT, message='MOSS finished processing')

                url = MOSS.generate_url(
                    user_id=job.user.moss_id,
                    language=SUPPORTED_LANGUAGES[job.language][1],
                    **paths,
                    max_until_ignored=job.max_until_ignored,
                    max_displayed_matches=job.max_displayed_matches,
                    use_basename=True,

                    # TODO other events to log?
                    # on_start=None,
                    # on_connect=None,

                    on_upload_start=on_upload_start,
                    on_upload_finish=on_upload_finish,

                    on_processing_start=on_processing_start,
                    on_processing_finish=on_processing_finish,
                )

            msg = f'Started parsing MOSS report: {url}'
            logger.info(msg)

            job.status = PARSING_STATUS
            job.save()
            JobEvent.objects.create(job=job, type=PARSING_EVENT, message=msg)

            # Parsing and extraction
            result = MOSS.generate_report(url)
            msg = f'Result finished parsing: {len(result.matches)} matches detected'
            logger.info(msg)
            JobEvent.objects.create(job=job, type=PARSING_EVENT, message=msg)

            break  # Success, do not retry

        except socket.error as e:
            error = MossConnectionError(e.strerror)

        except RecoverableMossException as e:
            error = e  # Handled below
            if isinstance(e, ReportParsingError):
                # Malformed MOSS report... must regenerate
                url = None

        except EmptyResponse:
            # Job ended without any response (i.e., timed out)

            load_status, ping, average_ping = Pinger.determine_load()
            ping_message = f'({ping} vs. {average_ping})'

            if load_status == LoadStatus.NORMAL:
                if attempt >= MIN_RETRIES_COUNT - 1:  # Retry job a minimum number of times
                    msg = f'Moss is not under load {ping_message} - job ({job_id}) will never finish'
                    error = FatalMossException(
                        f"MOSS returned no response at least {MIN_RETRIES_COUNT - 1} times, but isn't under load. The job will never finish.")
                    logger.debug(msg)
                    break

                else:
                    msg = f'MOSS returned no response but is not under load. Will retry {MIN_RETRIES_COUNT - 1 - attempt} more times'

            elif load_status in (LoadStatus.UNDER_LOAD, LoadStatus.UNDER_SEVERE_LOAD):
                msg = f'Moss is under load {ping_message}, retrying job ({job_id})'

            else:
                msg = f'Moss is down {ping_message}, retrying job ({job_id})'

            error = RecoverableMossException(msg)
            logger.debug(msg)

        except FatalMossException as e:
            error = e
            logger.error(f'Fatal moss exception: {e}')
            break  # Will be handled below (result is None)

        except Exception as e:
            error = e
            # Something catastrophic happened
            logger.error(f'Unknown error: {e}')
            break  # Will be handled below (result is None)

        msg = f'(Attempt {attempt + 1}) Error: {error} | Retrying in {time_to_sleep} seconds'

        # We can retry
        logger.warning(msg)
        JobEvent.objects.create(job=job, type=RETRY_EVENT, message=msg)

        time.sleep(time_to_sleep)

    failed = result is None

    # Represents when no more processing of the job will occur
    job.completion_date = now()

    try:
        if failed:
            job.status = FAILED_STATUS
            if error is not None:
                error_message = f'Error: {error}'
            else:
                error_message = 'Maximum processing time exceeded (job has been cancelled)'

            JobEvent.objects.create(
                job=job, type=FAILED_EVENT, message=error_message)
            send_email_notification(job)
            return None

        # Parse result
        moss_result = MOSSResult.objects.create(
            job=job,
            url=result.url
        )

        for match in result.matches:
            first_submission = Submission.objects.filter(
                job=job, submission_id=match.name_1).first()
            second_submission = Submission.objects.filter(
                job=job, submission_id=match.name_2).first()

            # Ensure matching submission is found (avoid future errors)
            if first_submission and second_submission:
                Match.objects.create(
                    moss_result=moss_result,
                    first_submission=first_submission,
                    second_submission=second_submission,
                    first_percentage=match.percentage_1,
                    second_percentage=match.percentage_2,
                    lines_matched=match.lines_matched,
                    line_matches=match.line_matches
                )

        JobEvent.objects.create(
            job=job, type=COMPLETED_EVENT, message='Completed')
        job.status = COMPLETED_STATUS
        send_email_notification(job)

        return result.url

    finally:
        job.save()

        if DEBUG:
            # Calculate average file_size
            num_files = len(paths[FILES_NAME])
            avg_file_size = sum([os.path.getsize(x)
                                for x in paths[FILES_NAME]]) / num_files

            log_info = vars(job).copy()
            log_info.pop('_state', None)
            log_info.update({
                'num_files': num_files,
                'avg_file_size': avg_file_size,
                'moss_id': job.user.moss_id,
                'num_attempts': num_attempts
            })

            # Perform a ping
            Pinger.ping()

            log_info.update({'avg': Pinger.get_average_ping()} or {})
            logger.debug(f'Job info: {log_info}')

            with open('jobs.log', 'a+') as fp:
                log_info['duration'] = (
                    log_info['completion_date'] - log_info['start_date']).total_seconds()
                json.dump(log_info, fp, sort_keys=True, default=str)
                print(file=fp)
