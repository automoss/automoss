from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import GeneratedReport

@login_required
def index(request, job_id):
    """ Renders view of MOSS Job Report"""
    # report = request.user.mossuser.job_set.get(job_id=job_id).mossreport
    context = {} # "report": report
    return render(request, 'reports/index.html', context)

# TODO Complete generated report viewing
# @login_required
# def report(request, job_id, report_id):
#     """ Renders view of user-generated Report"""
#     context = {"report": GeneratedReport.objects.get(report_id=report_id)}
#     return render(request, 'reports/report.html', context)
