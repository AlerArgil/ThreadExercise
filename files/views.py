from rest_framework import generics

from files.models import Task
from files.serializers import ParseCSVSerializer, ActiveTasksCountSerializer, TaskSerializer


class ParseFileView(generics.CreateAPIView):
    """
    View for creating file
    """
    serializer_class = ParseCSVSerializer


class TaskCounterView(generics.RetrieveAPIView):
    """
    View for show active task count
    """
    serializer_class = ActiveTasksCountSerializer

    # def get_queryset(self):
    #     query = Task.objects.filter(status=Task.PENDING).annotate(active_tasks_count=Count('pk'))
    #     return query

    def get_object(self):
        return {'active_tasks_count': Task.objects.filter(status=Task.PENDING).count()}


class DetailTaskView(generics.RetrieveAPIView):
    """
    View for detail information about tasks
    """
    queryset = Task.objects.select_related('file').all()
    serializer_class = TaskSerializer
