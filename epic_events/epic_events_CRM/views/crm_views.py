import click
from colorama import Fore
from views.crm_base_view import BaseView


class CRMView(BaseView):
    @staticmethod
    def prompt_login():
        """
        Prompt the user to log in with their username and password.

        This method clears the screen and displays a welcome message.
        It then prompts the user to enter their username and password,
        hiding the input for the password for security purposes.

        Returns:
            dict: A dictionary containing the entered username and password.
        """
        click.clear()
        click.secho("Welcome to Epic Events CRM!", fg="blue", bold=True)
        click.secho("Please log in...", fg="blue", bold=True)
        username = click.prompt(Fore.YELLOW + "Username: ")
        password = click.prompt(Fore.YELLOW + "Password: ", hide_input=True)

        return {
            "username": username,
            "password": password
        }

    @staticmethod
    def get_collaborator_choice(limit) -> int:
        """
        Prompt the user to choose an option within a specified limit.

        This method prompts the user to choose an option by entering a number.
        It ensures that the chosen option is within the range from 1 to the provided limit.

        Args:
            limit (int): The upper limit of the options.

        Returns:
            int: The chosen option.

        """
        while True:
            choice = click.prompt("Please choose an option", type=int)
            if 1 <= choice <= limit:
                return choice
            else:
                click.secho("Invalid option. Please try again.", fg="red")
