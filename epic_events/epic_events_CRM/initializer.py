import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epic_events_CRM.settings")

django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.auth.hashers import make_password
from crm.models import Collaborator, Client, Role, Contract, Evenement
from datetime import date

# Réinitialiser la base de données avant de relancer la création des groupes et utilisateurs
django.db.connections['default'].cursor().execute('SET FOREIGN_KEY_CHECKS=0')
Collaborator.objects.all().delete()
Client.objects.all().delete()
Group.objects.all().delete()
Contract.objects.all().delete()
Evenement.objects.all().delete()
django.db.connections['default'].cursor().execute('SET FOREIGN_KEY_CHECKS=1')

group_names = ['management_team', 'sales_team', 'support_team']
groups = {}
for group_name in group_names:
    group, created = Group.objects.get_or_create(name=group_name)
    if created:
        print(f"Group '{group_name}' created.")
    else:
        print(f"Group '{group_name}' already exists.")
    groups[group_name] = group

permissions = {
    'management_team': ['view_client', 'manage_collaborators', 'manage_contracts_creation_modification',
                        'view_contract', 'view_event'],
    'sales_team': ['add_client', 'view_client', 'view_contract', 'view_event'],
    'support_team': ['view_client', 'view_contract', 'view_event'],
}

for group_name, perm_codenames in permissions.items():
    group = groups[group_name]
    for codename in perm_codenames:
        perm, created = Permission.objects.get_or_create(codename=codename)
        group.permissions.add(perm)
    print(f"Permissions successfully assigned to the group '{group_name}'.")


def create_collaborator(first_name, last_name, username, email, role_name, employee_number, password, group_name):
    role, created = Role.objects.get_or_create(name=role_name)
    if created:
        print(f"Role '{role_name}' created successfully.")
    else:
        print(f"The role '{role_name}' already existed.")

    collaborator = Collaborator(
        first_name=first_name,
        last_name=last_name,
        username=username,
        email=email,
        role=role,
        employee_number=employee_number,
        password=make_password(password)
    )

    collaborator.save()
    groups[group_name].user_set.add(collaborator)
    print(f"Collaborator '{first_name} {last_name}' created and added to '{group_name}'s group successfully.")


create_collaborator("Aurelien", "Allenic", "aurelien", "aurelien.allenic@gmail.com",
                    "management", "9473", "manageMdp1",
                    "management_team")
create_collaborator("Boris", "Johnson", "sales", "alex.sales@example.net",
                    "sales", "9474", "salesMdp1", "sales_team")
create_collaborator("Emma", "Stone", "support", "emma.stone@example.net",
                    "support", "9475", "supportMdp1",
                    "support_team")


def find_sales_contact(username):
    try:
        return Collaborator.objects.get(username=username)
    except Collaborator.DoesNotExist:
        print(f"No sales contact found with username: {username}")
        return None


def create_client(name, email, phone, company_name, commercial_contact):
    sales_contact = find_sales_contact(commercial_contact)
    if sales_contact is None:
        return

    client = Client(
        name=name,
        email=email,
        phone=phone,
        company_name=company_name,
        commercial_contact=sales_contact
    )
    client.save()
    print(f"Client '{name}' created.")

clients_data = [
    {"name": "first client", "email": "first.client@client.com", "phone": "0625324428", "company_name": "first company",
     "commercial_contact": "sales"},
    {"name": "second client", "email": "second.client@client.com", "phone": "0398562412", "company_name": "second company",
     "commercial_contact": "sales"},
    {"name": "third client", "email": "third.client@client.com", "phone": "0451289563",
     "company_name": "third company", "commercial_contact": "sales"}
]

for client_data in clients_data:
    create_client(**client_data)

contracts_data = [
    {"client_infos": "first client", "commercial_contact": "sales", "value": 1000, "due": 200, "status": "signed"},
    {"client_infos": "second client", "commercial_contact": "sales", "value": 1500, "due": 300, "status": "signed"}
]

contracts = {}
for data in contracts_data:
    try:
        client = Client.objects.get(name=data["client_infos"])
        commercial_contact = Collaborator.objects.get(username=data["commercial_contact"])
    except Client.DoesNotExist:
        print(f"Client '{data['client_infos']}' not found.")
        continue
    except Collaborator.DoesNotExist:
        print(f"Commercial contact '{data['commercial_contact']}' not found.")
        continue

    contract = Contract.objects.create(
        client_infos=client,
        commercial_contact=commercial_contact,
        value=data["value"],
        due=data["due"],
        status=data["status"]
    )
    contracts[data["client_infos"]] = contract
    print(f"Contract for client '{data['client_infos']}' created successfully.")


def create_event(name, client_name, client_contact, day_start, date_end, support_contact_username, location, attendees, notes, contract):
    try:
        client = Client.objects.get(name=client_name)
    except Client.DoesNotExist:
        print(f"Client '{client_name}' not found.")
        return

    try:
        support_contact = Collaborator.objects.get(username=support_contact_username)
    except Collaborator.DoesNotExist:
        print(f"Support contact '{support_contact_username}' not found.")
        return

    event = Evenement.objects.create(
        name=name,
        client=client,
        client_name=client_name,
        client_contact=client_contact,
        day_start=day_start,
        date_end=date_end,
        support_contact=support_contact,
        location=location,
        attendees=attendees,
        notes=notes,
        contract=contract
    )
    print(f"Event '{event}' created successfully.")
    return event


create_event("first event", "first client", "John Doe", date(2024, 5, 10), date(2024, 5, 11), "support", "Paris", 50, "Meeting with client", contracts["first client"])
create_event("second event", "second client", "John Doe", date(2024, 5, 10), date(2024, 5, 11), "support", "Paris", 50, "Meeting with client", contracts["second client"])
