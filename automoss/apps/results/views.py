from django.contrib.auth import login
from ...settings import SUBMISSION_UPLOAD_TEMPLATE
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from .models import Match

# def match_user_is(user):
#     return {"moss_result__job__user": user}

# def job_user_is(user):
#     return {"moss_result__job__user": user}

# @login_required
# def index(request, job_id):
#     context = {
#         'matches': Match.objects.filter(moss_result__job__job_id=job_id, **match_user_is(request.user))
#     }
#     return render(request, "results/index.html", context)

from ..jobs.models import Job
from ...settings import SUPPORTED_LANGUAGES


@method_decorator(login_required, name='dispatch')
class Index(View):
    """ Result Index View """
    template = "results/index.html"

    def get(self, request, job_id):
        """ Get result """
        context = {
            # , **match_user_is(request.user))
            'job': Job.objects.get(job_id=job_id),
            'matches': Match.objects.filter(moss_result__job__job_id=job_id)
        }
        return render(request, self.template, context)

@method_decorator(login_required, name='dispatch')
class ResultMatch(View):
    """ Match View """

    template = "results/match.html"

    def get(self, request, job_id, match_id):
        """ Get match """
        match = Match.objects.get(
            match_id=match_id)  # , **match_user_is(request.user))
        submissions = {
            'first': match.first_submission,
            'second': match.second_submission
        }

        # Add IDs to matches to ensure matching
        match_info = {k: v for k, v in enumerate(match.line_matches, start=1)}

        blocks = {}

        for submission_type, submission in submissions.items():

            file_path = SUBMISSION_UPLOAD_TEMPLATE.format(
                job_id=job_id,
                file_type='files',
                file_id=submission.submission_id
            )

            with open(file_path) as fp:
                lines = fp.readlines()

            blocks[submission_type] = []
            current = 0

            sorted_info = sorted(
                match_info.items(), key=lambda item: item[-1][submission_type]['from'])
            for match_id, match_lines in sorted_info:
                # TODO maybe return list of lines, not joined
                blocks[submission_type].append({
                    'text': ''.join(lines[current:match_lines[submission_type]['from']])
                })
                current = match_lines[submission_type]['to']
                blocks[submission_type].append({
                    'id': match_id,
                    'text': ''.join(lines[match_lines[submission_type]['from']:current])
                })

            # Get rest of file
            blocks[submission_type].append({
                'text': ''.join(lines[current:])
            })

        # TODO define colours elsewhere
        colours = [
            '255, 0, 0',
            '0, 255, 0',
            '0, 0, 255',
        ]

        job = Job.objects.get(job_id=job_id)
        # Get highlighter name
        job_language = SUPPORTED_LANGUAGES[job.language][3]

        context = {
            'submissions': submissions,
            'match_info': match_info,
            'blocks': blocks,
            'colours': colours,
            'language': job_language,
            'job': job,
            'match' : match
        }
        return render(request, self.template, context)

# @login_required
# def match(request, job_id, match_id):

#     match = Match.objects.get(match_id=match_id)#, **match_user_is(request.user))
#     submissions = {
#         'first': match.first_submission,
#         'second': match.second_submission
#     }

#     blocks = {}

#     for submission_type, submission in submissions.items():
#         file_path = SUBMISSION_UPLOAD_TEMPLATE.format(
#             job_id=job_id,
#             file_type='files',
#             file_id=submission.submission_id
#         )

#         with open(file_path) as fp:
#             lines = fp.readlines()

#         # sort line matches by submission_type's from field:
#         match.line_matches.sort(key=lambda x: x[submission_type]['from'])

#         # for line in lines:
#         blocks[submission_type] = []
#         current = 0
#         for match_id, match_lines in enumerate(match.line_matches, start=1):
#             blocks[submission_type].append({
#                 'text': ''.join(lines[current:match_lines[submission_type]['from']])
#             })
#             current = match_lines[submission_type]['to']
#             blocks[submission_type].append({
#                 'id': match_id,
#                 'text': ''.join(lines[match_lines[submission_type]['from']:current])
#             })

#         # Get rest of file
#         blocks[submission_type].append({
#             'text': ''.join(lines[current:])
#         })

#     # TODO define colours elsewhere
#     colours = [
#         '255, 0, 0',
#         '0, 255, 0',
#         '0, 0, 255',
#     ]

#     context = {
#         'blocks': blocks,
#         'colours': colours
#     }
#     return render(request, "results/match.html", context)
