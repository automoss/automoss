from django.contrib import admin
from .models import Job, Submission, JobEvent

admin.site.register(Job)
admin.site.register(Submission)
admin.site.register(JobEvent)
