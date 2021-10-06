from django.contrib.auth import login
from ...settings import SUBMISSION_UPLOAD_TEMPLATE
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from .models import Match
from ..jobs.models import Job
from ...settings import SUPPORTED_LANGUAGES, MATCH_CONTEXT
import os


@method_decorator(login_required, name='dispatch')
class Index(View):
    """ Result Index View """
    template = "results/index.html"

    def get(self, request, job_id):
        """ Get result """
        context = {
            'job': Job.objects.user_jobs(request.user).get(job_id=job_id),
            'matches': Match.objects.user_matches(request.user).filter(moss_result__job__job_id=job_id).order_by('-lines_matched')
        }
        return render(request, self.template, context)


@method_decorator(login_required, name='dispatch')
class ResultMatch(View):
    """ Match View """

    template = "results/match.html"

    def get(self, request, job_id, match_id):
        """ Get match """
        match = Match.objects.user_matches(request.user).get(
            match_id=match_id)
        submissions = {
            'first': match.first_submission,
            'second': match.second_submission
        }

        # Add IDs to matches to ensure matching
        match_info = {k: v for k, v in enumerate(match.line_matches, start=1)}

        blocks = {}

        match_numbers = None
        for submission_type, submission in submissions.items():

            file_path = SUBMISSION_UPLOAD_TEMPLATE.format(
                user_id=request.user.user_id,
                job_id=job_id,
                file_type='files',
                file_id=submission.submission_id
            )

            if not os.path.exists(file_path):
                continue

            with open(file_path) as fp:
                lines = fp.readlines()

            blocks[submission_type] = []
            current = 0

            sorted_info = sorted(
                match_info.items(), key=lambda item: item[-1][submission_type]['from'])
            if match_numbers is None:
                match_numbers = [x[0] for x in sorted_info]
            
            for match_id, match_lines in sorted_info:
                # TODO maybe return list of lines, not joined
                blocks[submission_type].append({
                    'text': ''.join(lines[current:match_lines[submission_type]['from']-1])
                })
                current = match_lines[submission_type]['to']
                blocks[submission_type].append({
                    'id': match_id,
                    'text': ''.join(lines[match_lines[submission_type]['from']-1:current])
                })

            # Get rest of file
            blocks[submission_type].append({
                'text': ''.join(lines[current:])
            })

        job = Job.objects.user_jobs(request.user).get(job_id=job_id)
        # Get highlighter name
        job_language = SUPPORTED_LANGUAGES[job.language][3]

        context = {
            'submissions': submissions,
            'match_numbers': match_numbers,
            'blocks': blocks,
            'language': job_language,
            'job': job,
            **MATCH_CONTEXT
        }
        return render(request, self.template, context)
