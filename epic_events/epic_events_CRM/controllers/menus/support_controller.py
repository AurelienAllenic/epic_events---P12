from django.db import DatabaseError
from typing import List
from crm.models import Collaborator
from crm.models import Evenement
from services.crm_functions import CRMFunctions
from views.menus.support_view import SupportView
from views.menus.general_view import GeneralView
from controllers.menus.general_controller import GeneralController


class SupportController:


    def __init__(self, collaborator: Collaborator,
                services_crm: CRMFunctions,
                view_cli: SupportView,
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
        Start the support menu by displaying the main menu
        and getting the user's choice
        """
        self.view_cli.display_info_message(f"Hi! {self.collaborator.get_full_name()}")
        self.view_cli.show_main_menu(collaborator=self.collaborator)

        choice = self.view_cli.get_user_menu_choice()

        match choice:
            case 1:
                # Show all clients
                self.general_controller.show_all_objects("Clients")
            case 2:
                # Show all contracts
                self.general_controller.show_all_objects("Contracts")
            case 3:
                # Show all events
                self.general_controller.show_all_objects("Events")
            case 4:
                # Show all events for the selectedcollaborator
                self.show_events_for_collaborator()
            case 5:
                # Modify an event
                self.general_controller.instance_modification("Events")
            case 6:
                # Return to main menu
                return
            case _:
                print(
                    f"Invalid menu option selected: {choice}. in start() at support controller"
                    f"Expected options were between 1 and 6.",
                    level='error')
                self.view_cli.display_error_message("Invalid option selected. Please try again.")
                self.start()

        continue_operation = self.view_cli.ask_user_if_continue()
        if not continue_operation:
            return
        self.start()


    def show_events_for_collaborator(self) -> None:
        """
        Show all events for the selected collaborator after checking for permissions
        """
        self.view_cli.clear_screen()
        if not self.collaborator.has_perm("crm.view_event"):

            print(f"Unauthorized access attempt by collaborator: {self.collaborator.username}"
                            f" to the list of events for the collaborator.", level="info")
            self.view_cli.display_error_message("You do not have permission to view the list of events.")
            return

        events_for_collaborator = self.get_events_for_collaborator(self.collaborator.id)

        if not events_for_collaborator:
            return

        self.general_view.display_list(events_for_collaborator, "events")


    def get_events_for_collaborator(self, collaborator_id: int) -> List[Evenement]:
        """
        get_events_for_collaborator takes a collaborator_id as a parameter, and get
        all events for the selected collaborator by passing the collaborator_id as
        parameter of the called function
        """
        try:
            events = self.services_crm.get_events_for_collaborator(collaborator_id)

        except DatabaseError:
            self.view_cli.display_error_message("I encountered a problem with the database. Please again later.")
            return []
        except Exception as e:
            self.view_cli.display_error_message(str(e))
            return []

        if not events:
            self.view_cli.display_info_message("There is no events available to display.")

        return events
