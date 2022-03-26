from rest_framework import serializers
from session.models import Session, Session_Student


class SessionStudentSerializers(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField(
        method_name='set_student_name')

    def set_student_name(self, session_student: Session_Student):
        student_name = str(session_student.student_id)
        return student_name

    class Meta:
        model = Session_Student
        fields = ['id', 'session_id', 'student_id',
                  'student_name', 'create_date']


class SessionSerializers(serializers.ModelSerializer):
    teacher_id = serializers.SerializerMethodField(
        method_name='set_teacher_name')
    course_id = serializers.SerializerMethodField(
        method_name='set_course_name')
    sessions = SessionStudentSerializers(
        many=True)
    count_student = serializers.SerializerMethodField(
        method_name='count_all_student')
    avg_date = serializers.SerializerMethodField(
        method_name='calculate_avg')

    def set_course_name(self, session: Session):
        course_name = str(session.course_id)
        return course_name

    def set_teacher_name(self, session: Session):
        teacher_name = str(session.teacher_id)
        return teacher_name

    def count_all_student(self, sessions: Session):
        all_sessions = sessions.sessions.count()
        return all_sessions

    def calculate_avg(self, sessions: Session):
        all_sessions = sessions.sessions.all()
        c_student = sessions.sessions.count()
        avg_date = 0
        for session in all_sessions:
            birth_date = session.student_id.bdate
            if birth_date is not None:
                bdate = birth_date
                bdate = bdate.year
                avg_date += int(bdate)
        if c_student != 0:
            avg_date = int(avg_date / c_student)
        return avg_date

    class Meta:
        model = Session
        fields = ['session_id', 'session_number', 'course_id', 'level_id',
                  'position_id', 'time_id', 'teacher_id', 'create_date', 'sessions', 'count_student', 'avg_date']
