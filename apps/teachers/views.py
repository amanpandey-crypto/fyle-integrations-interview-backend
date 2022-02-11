from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.students.models import Assignment, Student

from .models import Teacher
from .serializers import TeacherAssignmentSerializer


class ListAssignments(APIView):
    serializer_class = TeacherAssignmentSerializer

    def get(self, request, *args, **kwargs):
        assignments = Assignment.objects.filter(teacher__user=request.user).exclude(
            student__user=request.user
        )

        print(assignments)
        return Response(
            data=self.serializer_class(assignments, many=True).data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request, *args, **kwargs):
        teacher = Teacher.objects.get(user=request.user)
        request.data["teacher"] = teacher.id

        if "student_id" in request.data:
            student = Student.objects.get(pk=request.data["student_id"])
            request.data["student"] = student.id

        try:
            assignment = Assignment.objects.get(pk=request.data["id"])
        except Assignment.DoesNotExist:
            return Response(
                data={"error": "Assignment does not exist/permission denied"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        request.data["state"] = assignment.state

        serializer = self.serializer_class(assignment, data=request.data, partial=True)

        if serializer.is_valid():
            if assignment.teacher.id != teacher.id:
                return Response(data={'non_field_errors':['Teacher cannot grade for other teacher''s assignment']}, status=status.HTTP_400_BAD_REQUEST)
            print(serializer.validated_data)
            serializer.validated_data['state'] = "GRADED"
            serializer.save()
            print(serializer.data)
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)