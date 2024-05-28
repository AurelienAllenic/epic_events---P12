from crm.models import Collaborator, Evenement
from services.crm_functions import CRMFunctions
from views.menus.management_view import ManagementView
from typing import Any, List, Optional
from django.db import DatabaseError
from controllers.menus.general_controller import GeneralController
from views.menus.general_view import GeneralView
from sentry_sdk import capture_message, capture_exception


class ManagementController:
    MAIN_MENU_OPTIONS_MANAGEMENT = [
        "1 - Manipulate collaborators data in the CRM system.",
        "2 - Manipulate contracts.",
        "3 - Filter events based on whether they have or don't have a support contact.",
        "4 - Assign or change the 'support' collaborator associated with an event.",
        "5 - View the list of all clients.",
        "6 - View the list of all contracts.",
        "7 - View the list of all events.",
        "8 - Exit the CRM."
    ]

    SUB_MENU_MANAGE_COLLABORATORS_MANAGEMENT = [
        "1 - Create a collaborator.",
        "2 - Update a collaborator.",
        "3 - Delete a collaborator.",
        "4 - Return to main menu"
    ]

    SUB_MENU_MANAGE_CONTRACTS_MANAGEMENT = [
        "1 - Create new contract.",
        "2 - Update a contract.",
        "3 - Return to main menu"
    ]

    SUB_MENU_EVENTS_MANAGEMENT = [
        "1 - View events with support contact assigned.",
        "2 - View events without support contact assigned.",
        "3 - Return to main menu"
    ]


    def __init__(self, collaborator: Collaborator,
                services_crm: CRMFunctions,
                view_cli: ManagementView,
                general_controller : GeneralController,
                general_view : GeneralView
                ):
        self.collaborator = collaborator
        self.services_crm = services_crm
        self.view_cli = view_cli
        self.general_controller = general_controller
        self.general_view = general_view


    def start(self) -> None:
        """
        start takes no parameters, 
        display the main menu for a collaborator with role management
        and redirect him accordingly
        """
        name_to_display = self.collaborator.get_full_name() or self.collaborator.username

        self.view_cli.show_menu(name_to_display, self.MAIN_MENU_OPTIONS_MANAGEMENT)

        choice = self.view_cli.get_collaborator_choice(limit=len(self.MAIN_MENU_OPTIONS_MANAGEMENT))

        match choice:
            case 1:
                # Manage collaborators
                self.manage_management_objects("Collaborators")
            case 2:
                # Manage contracts
                self.manage_management_objects("Contracts")
            case 3:
                # Manage events
                self.manage_management_objects("Events")
            case 4:
                # Manage support contacts
                self.modify_support_contact()
            case 5:
                # Show All Clients
                self.general_controller.show_all_objects("Clients")
            case 6:
                # Show All Contracts
                self.general_controller.show_all_objects("Contracts")
            case 7:
                # Show All Events
                self.general_controller.show_all_objects("Events")
            case 8:
                # Exit the CRM
                return
            case _:
                capture_message(
                    f"Invalid menu option : {choice}. in start() - management controller."
                    f"Expected options between 1 and {len(self.MAIN_MENU_OPTIONS_MANAGEMENT)}.",
                    level='error')
                self.view_cli.display_error_message("Invalid option selected. Please try again.")

        continue_operation = self.view_cli.ask_user_if_continue()

        if not continue_operation:
            return
        
        self.start()


    def manage_management_objects(self, object_type: str) -> None:
        """
        manage_management_objects takes the object_type str as parameter, 
        check for permissions, and redirect the user either to another menu
        to choose an option or to a function to match his choice 
        """
        self.view_cli.clear_screen()
        # Check for Permissions according to the object_type
        if object_type.lower() == "collaborators":
            if not self.collaborator.has_perm("crm.manage_collaborators"):
                capture_message(f"Unauthorized access attempt by collaborator: {self.collaborator.username}"
                            f" to manage {object_type}.", level="info")
                self.view_cli.display_error_message(f"You do not have permission to manage {object_type}.")
                return
            user_perms = self.collaborator.user_permissions
            print("Permissions de l'utilisateur :", user_perms)
        elif object_type.lower() == "contracts":
            if not self.collaborator.has_perm("crm.manage_contracts_creation_modification"):
                capture_message(f"Unauthorized access attempt by collaborator: {self.collaborator.username}"
                            f" to manage {object_type}.", level="info")
                self.view_cli.display_error_message(f"You do not have permission to manage {object_type}.")
                return
        elif object_type.lower() == "events":
            if not self.collaborator.has_perm("crm.view_event"):
                capture_message(f"Unauthorized access attempt by collaborator: {self.collaborator.username}"
                            f" to manage {object_type}.", level="info")

                self.view_cli.display_error_message(f"You do not have permission to manage {object_type}.")
                return
        # Redirect the user to the appropriate menu or function
        choice = None
        if object_type.lower() == "collaborators" or object_type.lower() == "clients":
            self.view_cli.show_menu(self.collaborator.get_full_name(), self.SUB_MENU_MANAGE_COLLABORATORS_MANAGEMENT)
            choice = self.view_cli.get_collaborator_choice(limit=len(self.SUB_MENU_MANAGE_COLLABORATORS_MANAGEMENT))
        elif object_type.lower() == "contracts":
            self.view_cli.show_menu(self.collaborator.get_full_name(), self.SUB_MENU_MANAGE_CONTRACTS_MANAGEMENT)
            choice = self.view_cli.get_collaborator_choice(limit=len(self.SUB_MENU_MANAGE_CONTRACTS_MANAGEMENT))
        elif object_type.lower() == "events":
            self.view_cli.show_menu(self.collaborator.get_full_name(), self.SUB_MENU_EVENTS_MANAGEMENT)
            choiceEvent = self.view_cli.get_collaborator_choice(limit=len(self.SUB_MENU_EVENTS_MANAGEMENT))
        else:
            print(f"Invalid object type specified : {object_type}.")
            return
        if choice != None:
            # Menu for both contracts and events, adapting to the object_type
            match choice:
                case 1:
                    # Create an instance object corresponding to the object_type
                    self.general_controller.instance_creation(object_type)
                case 2:
                    # Update an instance object corresponding to the object_type
                    self.general_controller.instance_modification(object_type)
                case 3:
                    # Delete an instance object if the object_type is contracts, else restart the menu
                    if object_type.lower() == "contracts":
                        self.start()
                    else:
                        self.instance_deletion(object_type)
                case 4:
                    # Return to the main menu
                    self.start()
                case _:
                    capture_message(
                    f"Invalid option : {choice}. in start() - management controller."
                    f"Expected between 1 and 3 if object_type is contracts and 4 if object_type is events.",
                    level='error')
                    self.view_cli.display_info_message("Invalid option selected. Please try again.")
                    return
        else:
            match choiceEvent:
                case 1:
                    # Show events with support contact assigned
                    self.show_events_with_support()
                case 2:
                    # Show events without support contact assigned
                    self.show_events_without_support()
                case 3:
                    # Return to the main menu
                    self.start()
                case _:
                    capture_message(
                    f"Invalid menu option : {choice}. in start() - management controller."
                    f"Expected options between 1 and {len(self.SUB_MENU_EVENTS_MANAGEMENT)}.",
                    level='error')
                    self.view_cli.display_info_message("Invalid option selected. Please try again.")
                    return


    def show_events_with_support(self) -> None:
        """
        show_events_with_support takes no parameters, 
        get the events with support contact assigned, 
        and display them
        """
        events_to_show = self.get_events_with_optional_filter(support_contact_required=True)


        if not events_to_show:
            return

        self.view_cli.display_list(events_to_show, "events")


    def show_events_without_support(self) -> None:
        """
        show_events_without_support takes no parameters, 
        get the events without support contact assigned, 
        and display them
        """
        events_to_show = self.get_events_with_optional_filter(support_contact_required=False)


        if not events_to_show:
            return
        
        self.view_cli.display_list(events_to_show, "events")


    def modify_support_contact(self) -> None:
        """
        modify_support_contact takes no parameters, 
        get the events with support contact assigned, 
        and display them
        """
        self.view_cli.clear_screen()

        events = self.get_events_with_optional_filter(support_contact_required=None)
        if not events:
            return
        print(events, 'events')
        selected_event = self.general_controller.select_object_from(events, object_type="Events")
        if not selected_event:
            return

        support_collaborators = self.get_support_collaborators()
        print(support_collaborators, "le type de support_collaborators")
        if not support_collaborators:
            return
        
        selected_support_collaborator = self.general_controller.select_object_from(support_collaborators,
                                                            "collaborators")
        print("selected_support_collaborator", selected_support_collaborator)
        print(type(selected_event), 'le type de selected event')
        print(selected_event, 'selected event')
        event_with_new_support_collaborator = self.add_support_contact_to_event(selected_event,
                                                                                selected_support_collaborator)
        print(event_with_new_support_collaborator, "le type de event_with_new_support_collaborator")
        self.view_cli.display_object_details(event_with_new_support_collaborator)
        self.view_cli.display_info_message(f"The support contact {selected_support_collaborator.get_full_name()}"
                                        f" has been correctly assigned to the event.")


    def instance_deletion(self, object_type: str) -> None:
        """
        instance_deletion takes the object_type str as parameter, 
        get all the instances of the object_type, 
        display them, allow user to select one, 
        and delete it
        """
        self.view_cli.clear_screen()
        our_objects = CRMFunctions.get_all_objects(object_type)
        if not our_objects:
            return

        select_collaborator = self.general_controller.select_object_from(our_objects, object_type)
        if not select_collaborator:
            return

        self.delete_collaborator(select_collaborator)


    def delete_collaborator(self, collaborator: Collaborator) -> None:
        """
        delete_collaborator takes the collaborator object as parameter, 
        display the collaborator details, 
        ask the user if he wants to delete the collaborator, 
        and delete it if he confirms
        """
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
            capture_exception(e)
            self.view_cli.display_error_message("A problem occurred with the database. Please try again later.")
        except Exception as e:
            capture_exception(e)
            self.view_cli.display_error_message(f"An unexpected error occurred: {e}")



    def get_events_with_optional_filter(self, support_contact_required: Optional[bool] = None) -> List[Evenement]:
        """
        get_events_with_optional_filter takes the support_contact_required bool as parameter, 
        get the events with optional filter, 
        and return them
        """
        try:
            events = self.services_crm.get_all_events_with_optional_filter(support_contact_required)

        except DatabaseError:
            capture_exception(e)
            self.view_cli.display_error_message("I encountered a problem with the database. Please try again later.")
            return []
        except Exception as e:
            capture_exception(e)
            self.view_cli.display_error_message(f"{e}")
            return []

        if not events:
            self.view_cli.display_info_message("There are no events available to display.")

        return events


    def get_support_collaborators(self) -> List[Collaborator]:
        """
        get_support_collaborators takes no parameters, 
        get the support collaborators, 
        and return them
        """
        try:
            support_collaborators = self.services_crm.get_support_collaborators()

        except DatabaseError:
            capture_exception(e)
            self.view_cli.display_error_message("I encountered a problem with the database. Please try again later.")
            return []
        except Exception as e:
            capture_exception(e)
            self.view_cli.display_error_message(str(e))
            return []

        if not support_collaborators:
            self.view_cli.display_info_message("There not support collaborators to display.")

        return support_collaborators


    def add_support_contact_to_event(self, event: Evenement, support_contact: Collaborator) -> Evenement:
        """
        add_support_contact_to_event takes the event object and the support_contact object as parameters, 
        add the support contact to the event, 
        and return the event with the new support contact for validation
        """
        try:
            print("event", event, "support_contact", event.client.id)

            event_with_new_support_contact = self.services_crm.add_support_contact_to_event(event, support_contact)
            print(event_with_new_support_contact, "event with new support contact")
            return event_with_new_support_contact
        except DatabaseError:
            capture_exception(e)
            self.view_cli.display_error_message("I encountered a problem with the database. Please try again later.")
        except Exception as e:
            capture_exception(e)
            self.view_cli.display_error_message(str(e))
