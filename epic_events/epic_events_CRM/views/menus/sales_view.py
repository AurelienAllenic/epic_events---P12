from rich.console import Console
from rich.table import Table
from views.crm_base_view import BaseView
from typing import List
import click
from django.utils.timezone import make_aware
from django.utils.timezone import get_default_timezone
from dateutil.parser import parse
from datetime import datetime
from crm.models import Contract

class SalesView(BaseView):

    def show_main_menu(self, collaborator_name: str, menu_options: List[str]):
        self.clear_screen()
        console = Console()

        table = Table(show_header=True,
                    header_style="bold magenta")

        table.add_column("Menu Options",
                        justify="left",
                        style="dim")

        for option in menu_options:
            table.add_row(option)

        self.display_info_message(f"Welcome {collaborator_name}.")
        self.display_info_message(f"What operation wold you like to perform?\n")

        console.print(table)

    def get_user_menu_choice(self) -> int:
        choice = self.get_collaborator_choice(limit=7)

        return choice


    def get_valid_start_date(self) -> datetime:

        while True:
            start_date_str = click.prompt("Start date (YYYY-MM-DD HH:MM)", default="", show_default=False)
            try:

                naive_start_date = parse(start_date_str)
            except ValueError:

                self.display_error_message("Invalid date format. Please use YYYY-MM-DD HH:MM.")
                continue

            if naive_start_date < datetime.now():
                self.display_error_message("Start date must be in the future. Please try again.")
                continue

            return make_aware(naive_start_date, get_default_timezone())

    def get_valid_end_date(self, start_date: datetime) -> datetime:
        while True:
            end_date_str = click.prompt("End date (YYYY-MM-DD HH:MM)", default="", show_default=False)
            try:

                naive_end_date = parse(end_date_str)
                aware_end_date = make_aware(naive_end_date, get_default_timezone())
            except ValueError:

                self.display_error_message("Invalid date format. Please use YYYY-MM-DD HH:MM.")
                continue
            if aware_end_date <= start_date:
                self.display_error_message("End date must be after start date. Please try again.")
                continue

            return aware_end_date


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
        table.add_row("Value", str(contract.value))
        table.add_row("Due", str(contract.due))
        table.add_row("Creation Date", contract.creation_date.strftime("%Y-%m-%d"))
        table.add_row("Status", "Signed" if contract.status == "signed" else "Not Signed")

        console.print(table, justify="center")


    def get_data_for_contract_modification(self) -> dict:
        modification_data = {}
        self.display_info_message("Modifying contract..."
                                  "Please leave blank any field you do not wish to modify")

        new_total_amount = self.get_valid_decimal_input("Total Amount (e.g. 9999.99)", allow_blank=True)
        if new_total_amount:
            modification_data["value"] = "{:.2f}".format(new_total_amount)

        new_amount_remaining = self.get_valid_decimal_input("Amount remaining (e.g. 9999.99)", allow_blank=True)
        if new_amount_remaining:
            modification_data["due"] = "{:.2f}".format(new_amount_remaining)

        new_status = self.get_valid_choice("New status (Options: signed, not_signed)",
                                           choices=["signed", "not_signed"],
                                           allow_blank=True)
        if new_status:
            modification_data["status"] = new_status

        return modification_data