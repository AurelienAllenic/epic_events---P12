import re
import click
from views.crm_base_view import BaseView
from rich.console import Console
from rich.table import Table
from colorama import Fore, Style
from django.db.models.query import QuerySet
from typing import List, TypeVar
from django.db import DatabaseError
from typing import Any, List, Optional, Union
from typing import TypeVar
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.db.models.query import QuerySet
from django.db import DatabaseError
from django.db.models import Model
from crm.models import Collaborator, Contract, Evenement, Client
from django.db.models.fields.related import ForeignKey
from django.contrib.auth import get_user_model


ModelType = TypeVar("ModelType")


class ManagementView(BaseView):


    def __init__(self):
        super().__init__()

    def get_data_for_create_object(self, object_type: str) -> dict:
        if object_type.lower() == "collaborators":
            first_name = self.get_valid_input_with_limit("First Name", 50)
            last_name = self.get_valid_input_with_limit("Last Name", 50)
            username = self.get_valid_input_with_limit("Username", 50)
            password = self.get_valid_password()
            email = self.get_valid_email()
            role = self.get_valid_role_for_collaborator()
            employee_number = self.get_valid_input_with_limit("Employee Number", 50)

            collaborator_data = {
                "first_name": first_name,
                "last_name": last_name,
                "username": username,
                "password": password,
                "email": email,
                "role_name": role,
                "employee_number": employee_number
            }

            return collaborator_data
        
        elif object_type.lower() == "contracts":
            self.display_info_message("Please provide the following information for the new contract:")

            value = self.get_valid_decimal_input("Total Amount (e.g., 9999.99)")
            due = self.get_valid_decimal_input("Amount Remaining (e.g., 9999.99)")
            status = self.get_valid_choice("Status (Options: signed, not_signed)", ["signed", "not_signed"])

            contract_data = {
                "value": value,
                "due": due,
                "status": status
            }

            return contract_data
        elif object_type.lower() == "clients":
            self.display_info_message("Please provide the following information for the new client")

            name = self.get_valid_input_with_limit("Full Name (max 100 characters)", 100)
            email = self.get_valid_email()
            phone = self.get_valid_input_with_limit("Phone number (max 20 characters)", 20)
            company_name = self.get_valid_input_with_limit("Company name (max 100 characters)", 100)

            client_data = {
                "name": name,
                "email": email,
                "phone": phone,
                "company_name": company_name
            }

            return client_data
        else:
            raise ValueError("Invalid object type. Expected 'collaborator', 'contract' or 'client'.")



    def get_valid_role_for_collaborator(self, allow_blank: bool = False) -> str:
        roles_choices = ['management', 'sales', 'support']
        role_prompt = "Role (management, sales, support)"

        while True:
            role = click.prompt(role_prompt, type=str, default="", show_default=True).strip().lower()

            if allow_blank and role == "":
                return role

            if not role:
                self.display_warning_message("Role cannot be empty.")
                continue

            if role not in roles_choices:
                self.display_error_message(f"Invalid role. Please enter a valid role: {', '.join(roles_choices)}.")
                continue

            return role


    def get_valid_password(self) -> str:
        password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$'

        password_instructions = ("Password must contain at least one uppercase letter, one lowercase letter, "
                                "one number, and be at least 8 characters long.")

        while True:
            password = click.prompt(Fore.YELLOW + "Password" + Style.RESET_ALL, hide_input = True).strip()
            if not password:
                self.display_warning_message("Password cannot be empty.")
                continue

            if not re.fullmatch(password_regex, password):
                self.display_error_message(f"Invalid password format. {password_instructions}")
                continue

            confirm_password = click.prompt(Fore.YELLOW + "Confirm password" + Style.RESET_ALL, hide_input = True)
            if password != confirm_password:
                self.display_error_message("Passwords do not match. Please try again.")
                continue

            return password


    def display_item_details(self, item: Any) -> None:
        self.clear_screen()
        console = Console()

        # Create a table to display item details
        table = Table(title="Item Detail", show_header=True, header_style="bold blue", show_lines=True)
        table.add_column("Field", style="dim", width=20)
        table.add_column("Value", width=40)

        # Add rows to the table with item details
        if isinstance(item, Collaborator):
            print('nous sommes dans le cas d"un collaborator')
            table.add_row("Item Type", "Collaborator")
            table.add_row("Collaborator ID", str(item.id))
            table.add_row("First Name", item.first_name)
            table.add_row("Last Name", item.last_name)
            table.add_row("Username", item.username)
            table.add_row("Email", item.email)
            table.add_row("Employee Number", item.employee_number)
            table.add_row("Role", item.role.name if item.role else "N/A")
        elif isinstance(item, Contract):
            print('nous sommes dans le cas d"un contrat', {item})
            table.add_row("Item Type", "Contract")
            table.add_row("Contract ID", str(item.id))
            table.add_row("Client", item.client_infos.name if item.client_infos else "No Name")
            table.add_row("Sales Contact", item.commercial_contact.get_full_name() if item.commercial_contact else "N/A")
            table.add_row("Total Amount", str(item.value))
            table.add_row("Amount Remaining", str(item.due))
            table.add_row("Status", item.status)
        else:
            print("Unsupported item type for display:", type(item))
            return

        # Print the table
        console.print(table, justify="center")


    def display_objects_for_selection(self, objects: List[Model]) -> None:
        self.clear_screen()
        console = Console()
        print('objects', objects)

        if any(isinstance(item, Collaborator) for item in objects):
            # Create table for collaborators
            table = Table(title="List of Available collaborators", show_header=True, header_style="bold magenta",
                        expand=True)

            # Determine fields of the object
            fields = objects[0]._meta.fields if objects else []

            # Add columns to the table based on the fields of the object
            for field in fields:
                table.add_column(field.name.capitalize(), style="dim", width=20)

            # Fill the table with objects data
            for obj in objects:
                row = []
                for field in fields:
                    if field.is_relation:
                        related_obj = getattr(obj, field.name)
                        if related_obj:
                            if field.name == 'commercial_contact':
                                user_model = get_user_model()
                                related_user = user_model.objects.get(id=related_obj.id)
                                row.append(related_user.get_full_name())
                            else:
                                row.append(str(related_obj))
                        else:
                            row.append("N/A")
                    else:
                        row.append(str(getattr(obj, field.name)) if getattr(obj, field.name) is not None else "N/A")
                table.add_row(*row)

            # Print the table for collaborators using Rich
            console.print(table)
        
        elif any(isinstance(item, Contract) for item in objects):
            # Create table for contracts
            table = Table(title="List of Available Contracts", show_header=True, header_style="bold magenta",
                        expand=True)
            table.add_column("Contract ID", style="dim", width=12)
            table.add_column("Client Name", width=20)
            table.add_column("Status", width=12)

            # Fill the table with contracts data
            for contract in objects:  # Utilisation des contrats passés en tant qu'objects
                self.display_info_message(f"Voici le supposé contract: {contract}")
                client_name = contract.client_infos.name if contract.client_infos else "No Name"
                status = contract.status

                table.add_row(
                    str(contract.id),
                    client_name,
                    status
                )

            # Print the table for contracts using Rich
            console.print(table)
        elif any(isinstance(item, Client) for item in objects):
            self.clear_screen()
            # Create console instance
            console = Console()

            # Create table
            table = Table(title="List of Available Clients", show_header=True, header_style="bold magenta", expand=True)
            table.add_column("ID", style="dim", width=10)
            table.add_column("Full Name", style="dim", width=20)

            # Fill the table with clients data
            for client in objects:
                client_name = client.name if client.name else "No Name"

                table.add_row(
                    str(client.id),
                    client_name
                )

            # Print the table using Rich
            console.print(table)
        elif any(isinstance(item, Evenement) for item in objects):
            # Create table for events
            table = Table(title="List of Available Events", show_header=True, header_style="bold magenta", expand=True)
            table.add_column("ID", style="dim", width=10)
            table.add_column("Name", style="dim", width=20)
            table.add_column("Client Name", style="dim", width=20)
            table.add_column("Support Contact", style="dim", width=20)

            # Fill the table with events data
            for event in objects:
                event_name = event.name if event.name else "No Name"
                client_name = event.client_name
                support_contact = event.support_contact.get_full_name() if event.support_contact else "N/A"

                table.add_row(
                    str(event.id),
                    event_name,
                    client_name,
                    support_contact
                )

            # Print the table for events using Rich
            console.print(table)
        else:
            console.print("Unsupported object type", objects)


    def get_data_for_modify_collaborator(self, full_name: str) -> dict:
        self.display_info_message(f"Modifying collaborator: {full_name}. "
                                "Leave blank any field you do not wish to modify.")

        modification_data = {}

        first_name = self.get_valid_input_with_limit("New First Name (or leave blank)", 50, allow_blank=True)
        if first_name:
            modification_data["first_name"] = first_name

        last_name = self.get_valid_input_with_limit("New Last Name (or leave blank)", 50, allow_blank=True)
        if last_name:
            modification_data["last_name"] = last_name

        email = self.get_valid_email(allow_blank=True)
        if email:
            modification_data["email"] = email

        username = self.get_valid_input_with_limit("New Username (or leave blank)", 50, allow_blank=True)
        if username:
            modification_data["username"] = username

        role = self.get_valid_role_for_collaborator(allow_blank = True)
        if role:
            modification_data["role_name"] = role

        employee_number = self.get_valid_input_with_limit("New Employee Number (or leave blank)", 50, allow_blank=True)
        if employee_number:
            modification_data["employee_number"] = employee_number

        return modification_data





    def get_data_for_modify_contract(self) -> dict:
        modification_data = {}
        self.display_info_message("Modifying contract... "
                                "Please leave blank any field you do not wish to modify")
        value = self.get_valid_decimal_input("Total Amount (e.g., 9999.99)", allow_blank=True)
        if value:
            modification_data["value"] = value

        due = self.get_valid_decimal_input("Amount Remaining (e.g., 9999.99)", allow_blank=True)
        if due:
            modification_data["due"] = due

        status = self.get_valid_choice("Status (Options: signed, not_signed)",
                                    ["signed", "not_signed"],
                                    allow_blank=True)
        if status:
            modification_data["status"] = status
        return modification_data
