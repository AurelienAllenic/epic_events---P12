from django.db import DatabaseError
from django.core.exceptions import ValidationError
from typing import List
from crm.models import Collaborator
from crm.models import Contract
from services.crm_functions import CRMFunctions
from views.menus.sales_view import SalesView
from views.menus.general_view import GeneralView
from controllers.menus.general_controller import GeneralController
from sentry_sdk import capture_exception


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
                general_controller : GeneralController,
                general_view : GeneralView
                ):
        self.collaborator = collaborator
        self.services_crm = services_crm
        self.view_cli = view_cli
        self.general_controller = general_controller
        self.general_view = general_view


    def start(self):
        """
        Start the main menu for sales role and redirect to another submenu
        or a function according to his choice
        """
        print("Starting the sales role...")
        name_to_display = self.collaborator.get_full_name() or self.collaborator.username
        self.view_cli.show_main_menu(name_to_display, self.MAIN_MENU_OPTIONS_SALES)
        user_choice = self.view_cli.get_user_menu_choice()
        match user_choice:
            case 1:
                self.view_cli.show_main_menu(name_to_display, self.SUB_MENU_CLIENT_SALES)
                user_sub_menu_choice = self.view_cli.get_user_menu_choice()
                match user_sub_menu_choice:
                    case 1:
                        # Create a client
                        self.general_controller.instance_creation("clients")
                    case 2:
                        # Update client infos
                        self.general_controller.instance_modification("clients")
                    case 3:
                        # Update client contract
                        self.general_controller.instance_modification("contracts")
                    case 4:
                        # Return to main menu
                        self.view_cli.show_main_menu(name_to_display, self.MAIN_MENU_OPTIONS_SALES)
                    case _:
                        print(
                            f"Invalid menu option selected: {user_choice}. in start() - sales controller."
                            f"Expected options were between 1 and 4",
                            level='error')
                        self.view_cli.display_error_message("Invalid option selected. Please try again.")
            case 2:
                self.filter_contracts()
            case 3:
                self.general_controller.instance_creation("events")
            case 4:
                self.general_controller.show_all_objects("Clients")
            case 5:
                self.general_controller.show_all_objects("Contracts")
            case 6:
                self.general_controller.show_all_objects("Events")
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


    def process_event_creation(self) -> None:
        """
        create an event by getting the contract assigned to it, attach the contract to the event
        and finally create the event
        """
        self.view_cli.clear_screen()
        signed_contracts = self.general_controller.get_contracts_assigned_to(self.collaborator.id, filter_type="signed")
        print('signed contracts', signed_contracts)
        if not signed_contracts:
            return

        selected_contract = self.general_controller.select_object_from(signed_contracts, "Events")
        if not selected_contract:
            return

        self.create_event_for_signed_contract(selected_contract)


    def filter_contracts(self):
        """
        Filter the contracts by getting the status
        from the user and displaying the contracts that match it
        """
        filter_types = {

            1: None,
            2: "no_fully_paid",
            3: "not_signed",
        }
        choice = self.view_cli.get_contract_filter_choices()

        self.view_cli.clear_screen()

        if choice not in filter_types:
            self.view_cli.display_error_message("Invalid choice. Please try again.")
            return

        filter_type = filter_types[choice]

        contracts_to_display = self.general_controller.get_contracts_assigned_to(self.collaborator.id, filter_type)

        if not contracts_to_display:

            print("no contracts to display")
            return

        self.view_cli.display_list(contracts_to_display, "Contracts")
