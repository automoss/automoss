from django.shortcuts import render, get_object_or_404
from .models import MOSSReport, GeneratedReport

def index(request, job_id):
    """ Renders view of MOSS Job Report"""
    report = MOSSReport.objects.get(job__job_id=job_id)
    context = {"report": report}
    return render(request, 'reports/index.html', context)

def report(request, job_id, report_id):
    """ Renders view of user-generated Report"""
    context = {"report": GeneratedReport.objects.get(report_id=report_id)}
    return render(request, 'reports/report.html', context)
