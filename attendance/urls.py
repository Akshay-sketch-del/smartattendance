from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path(
        'student-dashboard/',
        views.student_dashboard,
        name='student_dashboard'
    ),

    path(
        'faculty-dashboard/',
        views.faculty_dashboard,
        name='faculty_dashboard'
    ),

    path(
        'mark-attendance/<int:subject_id>/',
        views.mark_attendance,
        name='mark_attendance'
    ),

    path(
        'my-attendance/',
        views.my_attendance,
        name='my_attendance'
    ),

    path(
    'subject-attendance/',
    views.subject_attendance,
    name='subject_attendance'
    ),

    path(
    'low-attendance/',
    views.low_attendance,
    name='low_attendance'
    ),

    path(
    'request-correction/',
    views.request_correction,
    name='request_correction'
    ),

    path(
    'correction-requests/',
    views.correction_requests,
    name='correction_requests'
    ),

    path(
    'review-correction/<int:request_id>/approve/',
    views.approve_correction,
    name='approve_correction'
    ),

    path(
    'review-correction/<int:request_id>/reject/',
    views.reject_correction,
    name='reject_correction'
    ),

    path(
    'attendance-history/',
    views.attendance_history,
    name='attendance_history'
    ),

    path(
    'faculty-low-attendance/',
    views.faculty_low_attendance,
    name='faculty_low_attendance'
    ),
]