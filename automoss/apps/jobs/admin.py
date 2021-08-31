from django.contrib import admin
from .models import Job, MOSSResult, Match, Submission

admin.site.register(Job)
admin.site.register(MOSSResult)
admin.site.register(Match)
admin.site.register(Submission)
