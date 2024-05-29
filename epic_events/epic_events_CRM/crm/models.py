from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.conf import settings


class Client(models.Model):
    """
    Model for a client with a link to a commercial contact
    """
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
    """
    Model for a contract with a link to a client and a commercial_contact
    """
    STATUS_CHOICES = [

        ('signed', 'Signed'),
        ('not_signed', 'Not Signed')
    ]

    client_infos = models.ForeignKey(Client, on_delete=models.CASCADE)
    commercial_contact = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    value = models.FloatField()
    due = models.FloatField()
    creation_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    def __str__(self):
        return f"Contrat {self.id} - {self.client_infos}"

    class Meta:
        permissions = [
            ("manage_contracts_creation_modification", "Can create and modify contracts"),
        ]


class Evenement(models.Model):
    """
    Model for an event with a link to a contract, a client,
    a commercial_contact and a support_contact
    """
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length = 255, null = True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
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
    """
    Model for the roles, between management, sales, and support,
    each with a unique name and permissions
    """
    ROLES = [
        ('management', 'Management'),
        ('sales', 'Sales'),
        ('support', 'Support')
    ]

    name = models.CharField(max_length=10, choices=ROLES)

    def __str__(self):
        return self.name


class Collaborator(AbstractUser):
    """
    Model for a collaborator with a link to a role
    """
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    employee_number = models.CharField(max_length=50, unique=True)
    is_superuser = models.BooleanField(default=False)

    class Meta:
        permissions = [
            ("manage_collaborators", "Can create, update and delete collaborators")
        ]
