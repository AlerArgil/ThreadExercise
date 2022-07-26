from rest_framework import serializers

from files.models import Task, CSV


class NativeCSVSerializer(serializers.ModelSerializer):
    """
    CSV Serializer with all default field
    """
    class Meta:
        model = CSV
        fields = ('id', 'name', 'status', 'message')


class ParseCSVSerializer(NativeCSVSerializer):
    """
    CSV Serializer using in parse function
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.context.get('request') and self.context.get('request').parser_context.get('kwargs').get('name'):
            self.initial_data['name'] = self.context.get('request').parser_context.get('kwargs').get('name')

    class Meta(NativeCSVSerializer.Meta):
        pass


class InTaskCSVSerializer(NativeCSVSerializer):
    """
    CSV Serializer to show as relation in task instance
    """
    class Meta(NativeCSVSerializer.Meta):
        def __init__(self):
            super().__init__(self)
            self.fields = list(super().fields).remove('status')


class NativeTaskSerializer(serializers.ModelSerializer):
    """
    Task Serializer with all default field
    """
    class Meta:
        model = Task
        fields = ('id', 'file', 'status', 'column_name', 'sum', 'message')


class TaskSerializer(NativeTaskSerializer):
    """
    Task Serializer for common purpose
    """
    file = InTaskCSVSerializer()


class ActiveTasksCountSerializer(serializers.Serializer):
    """
    Task Serializer for counting request
    """
    active_tasks_count = serializers.IntegerField()

    class Meta:
        fields = ('active_tasks_count',)
