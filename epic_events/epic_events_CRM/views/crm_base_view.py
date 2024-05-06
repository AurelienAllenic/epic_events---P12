import re
from typing import List
from typing import Optional
from django.db.models.query import QuerySet
import click
from rich.box import ROUNDED
from rich.console import Console
from rich.table import Table
from rich.text import Text
from crm.models import Contract, Client, Evenement


class BaseView:

    def ask_user_if_continue(self) -> bool:
        while True:
            response = click.prompt("Do you want to perform another operation? (yes/no)", type=str).lower()
            if response == "yes":
                return True
            elif response == "no":
                return False
            else:
                self.display_error_message("Invalid response. Please enter 'yes' or 'no'.")

    def get_user_confirmation(self, question: str) -> bool:
        while True:
            response = click.prompt(f"{question} (yes/no)", type=str).lower()
            if response == "yes":
                return True
            elif response == "no":
                return False
            else:
                self.display_error_message("Invalid response. Please enter 'yes' or 'no'.")

    def get_collaborator_choice(self, limit: int) -> int:
        while True:
            choice = click.prompt("Please choose an option", type=int)
            if 1 <= choice <= limit:
                return choice
            else:
                self.display_error_message("Invalid option. Please try again.")

    def prompt_for_selection_by_id(self, ids: List[int], model_name: str) -> int:
    # Ask the user to choose an ID
        while True:
            selected_id = click.prompt(f"Please enter the ID of the {model_name} you wish to select.", type=int)
            print("Selected ID:", selected_id)
            print("Valid IDs:", ids)  # Afficher les IDs valides
            if selected_id in ids:
                return selected_id
            else:
                self.display_error_message(f"Invalid {model_name} ID. Please choose from the list.")


    @staticmethod
    def clear_screen() -> None:
        click.clear()

    @staticmethod
    def display_error_message(error_message: str) -> None:

        console = Console()
        error_text = Text(error_message, style="bold red")
        console.print(error_text)

    @staticmethod
    def display_info_message(info_message: str) -> None:
        console = Console()
        info_text = Text(info_message, style="bold green")
        console.print(info_text)

    @staticmethod
    def display_message(message: str) -> None:
        console = Console()
        message_text = Text(message, style="bold magenta")
        console.print(message_text)

    @staticmethod
    def display_warning_message(message: str) -> None:
        console = Console()
        message_text = Text(message, style="bold yellow")
        console.print(message_text)

    def display_list(self, objects: List, object_type: str) -> None:
        console = Console()
        table = Table(title=f"List of all {object_type}", show_header=True, header_style="bold magenta", expand=True)

        # Create columns based on object type
        if object_type.lower() == "events":
            table.add_column("ID", style="dim", width=10)
            table.add_column("Contract ID", style="dim", width=12)
            table.add_column("Name", style="dim", width=12)
            table.add_column("Client Name", style="dim", width=20)
            table.add_column("Support Contact", style="dim", width=20)
            table.add_column("Start Date", style="dim", width=20)
            table.add_column("End Date", style="dim", width=20)
            table.add_column("Location", style="dim", width=25)
            table.add_column("Attendees", justify="right", style="dim", width=12)
            table.add_column("Notes", style="dim", width=30)
        elif object_type.lower() == "clients":
            print('nous sommes dans le cas d"un client')
            table.add_column("Full Name", style="dim", width=20)
            table.add_column("Email", style="dim", width=20)
            table.add_column("Phone", justify="right", style="dim", width=12)
            table.add_column("Company Name", style="dim", width=20)
            table.add_column("Creation Date", style="dim", width=20)
        elif object_type.lower() == "contracts":
            table.add_column("ID", style="dim", width=10)
            table.add_column("Client Name", style="dim", width=20)
            table.add_column("Sales Contact", style="dim", width=20)
            table.add_column("Total Amount", justify="right", style="dim", width=12)
            table.add_column("Amount Remaining", justify="right", style="dim", width=15)
            table.add_column("Creation Date", style="dim", width=20)
            table.add_column("Status", style="dim", width=15)
        else:
            console.print("Unsupported object type.")
            return

        # Fill the table with objects' data
        for obj in objects:
            if object_type.lower() == "events":
                table.add_row(
                    str(obj.id),
                    str(obj.contract.id) if obj.contract else "No Contract",
                    obj.name if obj.name else "No Named",
                    obj.client_name,
                    obj.support_contact.get_full_name() if obj.support_contact else "No Contact Assigned",
                    obj.start_date.strftime("%Y-%m-%d %H:%M"),
                    obj.end_date.strftime("%Y-%m-%d %H:%M"),
                    obj.location,
                    str(obj.attendees),
                    obj.notes if obj.notes else "No Notes"
                )
            elif object_type.lower() == "clients":
                table.add_row(
                    obj.name,
                    obj.email,
                    obj.phone,
                    obj.company_name,
                    obj.creation_date.strftime("%Y-%m-%d %H:%M")
                )
            elif object_type.lower() == "contracts":
                table.add_row(
                    str(obj.id),
                    obj.client_infos.name if obj.client_infos else "No Client Assigned",
                    obj.commercial_contact.get_full_name() if obj.commercial_contact else "No Contact Assigned",
                    f"${obj.value:.2f}",
                    f"${obj.due:.2f}",
                    obj.creation_date.strftime("%Y-%m-%d %H:%M"),
                    obj.status
                )

        # Print the table using Rich
        console.print(table)

    # ==========================  Management Controller    ===============================

    def show_menu(self, collaborator_name: str, menu_options: List[str]) -> None:
        self.clear_screen()
        console = Console()

        # Create a table for the menu options.
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Menu Options", justify="left", style="dim")

        # Add menu options to the table
        for option in menu_options:
            table.add_row(option)

        self.display_info_message(f"Welcome {collaborator_name}.")
        self.display_info_message("What operation would you like to perform?\n")

        # Print table (menu options)
        console.print(table)

    def get_valid_input_with_limit(self, prompt_text: str, max_length: int, allow_blank: bool = False) -> str:

        # Loop to ensure valid input within the specified limit or allow blank input.
        while True:
            # Prompts the user for input.
            user_input = click.prompt(prompt_text, type=str, default="", show_default=False).strip()

            # Checks if the input is empty and blank inputs are allowed.
            if allow_blank and user_input == "":
                return user_input

            # Checks if the input is empty and blank inputs are not allowed.
            if not user_input:
                self.display_warning_message(f"{prompt_text} cannot be empty.")
                continue

            # Checks if the input exceeds the maximum length.
            if len(user_input) > max_length:
                self.display_warning_message(f"{prompt_text} must not exceed {max_length} characters.")
                continue

            # Returns the valid input if it's not empty or exceeds the length limit
            return user_input

    def get_valid_email(self, allow_blank: bool = False) -> str:
        email_regex = r'\b[A-Z|a-z|0-9|._%+-]+@[A-Z|a-z|0-9|.-]+\.[A-Z|a-z]{2,}\b'
        while True:
            email = click.prompt("Email", type=str, default="", show_default=False).strip()

            # Check if input is blank and allow_blank is True
            if allow_blank and email == "":
                return email

            # Check if input is empty
            if not email:
                self.display_warning_message("Email cannot be empty.")
                continue

            # Check if input matches email regex pattern
            if not re.fullmatch(email_regex, email):
                self.display_error_message(
                    "Invalid email format. Please enter a valid email address, such as example@domain.com.")
                continue
            return email

    def get_valid_decimal_input(self, prompt_text: str, allow_blank: bool = False) -> Optional[float]:
        while True:
            user_input = click.prompt(prompt_text, default="", show_default=False).strip()

            # Check if input is blank and allow_blank is True
            if allow_blank and user_input == "":
                return None

            # Check if input is empty and allow_blank is False
            if not user_input and not allow_blank:
                self.display_error_message("This field cannot be empty.")
                continue

            try:
                # Convert input to float and check if it's positive
                value = float(user_input)
                if value < 0:
                    self.display_error_message("Please enter a positive decimal number (e.g. 9999.99)")
                    continue
                return value
            except ValueError:
                # Handle non-numeric input
                self.display_error_message("Please enter a positive decimal number (e.g. 9999.99)")
                continue

    def get_valid_choice(self, prompt_text: str,
                         choices: List[str],
                         allow_blank: bool = False) -> Optional[str]:
        while True:
            choice = click.prompt(prompt_text, default="", show_default=False).strip().lower()

            # Check if input is blank and allow_blank is True
            if allow_blank and choice == "":
                return None

            # Check if input is empty
            if not allow_blank and choice == "":
                self.display_error_message("Status cannot be empty.")
                continue

            # Check if input is in the list of valid choices
            if choice not in choices:
                self.display_error_message(f"Invalid choice. Please choose from ({', '.join(choices)}).")
                continue

            return choice

    # ==========================  Sales Controller    ===============================

    def display_contract_details(self, contract: Contract) -> None:

        console = Console()
        self.clear_screen()

        # Create a table to display contract details
        table = Table(title="Contract Detail",
                    show_header=True,
                    header_style="bold blue",
                    show_lines=True)

        table.add_column("Field", style="dim", width=20)
        table.add_column("Value", width=40)

        # Add rows to the table with contract details
        table.add_row("Contract ID", str(contract.id))
        table.add_row("Client Information", contract.client_infos.name + " - " + contract.client_infos.email)
        table.add_row("Commercial Contact", contract.commercial_contact.get_full_name() if contract.commercial_contact else "N/A")
        table.add_row("Total Amount", str(contract.value))
        table.add_row("Amount Remaining", str(contract.due))
        table.add_row("Creation Date", contract.creation_date.strftime("%Y-%m-%d"))
        table.add_row("Status", "Signed" if contract.status == "signed" else "Not Signed")

        console.print(table, justify="center")

    def display_clients_for_selection(self, clients: List[Client]) -> None:

        self.clear_screen()
        # Create console instance
        console = Console()

        # Create table
        table = Table(title="List of Available Clients", show_header=True, header_style="bold magenta", expand=True)
        table.add_column("ID", style="dim", width=10)
        table.add_column("Full Name", style="dim", width=20)

        # Fill the table with clients data
        for client in clients:
            client_name = client.name if client.name else "No Name"

            table.add_row(
                str(client.id),
                client_name
            )

        # Print the table using Rich
        console.print(table)

    def display_client_details(self, client: Client) -> None:
        self.clear_screen()
        console = Console()

        # Create a table to display client details
        table = Table(title="Client Detail", show_header=True, header_style="bold blue", show_lines=True)
        table.add_column("Field", style="dim", width=20)
        table.add_column("Value", width=40)

        # Add rows to the table with client details
        table.add_row("Client ID", str(client.id))
        table.add_row("name", client.name)
        table.add_row("Email", client.email)
        table.add_row("Phone", client.phone)
        table.add_row("Company Name", client.company_name)
        table.add_row("Commercial Contact", client.commercial_contact.get_full_name() if client.commercial_contact else "N/A")

        # Print the table
        console.print(table, justify="center")

    def display_contracts_for_selection(self, contracts: List[Contract]) -> None:
        self.clear_screen()
        # Create console instance
        console = Console()

        # Create table
        table = Table(title="List of Available Contracts", show_header=True, header_style="bold magenta",
                      expand=True)
        table.add_column("Contract ID", style="dim", width=12)
        table.add_column("Client Name", width=20)
        table.add_column("Status", width=12)

        # Fill the table with contracts data
        for contract in contracts:
            client_name = contract.client.full_name if contract.client.full_name else "No Name"
            status = contract.get_status_display()

            table.add_row(
                str(contract.id),
                client_name,
                status
            )

        # Print the table using Rich
        console.print(table)

    # ==========================  Support Controller    ===============================

    @staticmethod
    def display_events_for_selection(events: List[Evenement]) -> None:

        console = Console()

        # Create table
        table = Table(title="List of Available Events", show_header=True, header_style="bold magenta", expand=True)
        table.add_column("ID", style="dim", width=10)
        table.add_column("Name", style="dim", width=20)
        table.add_column("Client Name", style="dim", width=20)
        table.add_column("Support Contact", style="dim", width=20)

        for event in events:
            event_name = event.name if event.name else "No Name"
            client_name = event.client_name
            support_contact = event.support_contact.get_full_name() if event.support_contact else "N/A"

            table.add_row(
                str(event.id),
                event_name,
                client_name,
                support_contact
            )

        console.print(table)

    @staticmethod
    def display_event_details(event: Evenement) -> None:
        console = Console()
        table = Table(title="Event Detail", show_header=True, header_style="bold blue", show_lines=True)
        table.add_column("Field", style="dim", width=20)
        table.add_column("Value", width=40)

        table.add_row("Event ID", str(event.id))
        table.add_row("Name", event.name)
        table.add_row("Client Name", event.client_name)
        table.add_row("Client Contact", event.client_contact or "N/A")
        table.add_row("Start Date", event.day_start.strftime("%Y-%m-%d %H:%M"))
        table.add_row("End Date", event.date_end.strftime("%Y-%m-%d %H:%M"))
        table.add_row("Location", event.location)
        table.add_row("Attendees", str(event.attendees))
        table.add_row("Support Contact", event.support_contact.get_full_name() if event.support_contact else "N/A")
        table.add_row("Notes", event.notes or "N/A")

        console.print(table, justify="center")
