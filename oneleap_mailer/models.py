from django.db import models

# Create your models here.
class EmailMessageTemplate(models.Model):
    markdown_template = models.TextField()
    text_template = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    subject = models.CharField(max_length=128)
    name = models.CharField(max_length=128)
