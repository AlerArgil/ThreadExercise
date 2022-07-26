import os
import tempfile
from time import sleep

from django.core.files.storage import default_storage
from django.test import TestCase, TransactionTestCase


class CSVParseSerializersTests(TestCase):

    def test_not_valid_without_file(self):
        """
        if name of file doesnt exists, then validation exception
        """
        from files.serializers import ParseCSVSerializer
        data = dict(name='wrongName')
        serializer = ParseCSVSerializer(data=data)
        self.assertFalse(serializer.is_valid(raise_exception=False))

    def test_error_valid_serialization_without_file(self):
        """
        Trying validation without name, then validation exception
        """
        from files.serializers import ParseCSVSerializer
        serializer = ParseCSVSerializer(data=[])
        self.assertFalse(serializer.is_valid(raise_exception=False))


    def test_error_status_choices(self):
        """
        Trying validation with wrong status
        """
        from django.conf import settings
        from files.serializers import ParseCSVSerializer
        temp_file = tempfile.NamedTemporaryFile(dir=settings.MEDIA_ROOT)
        data = dict(name=temp_file.name.split('/').pop(), status='WrongStatus')
        serializer = ParseCSVSerializer(data=data)
        self.assertFalse(serializer.is_valid(raise_exception=False))

    def test_valid_serialization_data_file(self):
        """
        if name of file doesnt exists, then validation exception
        """
        from django.conf import settings
        from files.serializers import ParseCSVSerializer
        temp_file = tempfile.NamedTemporaryFile(dir=settings.MEDIA_ROOT)
        data = dict(name=temp_file.name.split('/').pop())
        serializer = ParseCSVSerializer(data=data)
        valid = serializer.is_valid(raise_exception=True)
        self.assertTrue(valid)


class FileParsingTests(TransactionTestCase):
    def pre_create_csv(self, filename):
        from files.models import CSV
        file = CSV()
        file.name = filename
        file.save()
        sleep(1)
        return file

    def test_empty_file_parsing(self):
        """
        if name of file doesnt exists, then validation exception
        """
        from django.conf import settings
        temp_file = tempfile.NamedTemporaryFile(dir=settings.MEDIA_ROOT)
        file = self.pre_create_csv(temp_file.name.split('/').pop())
        self.assertEqual(file.status, 'failed')

    def test_success_file_parsing_with_success_task(self):
        """
        if format file right, then all success
        """
        from django.conf import settings
        temp_file = tempfile.NamedTemporaryFile(dir=settings.MEDIA_ROOT)
        with temp_file as tf:
            tf.writelines([b'"n1","n2","n3"\n', b'"1","2","3"\n', b'"4","5","6"\n', b'"7","8","9"\n'])
            os.link(tf.name, tf.name+'.csv')
        file = self.pre_create_csv(temp_file.name.split('/').pop()+'.csv')
        default_storage.delete(tf.name+'.csv')
        self.assertEqual(file.status, 'success')
        self.assertEqual(file.tasks.filter(status='success').count(), 1)
        self.assertEqual(file.tasks.filter(status='success').first().column_name, "n2")

    def test_success_file_parsing_with_all_failed_task(self):
        """
        if format file wrong, then file success task failed
        """
        from django.conf import settings
        from files.models import CSV
        temp_file = tempfile.NamedTemporaryFile(dir=settings.MEDIA_ROOT)
        with temp_file as tf:
            tf.writelines([b'"n1","n2","n3"\n', b'"1","WRONG2","3"\n', b'"4","5","6"\n', b'"7","8","9"\n'])
            os.link(tf.name, tf.name+'.csv')
        file = self.pre_create_csv(temp_file.name.split('/').pop()+'.csv')
        default_storage.delete(tf.name+'.csv')
        self.assertEqual(file.status, 'success')
        self.assertEqual(file.tasks.filter(status='failed').count(), 1)
        self.assertEqual(file.tasks.filter(status='failed').first().column_name, "n2")
