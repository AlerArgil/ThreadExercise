from concurrent.futures import ThreadPoolExecutor

import pyexcel
from django.core.files.storage import default_storage
from django.db import models

from files.validators import FileExists


class CSV(models.Model):
    """
    Objects with information about parsing file
    """
    NEW = 'new'
    FAILED = 'failed'
    SUCCESS = 'success'
    PENDING = 'pending'
    STATUS_CHOICES = [
        (NEW, 'new'),
        (FAILED, 'failed'),
        (SUCCESS, 'success'),
        (PENDING, 'pending')
    ]

    name = models.CharField(max_length=20, validators=[FileExists()])
    status = models.CharField(max_length=7, choices=STATUS_CHOICES, default=NEW)
    message = models.TextField(blank=True, null=True)

    def parsing(self):
        """
        File parsing function
        """
        self.status = self.PENDING
        self.save()
        try:
            file_content = pyexcel.get_sheet(file_name=default_storage.path(self.name), delimiter=',', quotechar='\'')
            chosen_columns = file_content.column[1::10]
            with ThreadPoolExecutor() as executor:
                executor.map(self.start_tasks, chosen_columns)
            self.status = self.SUCCESS
        except Exception as e:
            self.status = self.FAILED
            self.message = str(type(e)) + ':' + str(e)
        self.save()

    def start_tasks(self, columns):
        """
        Creating and calculation tasks
        """
        new_task = self.tasks.create()
        new_task.calculation(columns)


class Task(models.Model):
    """
    Objects with sum of column and other information
    """
    FAILED = 'failed'
    SUCCESS = 'success'
    PENDING = 'pending'

    STATUS_CHOICES = [
        (FAILED, 'failed'),
        (SUCCESS, 'success'),
    ]

    file = models.ForeignKey(CSV, related_name='tasks', on_delete=models.CASCADE)
    status = models.CharField(max_length=7, choices=STATUS_CHOICES, default=PENDING)
    column_name = models.CharField(max_length=30, blank=True, null=True)
    sum = models.FloatField(null=True)
    message = models.TextField(blank=True, null=True)

    def calculation(self, columns):
        """
        Initialize and calculate sum for column list
        """
        self.status = self.PENDING
        self.save()
        self.column_name = columns[0].replace('\"', '')
        del columns[0]
        all_sum = 0.0
        try:
            for term in columns:
                float_term = float(term.replace('\"', '')) if term.replace('\"', '') != '' else 0
                all_sum += float_term
            self.sum = all_sum
            self.status = self.SUCCESS
        except Exception as e:
            self.message = e
            self.status = self.FAILED
        self.save()
