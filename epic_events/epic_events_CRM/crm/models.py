from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.conf import settings


class Client(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    company_name = models.CharField(max_length=100)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_update = models.DateTimeField(auto_now=True)
    commercial_contact = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class Contract(models.Model):
    client_infos = models.ForeignKey(Client, on_delete=models.CASCADE)
    commercial_contact = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    value = models.FloatField()
    due = models.FloatField()
    creation_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20)

    def __str__(self):
        return f"Contrat {self.id} - {self.client_infos}"

    class Meta:
        permissions = [
            ("manage_contracts_creation_modification", "Can create and modify contracts"),
        ]


class Evenement(models.Model):
    client_id = models.ForeignKey(Client, on_delete=models.CASCADE)
    client_name = models.CharField(max_length=100)
    client_contact = models.CharField(max_length=100)
    day_start = models.DateField()
    date_end = models.DateField()
    support_contact = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    location = models.CharField(max_length=100)
    attendees = models.PositiveIntegerField()
    notes = models.TextField()

    def __str__(self):
        return f"Evenement {self.id} - {self.client_name}"


class Role(models.Model):
    ROLES = [
        ('management', 'Management'),
        ('sales', 'Sales'),
        ('support', 'Support')
    ]

    name = models.CharField(max_length=10, choices=ROLES)

    def __str__(self):
        return self.name


class Collaborator(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    employee_number = models.CharField(max_length=50, unique=True)
    is_superuser = models.BooleanField(default=False)

    class Meta:
        permissions = [
            ("manage_collaborators", "Can create, update and delete collaborators")
        ]
