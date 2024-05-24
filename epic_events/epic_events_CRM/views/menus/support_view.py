from datetime import datetime
from typing import Optional
from typing import List
from django.db.models.query import QuerySet
from django.utils.timezone import make_aware
from django.utils.timezone import get_default_timezone
from dateutil.parser import parse
import click
from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich import box
from rich.box import ROUNDED
from colorama import Fore
from colorama import Style
from crm.models import Collaborator
from crm.models import Client
from crm.models import  Evenement
from views.crm_base_view import BaseView

class SupportView(BaseView):


    def __init__(self):
        super().__init__()


    MENU_OPTIONS = [
        "1 - View the list of all clients.",
        "2 - View the list of all contracts.",
        "3 - View the list of all events.",
        "4 - View your assigned events.",
        "5 - Modify one of your assigned events.",
        "6 - Exit of CRM system."
    ]
    MENU_LIMIT = len(MENU_OPTIONS)

    def show_main_menu(self, collaborator: Collaborator) -> None:
        self.clear_screen()
        console = Console()

        name_to_display = collaborator.get_full_name() or collaborator.username

        table = Table(show_header=True,
                    header_style="bold magenta")

        table.add_column("Menu Options",
                        justify="left",
                        style="dim")

        for option in self.MENU_OPTIONS:
            table.add_row(option)

        self.display_info_message(f"Welcome {name_to_display}.")
        self.display_info_message(f"What operation wold you like to perform?\n")

        console.print(table)

    def get_user_menu_choice(self) -> int:
        choice = self.get_collaborator_choice(limit=self.MENU_LIMIT)

        return choice
