from ...settings import SUBMISSION_UPLOAD_TEMPLATE
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Match


@login_required
def index(request, job_id):
    context = {
        'matches': Match.objects.filter(moss_result__job__job_id=job_id)
    }
    return render(request, "results/index.html", context)

@login_required
def match(request, job_id, match_id):

    match = Match.objects.get(match_id=match_id)
    submissions = {
        'first': match.first_submission,
        'second': match.second_submission
    }

    blocks = {}

    for submission_type, submission in submissions.items():
        file_path = SUBMISSION_UPLOAD_TEMPLATE.format(
            job_id=job_id,
            file_type='files',
            file_id=submission.submission_id
        )

        with open(file_path) as fp:
            lines = fp.readlines()

        # sort line matches by submission_type's from field:
        match.line_matches.sort(key=lambda x: x[submission_type]['from'])

        # for line in lines:
        blocks[submission_type] = []
        current = 0
        for match_id, match_lines in enumerate(match.line_matches, start=1):
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

    context = {
        'blocks': blocks,
        'colours': colours
    }
    return render(request, "results/match.html", context)
