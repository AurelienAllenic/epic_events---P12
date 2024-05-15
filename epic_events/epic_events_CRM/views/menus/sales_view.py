from rich.console import Console
from rich.table import Table
from views.crm_base_view import BaseView
from typing import List


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
