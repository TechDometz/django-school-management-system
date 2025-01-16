from django.contrib import admin

from .models import *

admin.site.register(Assignment)
admin.site.register(GradedAssignment)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(SpecificExplanations)
admin.site.register(Concept)
admin.site.register(Note)
