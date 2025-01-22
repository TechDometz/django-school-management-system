from django.contrib import admin

from .models import *

admin.site.register(Department)
admin.site.register(Subject)
admin.site.register(GradeLevel)
admin.site.register(ClassLevel)
admin.site.register(ClassYear)
admin.site.register(Stream)
admin.site.register(ClassRoom)
admin.site.register(AllocatedSubject)
admin.site.register(StudentClass)
admin.site.register(Topic)
admin.site.register(SubTopic)
admin.site.register(Dormitory)
admin.site.register(DormitoryAllocation)
admin.site.register(MessageToParent)
admin.site.register(MessageToTeacher)
admin.site.register(Teacher)
