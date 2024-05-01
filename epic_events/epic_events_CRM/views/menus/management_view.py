import re
import click
from views.crm_base_view import BaseView
from rich.console import Console
from rich.table import Table
from colorama import Fore, Style
from django.db.models.query import QuerySet
from typing import List, TypeVar
from django.db import DatabaseError
from typing import Any, List, Optional
from typing import TypeVar
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.db.models.query import QuerySet
from django.db import DatabaseError
from django.db.models import Model
from crm.models import Collaborator


ModelType = TypeVar("ModelType")


class ManagementView(BaseView):


    def __init__(self):
        super().__init__()


    def get_data_for_create_collaborator(self) -> dict:
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


    def display_item_details(self, collaborator: Collaborator) -> None:
        self.clear_screen()
        console = Console()

        # Create a table to display collaborator details
        table = Table(title = "Collaborator Detail", show_header = True, header_style = "bold blue", show_lines = True)
        table.add_column("Field", style = "dim", width = 20)
        table.add_column("Value", width = 40)

        # Add rows to the table with collaborator details
        table.add_row("Collaborator ID", str(collaborator.id))
        table.add_row("First Name", collaborator.first_name)
        table.add_row("Last Name", collaborator.last_name)
        table.add_row("Username", collaborator.username)
        table.add_row("Email", collaborator.email)
        table.add_row("Employee Number", collaborator.employee_number)
        table.add_row("Role", collaborator.role.name if collaborator.role else "N/A")

        # Print the table
        console.print(table, justify = "center")

    def display_objects_for_selection(self, objects: List[ModelType]) -> None:
        self.clear_screen()
        for(obj) in objects:
            print(obj, 'object')
        # Create console instance
        console = Console()

        # Create table
        table = Table(show_header=True, header_style="bold magenta", expand=True)

        # Determine fields of the object
        fields = objects[0]._meta.fields if objects else []

        # Add columns to the table based on the fields of the object
        for field in fields:
            table.add_column(field.name.capitalize(), style="dim", width=20)

        # Fill the table with objects data
        for obj in objects:
            row = [str(getattr(obj, field.name)) if getattr(obj, field.name) is not None else "N/A" for field in fields]
            table.add_row(*row)

        # Print the table using Rich
        console.print(table)

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

    def get_data_for_create_contract(self) -> dict:
        self.display_info_message("Please provide the following information for the new contract:")

        value = self.get_valid_decimal_input("Total Amount (e.g., 9999.99)")
        due = self.get_valid_decimal_input("Amount Remaining (e.g., 9999.99)")
        status = self.get_valid_choice("Status (Options: signed, not_signet)", ["signed", "not_signed"])

        contract_data = {
            "value": value,
            "due": due,
            "status": status
        }

        return contract_data

    def get_data_for_modify_contract(self) -> dict:
        modification_data = {}
        self.display_info_message("Modifying contract... "
                                "Please leave blank any field you do not wish to modify")
        total_amount = self.get_valid_decimal_input("Total Amount (e.g., 9999.99)", allow_blank=True)
        if total_amount:
            modification_data["total_amount"] = total_amount

        amount_remaining = self.get_valid_decimal_input("Amount Remaining (e.g., 9999.99)", allow_blank=True)
        if amount_remaining:
            modification_data["amount_remaining"] = amount_remaining

        status = self.get_valid_choice("Status (Options: signed, not_signed)",
                                    ["signed", "not_signed"],
                                    allow_blank=True)
        if status:
            modification_data["status"] = status

        return modification_data
