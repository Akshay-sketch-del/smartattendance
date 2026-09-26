from django.db import models
from django.contrib.auth.models import User


# -----------------------------------
# DEPARTMENT
# -----------------------------------
class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


# -----------------------------------
# FACULTY
# -----------------------------------
class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=30, unique=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name()}"


# -----------------------------------
# STUDENT
# -----------------------------------
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    usn = models.CharField(max_length=30, unique=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE
    )
    semester = models.IntegerField()
    section = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.usn} - {self.user.get_full_name()}"


# -----------------------------------
# SUBJECT
# -----------------------------------
class Subject(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)

    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE
    )

    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE
    )

    semester = models.IntegerField()

    def __str__(self):
        return f"{self.code} - {self.name}"


# -----------------------------------
# ATTENDANCE SESSION
# -----------------------------------
class AttendanceSession(models.Model):
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )

    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE
    )

    date = models.DateField()
    period = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('subject', 'date', 'period')

    def __str__(self):
        return f"{self.subject.name} - {self.date} - Period {self.period}"


# -----------------------------------
# ATTENDANCE
# -----------------------------------
class Attendance(models.Model):

    STATUS_CHOICES = [
        ('Present', 'Present'),
        ('Absent', 'Absent'),
    ]

    session = models.ForeignKey(
        AttendanceSession,
        on_delete=models.CASCADE
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES
    )

    marked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('session', 'student')

    def __str__(self):
        return f"{self.student.usn} - {self.session.subject.code} - {self.status}"


# -----------------------------------
# CORRECTION REQUEST
# -----------------------------------
class CorrectionRequest(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    attendance = models.ForeignKey(
        Attendance,
        on_delete=models.CASCADE
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE
    )

    requested_status = models.CharField(
        max_length=10,
        choices=Attendance.STATUS_CHOICES
    )

    reason = models.TextField()

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    reviewed_by = models.ForeignKey(
        Faculty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.student.usn} - {self.status}"