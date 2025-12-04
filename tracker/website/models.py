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


class sor(models.Model):

    sor_internal_no = models.CharField(max_length=4, blank=True)
    dwt_sor = models.CharField(max_length=10, blank=True)
    contract_no = models.CharField(max_length=10, blank=True)
    work_order = models.CharField(max_length=16, blank=True)
    tools = models.CharField(max_length=50, blank=True)
    wo_status = models.CharField(max_length=50, blank=True)
    link_code = models.CharField(max_length=300, blank=True)
    RITM = models.CharField(max_length=50, blank=True)
    subclass = models.CharField(max_length=50, blank=True)
    cost = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    sor_type = models.CharField(max_length=20, blank=True)
    sor_boq_status = models.CharField(max_length=20, blank=True)
    sor_boq_req_date = models.DateTimeField(blank=True)
    sor_boq_approved_date = models.DateTimeField(blank=True)
    sor_status = models.CharField(max_length=20, blank=True)
    rfs_boq_status = models.CharField(max_length=20, blank=True)
    rfs_boq_req_date = models.DateTimeField(blank=True)
    rfs_boq_approved_date = models.DateTimeField(blank=True)
    rfs_status = models.CharField(max_length=20, blank=True)
    oil_sheet_status = models.CharField(max_length=20, blank=True)
    oil_req_date = models.DateTimeField(blank=True)
    oil_approved_date = models.DateTimeField(blank=True)
    pac_status = models.CharField(max_length=20, blank=True)
    pac_req_date = models.DateTimeField(blank=True)
    pac_approved_date = models.DateTimeField(blank=True)
    first_50_invoice_no = models.CharField(max_length=7, blank=True)
    second_50_invoice_no = models.CharField(max_length=7, blank=True)
    sor_overall_status = models.CharField(max_length=100, blank=True)
    sor_amount = models.DecimalField(
        max_digits=15, decimal_places=2, null=True)
    dependency = models.CharField(max_length=300)
    overall_sor_total = models.DecimalField(
        max_digits=15, decimal_places=2, null=True)
    remarks = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return (f"{self.sor_internal_no} {self.link_code} {self.dwt_sor} {self.sor_type}  {self.sor_overall_status}")
