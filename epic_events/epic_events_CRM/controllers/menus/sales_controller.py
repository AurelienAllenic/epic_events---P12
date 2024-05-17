from django.db import IntegrityError
from django.db import DatabaseError
from django.db.models.query import QuerySet
from django.core.exceptions import ValidationError
from typing import List
from typing import Optional
from crm.models import Collaborator
from crm.models import Client
from crm.models import Contract
from crm.models import Evenement
from services.crm_functions import CRMFunctions
from views.menus.sales_view import SalesView
from views.menus.management_view import ManagementView
from controllers.menus.management_controller import ManagementController

class SalesController:

    MAIN_MENU_OPTIONS_SALES = [
    "1 - Manipulate Clients data in the CRM system.",
    "2 - Filter Contracts.",
    "3 - Create an event for a Client.",
    "4 - View the list of all clients.",
    "5 - View the list of all contracts.",
    "6 - View the list of all events.",
    "7 - Exit the CRM."
    ]

    SUB_MENU_CLIENT_SALES = [
        "1 - Create a client.",
        "2 - Update client infos.",
        "3 - Update client contract.",
        "4 - Return to main menu."
    ]

    def __init__(self, collaborator: Collaborator,
                services_crm: CRMFunctions,
                view_cli: SalesView,
                view_management: ManagementView,
                management_controller: ManagementController
                ):
        self.collaborator = collaborator
        self.services_crm = services_crm
        self.view_cli = view_cli
        self.view_management = view_management
        self.management_controller = management_controller

    def start(self):
        print("Starting the sales role...")
        name_to_display = self.collaborator.get_full_name() or collaborator.username

        self.view_cli.show_main_menu(name_to_display, self.MAIN_MENU_OPTIONS_SALES)

        user_choice = self.view_cli.get_user_menu_choice()

        match user_choice:
            case 1:
                # Create a new Client.
                
                self.view_cli.show_main_menu(name_to_display, self.SUB_MENU_CLIENT_SALES)
                user_sub_menu_choice = self.view_cli.get_user_menu_choice()
                match user_sub_menu_choice:
                    case 1:
                        self.management_controller.instance_creation("clients")
                    case 2:
                        self.management_controller.instance_modification("clients")
                    case 3:
                        self.management_controller.instance_deletion("clients")
                    case 4:
                        self.view_cli.show_main_menu(name_to_display, self.MAIN_MENU_OPTIONS_SALES)
                    case _:
                        print(
                            f"Invalid menu option selected: {user_choice}. in start() - sales controller."
                            f"Expected options were between 1 and 4",
                            level='error')
                        self.view_cli.display_error_message("Invalid option selected. Please try again.")
            case 2:
                #  Filter contracts
                print("Filtering contracts...")
                pass
            case 3:
                # Create an event for a client
                print("Creating an event for a client...")
                pass
            case 4:
                self.management_controller.show_all_management_objects("Clients")
                pass
            case 5:
                self.management_controller.show_all_management_objects("Contracts")
            case 6:
                self.management_controller.show_all_management_objects("Events")
            case 7:
                print("Exit the CRM system")
                return
            case _:
                print(
                    f"Invalid menu option selected: {user_choice}. in start() - sales controller."
                    f"Expected options were between 1 and 7",
                    level='error')
                self.view_cli.display_error_message("Invalid option selected. Please try again.")

        continue_operation = self.view_cli.ask_user_if_continue()

        if not continue_operation:
            return
        
        self.start()