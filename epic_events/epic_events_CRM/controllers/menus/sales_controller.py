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
from views.menus.general_view import GeneralView
from controllers.menus.management_controller import ManagementController
from controllers.menus.general_controller import GeneralController

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
        print("Starting the sales role...")
        name_to_display = self.collaborator.get_full_name() or collaborator.username

        self.view_cli.show_main_menu(name_to_display, self.MAIN_MENU_OPTIONS_SALES)

        user_choice = self.view_cli.get_user_menu_choice()

        match user_choice:
            case 1:
                self.view_cli.show_main_menu(name_to_display, self.SUB_MENU_CLIENT_SALES)
                user_sub_menu_choice = self.view_cli.get_user_menu_choice()
                match user_sub_menu_choice:
                    case 1:
                        self.general_controller.instance_creation("clients")
                    case 2:
                        self.general_controller.instance_modification("clients")
                    case 3:
                        self.process_contract_modification()
                    case 4:
                        self.view_cli.show_main_menu(name_to_display, self.MAIN_MENU_OPTIONS_SALES)
                    case _:
                        print(
                            f"Invalid menu option selected: {user_choice}. in start() - sales controller."
                            f"Expected options were between 1 and 4",
                            level='error')
                        self.view_cli.display_error_message("Invalid option selected. Please try again.")
            case 2:
                self.filter_contracts()
                pass
            case 3:
                self.process_event_creation()
                pass
            case 4:
                self.general_controller.show_all_objects("Clients")
                pass
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


    def process_contract_modification(self) -> None:
            print('nous sommes dans process contract modification')
            contracts = self.get_contracts_assigned_to(self.collaborator.id)
            print('the contracts are', contracts)
            if not contracts:
                return

            selected_contract = self.general_controller.select_object_from(contracts)
            if not selected_contract:
                return

            self.services_crm.modify_contract(selected_contract)


    def get_contracts_assigned_to(self, collaborator_id: int, filter_type: str = None) -> List[Contract]:
        try:
            print('nous sommes dans le try de get contract assigned to', collaborator_id, filter_type)
            contracts = self.services_crm.get_filtered_contracts_for_collaborator(collaborator_id, filter_type)
        except ValueError as e:
            self.view_cli.display_error_message(str(e))
            return []
        except DatabaseError:
            self.view_cli.display_error_message("I encountered a problem with the database. Please try again later.")
            return []
        except Exception as e:
            self.view_cli.display_error_message(str(e))
            return []

        if not contracts:
            self.view_cli.display_info_message("There are no contracts to display")

        return contracts


    def process_event_creation(self) -> None:
        self.view_cli.clear_screen()

        signed_contracts = self.get_contracts_assigned_to(self.collaborator.id, filter_type="signed")
        print('signed contracts', signed_contracts)
        if not signed_contracts:
            return

        selected_contract = self.general_controller.select_object_from(signed_contracts, "Events")
        if not selected_contract:
            return

        self.create_event_for_signed_contract(selected_contract)


    def create_event_for_signed_contract(self, signed_contract: Contract) -> None:
        self.view_cli.clear_screen()

        self.view_cli.display_object_details(signed_contract)
        event_data = self.view_cli.get_data_for_add_new_event()

        event_data["contract"] = signed_contract

        try:
            print('event data', event_data)
            new_event = self.services_crm.create_event(**event_data)
            print('new event', new_event)
            self.view_cli.display_object_details(new_event)
            self.view_cli.display_info_message("Event created successfully.")
        except ValidationError as e:
            self.view_cli.display_error_message(f"Validation error: {e}")
        except DatabaseError:
            self.view_cli.display_error_message("I encountered a problem with the database. Please try again later.")
        except Exception as e:
            self.view_cli.display_error_message(str(e))


    def filter_contracts(self):

        filter_types = {
            1: None,  # get all contracts
            2: "no_fully_paid",
            3: "not_signed",
        }
        choice = self.view_cli.get_contract_filter_choices()

        self.view_cli.clear_screen()

        if choice not in filter_types:
            self.view_cli.display_error_message("Invalid choice. Please try again.")
            return

        filter_type = filter_types[choice]

        contracts_to_display = self.get_contracts_assigned_to(self.collaborator.id, filter_type)

        if not contracts_to_display:
            print("no contracts to display")
            return

        self.view_cli.display_list(contracts_to_display, "Contracts")


    def process_contract_modification(self) -> None:
        contracts = self.get_contracts_assigned_to(self.collaborator.id)
        if not contracts:
            return

        selected_contract = self.general_controller.select_object_from(contracts, "Contracts")
        if not selected_contract:
            return

        self.modify_contract(selected_contract)


    def modify_contract(self, contract: Contract) -> None:
        self.view_cli.clear_screen()

        self.view_cli.display_contract_details(contract)

        modifications = self.view_cli.get_data_for_contract_modification()

        if not modifications:
            self.view_cli.display_info_message("No modifications were made.")
            return

        try:
            contract_modified = self.services_crm.modify_contract(contract, modifications)
            self.view_cli.clear_screen()

            self.view_cli.display_contract_details(contract_modified)

            self.view_cli.display_info_message("The contract has been modified successfully.")
            return
        except ValidationError as e:
            self.view_cli.display_error_message(str(e))
        except DatabaseError:
            self.view_cli.display_error_message("I encountered a problem with the database. Please try again later.")
        except Exception as e:
            self.view_cli.display_error_message(str(e))
