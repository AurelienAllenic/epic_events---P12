import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epic_events_CRM.settings")

django.setup()

from django.contrib.auth.models import Group, Permission
from django.contrib.auth.hashers import make_password
from crm.models import Collaborator, Client, Role, Contract, Evenement
from datetime import date

# Réinitialiser la base de données avant de relancer la création des gourpes et users
django.db.connections['default'].cursor().execute('SET FOREIGN_KEY_CHECKS=0')
Collaborator.objects.all().delete()
Client.objects.all().delete()
Group.objects.all().delete()
django.db.connections['default'].cursor().execute('SET FOREIGN_KEY_CHECKS=1')


# Create groups
group_names = ['management_team', 'sales_team', 'support_team']
groups = {}
for group_name in group_names:
    group, created = Group.objects.get_or_create(name=group_name)
    if created:
        print(f"Group '{group_name}' created .")
    else:
        print(f"Group '{group_name}' already exists.")
    groups[group_name] = group

# Assign permissions to each group
permissions = {
    'management_team': ['view_client', 'manage_collaborators', 'manage_contracts_creation_modification',
                        'view_contract', 'view_event'],
    'sales_team': ['add_client', 'view_client', 'view_contract', 'view_event'],
    'support_team': ['view_client', 'view_contract', 'view_event'],
}

for group_name, perm_codenames in permissions.items():
    print('for ici')
    group = groups[group_name]
    print(f'for ici pour le group {group}')
    for codename in perm_codenames:
        perm, created = Permission.objects.get_or_create(codename=codename)
        group.permissions.add(perm)
    print(f"Permissions successfully assigned to the group '{group_name}'.")
    # Function to create a collaborator and add to a group
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


# Create users for each role and add them to respective groups
create_collaborator("Aurelien", "Allenic", "aurelien", "aurelien.allenic@gmail.com",
                    "management", "9473", "managementPassword9473",
                    "management_team")
create_collaborator("Boris", "Johnson", "borisSales", "alex.sales@example.net",
                    "sales", "9474", "SalesPassword9474", "sales_team")
create_collaborator("Emma", "Stone", "emmaStone", "emma.stone@example.net",
                    "support", "9475", "SupportPassword9475",
                    "support_team")

# Function to find sales contact by username
def find_sales_contact(username):
    try:
        return Collaborator.objects.get(username=username)
    except Collaborator.DoesNotExist:
        print(f"No sales contact found with : {username}")
        return None


# Function to create a client
def create_client(name, email, phone, company_name, commercial_contact):
    sales_contact = find_sales_contact(commercial_contact)
    if sales_contact is None:
        return

    client = Client(
        name= name,
        email=email,
        phone=phone,
        company_name=company_name,
        commercial_contact=sales_contact
    )
    client.save()
    print(f"Client '{name}' created.")


# Create clients and assign their sales contact
clients_data = [
    {"name": "first client", "email": "first.client@client.com", "phone": "0625324428", "company_name": "first company",
     "commercial_contact": "aurelien"},
    {"name": "second client", "email": "second.client@client.com", "phone": "0398562412", "company_name": "second company",
     "commercial_contact": "aurelien"},
    {"name": "third client", "email": "third.client@client.com", "phone": "0451289563",
     "company_name": "third company", "commercial_contact": "aurelien"}
]

for client_data in clients_data:
    create_client(**client_data)

def create_event(name, client_name, client_contact, day_start, date_end, support_contact_username, location, attendees, notes):
    # Recherche du client par nom
    try:
        client = Client.objects.get(name=client_name)
    except Client.DoesNotExist:
        print(f"Client '{client_name}' not found.")
        return
    
    # Recherche du contact de support par nom d'utilisateur
    try:
        support_contact = Collaborator.objects.get(username=support_contact_username)
    except Collaborator.DoesNotExist:
        print(f"Support contact '{support_contact_username}' not found.")
        return

    # Création de l'événement
    event = Evenement.objects.create(
        name=name,
        client_id=client,
        client_name=client_name,
        client_contact=client_contact,
        day_start=day_start,
        date_end=date_end,
        support_contact=support_contact,
        location=location,
        attendees=attendees,
        notes=notes
    )
    print(f"Event '{event}' created successfully.")
    return event

create_event("first event", "first client", "John Doe", date(2024, 5, 10), date(2024, 5, 11), "emmaStone", "Paris", 50, "Meeting with client")