from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


# Create your models here.

class ActivityLog(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    # Generic relation
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"{self.timestamp} - {self.action}"


class survey(models.Model):

    cluster_name = models.CharField(max_length=200, blank=True)
    work_order = models.CharField(max_length=16)
    region = models.CharField(max_length=20, blank=True)
    project_type = models.CharField(max_length=20, blank=True)
    RITM = models.CharField(max_length=11)
    target_area = models.IntegerField(blank=True, null=True)
    date_assigned = models.DateField()
    status = models.CharField(max_length=50)
    responsible = models.CharField(max_length=100)
    tools = models.CharField(max_length=50)
    wo_status = models.CharField(max_length=50)
    priority = models.CharField(max_length=20)
    remarks = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return (f"{self.cluster_name} {self.work_order} {self.region} {self.project_type} {self.RITM} {self.target_area} {self.wo_status}")


class design(models.Model):

    district_name = models.CharField(max_length=200, blank=True)
    cluster_name = models.CharField(max_length=200, blank=True)
    work_order = models.CharField(max_length=16)
    scope_work = models.CharField(max_length=100, blank=True)
    subclass = models.CharField(max_length=50)
    project_type = models.CharField(max_length=20)
    year = models.IntegerField()
    RITM = models.CharField(max_length=11)
    region = models.CharField(max_length=20)
    target_area = models.IntegerField(blank=True)
    date_assigned = models.DateField()
    design_type = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=50, blank=True)
    tools = models.CharField(max_length=50)
    wo_status = models.CharField(max_length=50)
    responsible = models.CharField(max_length=100)
    priority = models.CharField(max_length=20)
    remarks = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return (f"{self.cluster_name} {self.work_order} {self.region} {self.project_type} {self.RITM} {self.target_area} {self.wo_status}")
