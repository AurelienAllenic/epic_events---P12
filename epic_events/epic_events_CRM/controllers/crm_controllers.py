from typing import Optional
from django.core.exceptions import ValidationError
from crm.models import Collaborator
from services.crm_functions import CRMFunctions
from views.crm_views import CRMView
from controllers.menus.management_controller import ManagementController
from controllers.menus.sales_controller import SalesController
from views.menus.management_view import ManagementView
from views.menus.general_view import GeneralView
from views.menus.sales_view import SalesView
from controllers.menus.general_controller import GeneralController
from controllers.menus.support_controller import SupportController
from views.menus.support_view import SupportView


class CRMController:
    def __init__(self):
        self.crm_services = CRMFunctions()
        self.view_cli = CRMView()


    def authenticate_collaborator(self) -> Optional[Collaborator]:
        """
        Authenticate the collaborator by prompting the user for their username and password
        and then authenticating the user
        """
        login_data = self.view_cli.prompt_login()
        try:

            user = self.crm_services.authenticate_collaborator(**login_data)
            self.view_cli.display_info_message("Logged in successfully!")
            return user
        except ValidationError as e:
            self.view_cli.display_error_message(f"Login failed: {e}")
            return None


    def start(self):
        """
        Start the application by authenticating the collaborator
        and then displaying the main menu corresponding to its role
        """
        collaborator = self.authenticate_collaborator()

        if collaborator is None:
            return
        
        if collaborator.role is not None:
            role_name = collaborator.role.name
        else:
            self.view_cli.display_warning_message("Your account does not have a role assigned")
            return

        match role_name:
            case "support":
                view_cli = SupportView()
                general_view = GeneralView()
                general_controller = GeneralController(collaborator, self.crm_services, general_view)
                support_role_controller = SupportController(collaborator, self.crm_services, view_cli, general_controller,general_view)
                support_role_controller.start()
            case "sales":
                view_cli = SalesView()
                general_view = GeneralView()
                general_controller = GeneralController(collaborator, self.crm_services, general_view)
                sales_role_controller = SalesController(collaborator, self.crm_services, view_cli, general_controller,general_view)
                sales_role_controller.start()
            case "management":
                view_cli = ManagementView()
                general_view = GeneralView()
                general_controller = GeneralController(collaborator, self.crm_services, general_view)
                management_role_controller = ManagementController(collaborator, self.crm_services, view_cli, general_controller, general_view)
                management_role_controller.start()
            case _:
                self.view_cli.display_warning_message("Your role does not have specific task assigned.")
