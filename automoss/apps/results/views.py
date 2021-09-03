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


def match(request, job_id, match_id):

    match = Match.objects.get(match_id=match_id)

    # read files:
    line_matches = match.line_matches
    files = []
    for submission in (match.first_submission, match.second_submission):
        file_path = SUBMISSION_UPLOAD_TEMPLATE.format(
            job_id=job_id,
            file_type='files',
            file_id=submission.submission_id
        )
        with open(file_path) as fp:
            files.append(fp.readlines())

    chunks = []


    blocks = {}

    for index, x in enumerate(['first', 'second']):
        current = 0
        blocks[x] = []

        for match_id, m in enumerate(match.line_matches, start=1):
            blocks[x].append({
                'text': ''.join(files[index][current:m[x]['from']]) # exhaust previous
            })
            current = m[x]['to']
            blocks[x].append({
                'id': match_id,
                'text': ''.join(files[index][m[x]['from']:current]) # actual match
            })

        # Get rest of file
        blocks[x].append({
            'text': ''.join(files[index][current:]) 
        })

    # TODO define colours elsewhere
    colours = [
        '255, 0, 0',
        '0, 255, 0',
        '0, 0, 255',
    ]

    context = {
        'match': match,
        # 'files': files,
        'blocks' : blocks,
        'colours': colours
    }
    return render(request, "results/match.html", context)
