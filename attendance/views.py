from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import (
    Subject,
    Student,
    AttendanceSession,
    Attendance,
    CorrectionRequest
)


def login_view(request):

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            # Admin
            if user.is_superuser:
                return redirect('/admin/')

            # Faculty
            elif hasattr(user, 'faculty'):
                return redirect('/faculty-dashboard/')

            # Student
            elif hasattr(user, 'student'):
                return redirect('/student-dashboard/')

            else:
                messages.error(request, 'User role not found.')
                logout(request)

        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('/login/')

from django.contrib.auth.decorators import login_required


@login_required
def student_dashboard(request):

    student = request.user.student

    return render(
        request,
        'student_dashboard.html',
        {
            'student': student
        }
    )

@login_required
def faculty_dashboard(request):

    faculty = request.user.faculty

    subjects = faculty.subject_set.all()

    return render(
        request,
        'faculty_dashboard.html',
        {
            'faculty': faculty,
            'subjects': subjects
        }
    )
@login_required
def mark_attendance(request, subject_id):

    faculty = request.user.faculty

    subject = get_object_or_404(
        Subject,
        id=subject_id,
        faculty=faculty
    )

    students = Student.objects.filter(
        department=subject.department,
        semester=subject.semester
    )

    if request.method == 'POST':

        date = request.POST.get('date')
        period = request.POST.get('period')

        # Create attendance session
        session, created = AttendanceSession.objects.get_or_create(
            subject=subject,
            date=date,
            period=period,
            defaults={
                'faculty': faculty
            }
        )

        # Save attendance for every student
        for student in students:

            status = request.POST.get(
                f'status_{student.id}'
            )

            Attendance.objects.update_or_create(
                session=session,
                student=student,
                defaults={
                    'status': status
                }
            )

        messages.success(
            request,
            'Attendance saved successfully!'
        )

        return redirect('faculty_dashboard')

    return render(
        request,
        'mark_attendance.html',
        {
            'subject': subject,
            'students': students
        }
    )

@login_required
def my_attendance(request):

    student = request.user.student

    attendances = Attendance.objects.filter(
        student=student
    ).select_related(
        'session',
        'session__subject'
    ).order_by(
        '-session__date'
    )

    return render(
        request,
        'my_attendance.html',
        {
            'student': student,
            'attendances': attendances
        }
    )

@login_required
def subject_attendance(request):

    student = request.user.student

    attendances = Attendance.objects.filter(
        student=student
    ).select_related(
        'session',
        'session__subject'
    )

    subjects = {}

    for attendance in attendances:

        subject = attendance.session.subject

        if subject.id not in subjects:
            subjects[subject.id] = {
                'code': subject.code,
                'name': subject.name,
                'present': 0,
                'total': 0
            }

        subjects[subject.id]['total'] += 1

        if attendance.status == 'Present':
            subjects[subject.id]['present'] += 1

    for subject in subjects.values():

        if subject['total'] > 0:
            subject['percentage'] = round(
                (subject['present'] / subject['total']) * 100,
                2
            )
        else:
            subject['percentage'] = 0

    return render(
        request,
        'subject_attendance.html',
        {
            'student': student,
            'subjects': subjects.values()
        }
    )

@login_required
def low_attendance(request):

    student = request.user.student

    attendances = Attendance.objects.filter(
        student=student
    ).select_related(
        'session',
        'session__subject'
    )

    subjects = {}

    for attendance in attendances:

        subject = attendance.session.subject

        if subject.id not in subjects:
            subjects[subject.id] = {
                'code': subject.code,
                'name': subject.name,
                'present': 0,
                'total': 0
            }

        subjects[subject.id]['total'] += 1

        if attendance.status == 'Present':
            subjects[subject.id]['present'] += 1

    low_subjects = []

    for subject in subjects.values():

        percentage = (
            subject['present'] / subject['total']
        ) * 100

        if percentage < 75:

            subject['percentage'] = round(
                percentage,
                2
            )

            low_subjects.append(subject)

    return render(
        request,
        'low_attendance.html',
        {
            'student': student,
            'subjects': low_subjects
        }
    )
@login_required
def request_correction(request):

    student = request.user.student

    attendances = Attendance.objects.filter(
        student=student
    ).select_related(
        'session',
        'session__subject'
    ).order_by(
        '-session__date'
    )

    if request.method == 'POST':

        attendance_id = request.POST.get('attendance_id')
        requested_status = request.POST.get('requested_status')
        reason = request.POST.get('reason')

        attendance = get_object_or_404(
            Attendance,
            id=attendance_id,
            student=student
        )

        CorrectionRequest.objects.create(
            attendance=attendance,
            student=student,
            requested_status=requested_status,
            reason=reason
        )

        messages.success(
            request,
            'Correction request submitted successfully!'
        )

        return redirect('request_correction')

    return render(
        request,
        'request_correction.html',
        {
            'student': student,
            'attendances': attendances
        }
    )

@login_required
def correction_requests(request):

    faculty = request.user.faculty

    correction_requests = CorrectionRequest.objects.filter(
        attendance__session__faculty=faculty,
        status='Pending'
    ).select_related(
        'student',
        'attendance',
        'attendance__session',
        'attendance__session__subject'
    ).order_by(
        '-created_at'
    )

    return render(
        request,
        'correction_requests.html',
        {
            'faculty': faculty,
            'correction_requests': correction_requests
        }
    )

@login_required
def approve_correction(request, request_id):

    faculty = request.user.faculty

    correction = get_object_or_404(
        CorrectionRequest,
        id=request_id,
        attendance__session__faculty=faculty,
        status='Pending'
    )

    correction.attendance.status = correction.requested_status
    correction.attendance.save()

    correction.status = 'Approved'
    correction.reviewed_by = faculty
    correction.save()

    messages.success(
        request,
        'Correction request approved successfully!'
    )

    return redirect('correction_requests')


@login_required
def reject_correction(request, request_id):

    faculty = request.user.faculty

    correction = get_object_or_404(
        CorrectionRequest,
        id=request_id,
        attendance__session__faculty=faculty,
        status='Pending'
    )

    correction.status = 'Rejected'
    correction.reviewed_by = faculty
    correction.save()

    messages.success(
        request,
        'Correction request rejected.'
    )

    return redirect('correction_requests')

@login_required
def attendance_history(request):

    faculty = request.user.faculty

    sessions = AttendanceSession.objects.filter(
        faculty=faculty
    ).select_related(
        'subject'
    ).order_by(
        '-date',
        '-period'
    )

    return render(
        request,
        'attendance_history.html',
        {
            'faculty': faculty,
            'sessions': sessions
        }
    )

@login_required
def faculty_low_attendance(request):

    faculty = request.user.faculty

    attendances = Attendance.objects.filter(
        session__faculty=faculty
    ).select_related(
        'student',
        'session',
        'session__subject'
    )

    students = {}

    for attendance in attendances:

        student = attendance.student
        subject = attendance.session.subject

        key = (student.id, subject.id)

        if key not in students:
            students[key] = {
                'usn': student.usn,
                'name': student.user.username,
                'subject_code': subject.code,
                'subject_name': subject.name,
                'present': 0,
                'total': 0
            }

        students[key]['total'] += 1

        if attendance.status == 'Present':
            students[key]['present'] += 1

    low_attendance = []

    for student in students.values():

        percentage = (
            student['present'] /
            student['total']
        ) * 100

        if percentage < 75:

            student['percentage'] = round(
                percentage,
                2
            )

            low_attendance.append(student)

    return render(
        request,
        'faculty_low_attendance.html',
        {
            'faculty': faculty,
            'students': low_attendance
        }
    )