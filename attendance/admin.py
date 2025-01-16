from django.contrib import admin

from .models import *

admin.site.register(AttendanceStatus)
admin.site.register(TeachersAttendance)
admin.site.register(StudentAttendance)
admin.site.register(PeriodAttendance)
