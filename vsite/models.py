from django.apps import AppConfig
from django.db import models
import datetime
from django.utils import timezone

class MyappConfig(AppConfig):
    name = 'vsite'

    def ready(self):
        # Avoid executing database queries in AppConfig.ready()
        my_model_count = models.MyModel.objects.count()


class GeneratedCode(models.Model):
    code = models.CharField(max_length=9, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        # Check if the code is still valid (within 4 hours)
        return self.created_at + datetime.timedelta(hours=4) > timezone.now()
    
class VideoContent(models.Model):
    CHAPTER_CHOICES = (
        (1, 'Formulating the title'),
        (2, 'Crafting research questions'),
        (3, 'Creating introduction'),
        (4, 'Finding related literature'),
        (5, 'Presenting, analyzing, and interpreting data'),
        (6,'Formulating conclusions and recommendations'),
    )

    title = models.CharField(max_length=100)
    chapter = models.IntegerField(choices=CHAPTER_CHOICES)
    video = models.FileField(upload_to='videos/')
    short_details = models.TextField()

    def __str__(self):
        return self.title