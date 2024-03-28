from django.db import models
from django.db.models import CharField
from django.contrib.auth.models import AbstractUser

class Client(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    company_name = models.CharField(max_length=100)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    commercial_contact = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Contract(models.Model):
    id = models.AutoField(primary_key=True)
    client_infos = models.ForeignKey(Client, on_delete=models.CASCADE)
    commercial_contact = models.CharField(max_length=100)
    value = models.FloatField()
    due = models.FloatField()
    creation_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20)

    def __str__(self):
        return f"Contrat {self.id} - {self.client_infos}"

class Evenement(models.Model):
    id = models.AutoField(primary_key=True)
    client_id = models.ForeignKey(Client, on_delete=models.CASCADE)
    client_name = models.CharField(max_length=100)
    client_contact = models.CharField(max_length=100)
    day_start = models.DateField()
    date_end = models.DateField()
    support_contact = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    Attendees = models.PositiveIntegerField()
    notes = models.TextField()

    def __str__(self):
        return f"Evenement {self.id} - {self.client_name}"
    
class Collaborator(AbstractUser):

    employee_number = CharField(max_length=50, unique=True)
