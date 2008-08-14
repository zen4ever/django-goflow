from django.db import models

from django.contrib.auth.models import User

class SampleModel(models.Model):
    date = models.DateField(auto_now_add=True)
    text = models.CharField(max_length = 100)
    number = models.IntegerField(null=True, blank=True)
    requester = models.ForeignKey(User, verbose_name='requester')
    
    def __unicode__(self):
        return self.text
