from crm.models import Collaborator, Contract, Client
from services.crm_functions import CRMFunctions
from views.menus.management_view import ManagementView
from django.core.exceptions import ValidationError
from typing import Any, List, Optional
from django.db import DatabaseError

class ManagementController:
    MAIN_MENU_OPTIONS = [
        "1 - Manipulate collaborators data in the CRM system.",
        "2 - Manipulate contract.",
        "3 - Filter events based on whether they have or don't have a support contact.",
        "4 - Assign or change the 'support' collaborator associated with an event.",
        "5 - View the list of all clients.",
        "6 - View the list of all contracts.",
        "7 - View the list of all events.",
        "8 - Exit the CRM system."
    ]

    SUB_MENU_MANAGE_COLLABORATORS = [
        "1 - Create a collaborator.",
        "2 - Update a collaborator.",
        "3 - Delete a collaborator.",
        "4 - Return to main menu"
    ]

    SUB_MENU_MANAGE_CONTRACTS = [
        "1 - Create new contract.",
        "2 - Update a contract.",
        "3 - Return to main menu"
    ]

    SUB_MENU_EVENTS = [
        "1 - View events with support contact assigned.",
        "2 - View events without support contact assigned.",
        "3 - Return to main menu"
    ]

    def __init__(self, collaborator: Collaborator,
                services_crm: CRMFunctions,
                view_cli: ManagementView):
        self.collaborator = collaborator
        self.services_crm = services_crm
        self.view_cli = view_cli


    def start(self) -> None:
        name_to_display = self.collaborator.get_full_name() or collaborator.username
        self.view_cli.show_menu(name_to_display, self.MAIN_MENU_OPTIONS)
        choice = self.view_cli.get_collaborator_choice(limit=len(self.MAIN_MENU_OPTIONS))

        match choice:
            case 1:
                self.manage_management_objects("Collaborators")
            case 2:
                self.manage_management_objects("Contracts")
            case 3:
                self.manage_management_objects("Events")
            case 4:
                pass
            case 5:
                self.show_all_management_objects("Collaborators")
            case 6:
                self.show_all_management_objects("Contracts")
            case 7:
                self.show_all_management_objects("Events")
            case 8:
                return
            case _:
                print('case')


    def show_all_management_objects(self, object_type: str) -> None:
        self.view_cli.clear_screen()

        objects = CRMFunctions.get_all_objects(object_type)

        if not objects:
            print(f"No {object_type} found.")
            return

        if object_type.lower() == "collaborators":
            self.view_cli.display_list_of_clients(objects)
        elif object_type.lower() == "contracts":
            self.view_cli.display_list_of_contracts(objects)
        elif object_type.lower() == "events":
            self.view_cli.display_list_of_events(objects)


    def manage_management_objects(self, object_type: str) -> None:
        self.view_cli.clear_screen()

        if object_type.lower() == "collaborators":
            self.view_cli.show_menu(self.collaborator.get_full_name(), self.SUB_MENU_MANAGE_COLLABORATORS)
            choice = self.view_cli.get_collaborator_choice(limit=len(self.SUB_MENU_MANAGE_COLLABORATORS))
        elif object_type.lower() == "contracts":
            self.view_cli.show_menu(self.collaborator.get_full_name(), self.SUB_MENU_MANAGE_CONTRACTS)
            choice = self.view_cli.get_collaborator_choice(limit=len(self.SUB_MENU_MANAGE_CONTRACTS))
        elif object_type.lower() == "events":
            self.view_cli.show_menu(self.collaborator.get_full_name(), self.SUB_MENU_EVENTS)
            choice = self.view_cli.get_collaborator_choice(limit=len(self.SUB_MENU_EVENTS))
        else:
            print(f"Invalid object type specified : {object_type}.")
            return

        match choice:
            case 1:
                self.instance_creation(object_type)
            case 2:
                self.instance_modification(object_type)
            case 3:
                self.instance_deletion(object_type)
            case 4:
                print(4)
                self.start()
            case _:
                print("Invalid option selected. Please try again.")
                self.view_cli.display_info_message("Invalid option selected. Please try again.")
                return


    def instance_creation(self, object_type: str) -> None:
        if object_type.lower() == "collaborators":
            while True:
                self.view_cli.clear_screen()
                self.view_cli.display_info_message("Registering new collaborator...")

                data_collaborator = self.view_cli.get_data_for_create_collaborator()
                print(data_collaborator)
                try:
                    collaborator = self.services_crm.register_collaborator(**data_collaborator)

                    self.view_cli.clear_screen()
                    self.view_cli.display_info_message("User registered successfully!")

                    break
                except Exception as e:
                    self.view_cli.display_error_message(str(e))
                    break
        elif object_type.lower() == "contracts":
            print("Contract creation not implemented yet.")
            # Implement contract creation logic here
        else:
            print("Invalid object type specified.")
            return


    def instance_modification(self, object_type: str) -> None:
        self.view_cli.clear_screen()
        our_objects = CRMFunctions.get_all_objects(object_type)

        if not our_objects:
            return

        selected_object = self.select_object_from(our_objects, object_type)

        if not selected_object:
            return

        self.modify_object(selected_object)


    def select_object_from(self, list_of_objects: List[Any], object_type: str, message: Optional[str] = None) -> Optional[Any]:
        self.view_cli.clear_screen()

        self.view_cli.display_objects_for_selection(list_of_objects)

        if message:
            self.view_cli.display_info_message(message)

        objects_ids = [obj.id for obj in list_of_objects]

        selected_object_id = self.view_cli.prompt_for_selection_by_id(objects_ids, object_type)

        selected_object = next((obj for obj in list_of_objects if obj.id == selected_object_id), None)

        if not selected_object:
            self.view_cli.display_error_message(f"We couldn't find the {object_type}. Please try again later.")

        return selected_object


    def modify_object(self, selected_item: Any) -> None:
        if isinstance(selected_item, Client):
            print("Client modification not implemented yet.")
        elif isinstance(selected_item, Contract):
            print("Contract modification not implemented yet.")
        elif isinstance(selected_item, Collaborator):
            print("Colaborator modification.", {selected_item})
            while True:
                self.view_cli.display_item_details(selected_item)
                collaborator_data = self.view_cli.get_data_for_modify_collaborator(selected_item.get_full_name())

                if not collaborator_data:
                    self.view_cli.display_info_message("No modifications were made.")
                    return

                try:
                    collaborator_modified = self.services_crm.modify_collaborator(selected_item, collaborator_data)
                    self.view_cli.clear_screen()
                    self.view_cli.display_item_details(collaborator_modified)
                    self.view_cli.display_info_message("The collaborator has been modified successfully.")
                    break
                except Exception as e:
                    self.view_cli.display_error_message(str(e))
                    break
        else:
            print("Unsupported item type for modification:", type(selected_item))


    def instance_deletion(self, object_type: str) -> None:
        self.view_cli.clear_screen()

        our_objects = CRMFunctions.get_all_objects(object_type)
        if not our_objects:
            return

        select_collaborator = self.select_object_from(our_objects, object_type)
        if not select_collaborator:
            return

        self.delete_collaborator(select_collaborator)

    def delete_collaborator(self, collaborator: Collaborator) -> None:
        self.view_cli.clear_screen()
        self.view_cli.display_item_details(collaborator)
        self.view_cli.display_warning_message("Please note that this action is irreversible.")

        continue_action = self.view_cli.get_user_confirmation("Do you want to delete the collaborator?")

        if not continue_action:
            self.view_cli.display_info_message("The deletion of the collaborator has been canceled.")
            return
        try:
            self.services_crm.delete_collaborator(collaborator)
            self.view_cli.display_info_message("Collaborator successfully deleted.")
        except DatabaseError:
            self.view_cli.display_error_message("A problem occurred with the database. Please try again later.")
        except Exception as e:
            self.view_cli.display_error_message(f"An unexpected error occurred: {e}")
