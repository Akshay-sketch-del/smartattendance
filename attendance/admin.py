from django.contrib import admin

from .models import (
    Department,
    Faculty,
    Student,
    Subject,
    AttendanceSession,
    Attendance,
    CorrectionRequest
)


admin.site.register(Department)
admin.site.register(Faculty)
admin.site.register(Student)
admin.site.register(Subject)
admin.site.register(AttendanceSession)
admin.site.register(Attendance)
admin.site.register(CorrectionRequest)