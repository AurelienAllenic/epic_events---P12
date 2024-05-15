from crm.models import Collaborator, Contract, Client, Evenement
from services.crm_functions import CRMFunctions
from views.menus.management_view import ManagementView
from django.core.exceptions import ValidationError
from typing import Any, List, Optional
from django.db import DatabaseError
from django.db.models.query import QuerySet

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
                view_cli: ManagementView):
        self.collaborator = collaborator
        self.services_crm = services_crm
        self.view_cli = view_cli


    def start(self) -> None:
        name_to_display = self.collaborator.get_full_name() or collaborator.username
        self.view_cli.show_menu(name_to_display, self.MAIN_MENU_OPTIONS_MANAGEMENT)
        choice = self.view_cli.get_collaborator_choice(limit=len(self.MAIN_MENU_OPTIONS_MANAGEMENT))

        match choice:
            case 1:
                self.manage_management_objects("Collaborators")
            case 2:
                self.manage_management_objects("Contracts")
            case 3:
                self.manage_management_objects("Events")
            case 4:
                self.modify_support_contact()
            case 5:
                self.show_all_management_objects("Clients")
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

        if object_type.lower() == "clients":
            self.view_cli.display_list(objects, object_type)
        elif object_type.lower() == "contracts" or object_type.lower() == "contracts2":
            self.view_cli.display_list(objects, "contracts")
        elif object_type.lower() == "events":
            self.view_cli.display_list(objects, object_type)


    def manage_management_objects(self, object_type: str) -> None:
        self.view_cli.clear_screen()
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
            match choice:
                case 1:
                    self.instance_creation(object_type)
                case 2:
                    self.instance_modification(object_type)
                case 3:
                    if object_type.lower() == "contracts":
                        self.start()
                    else:
                        self.instance_deletion(object_type)
                case 4:
                    if(object_type.lower() != "contracts"):
                        self.start()
                    print("Nous ne devrions pas voir celà.")
                    return
                case _:
                    print("Invalid option selected. Please try again.")
                    self.view_cli.display_info_message("Invalid option selected. Please try again.")
                    return
        else:
            match choiceEvent:
                case 1:
                    self.show_events_with_support()
                case 2:
                    self.show_events_without_support()
                case 3:
                    self.start()
                case _:
                    print("Invalid option selected. Please try again.")
                    self.view_cli.display_info_message("Invalid option selected. Please try again.")
                    return


    def show_events_with_support(self) -> None:
        events_to_show = self.get_events_with_optional_filter(support_contact_required=True)

        if not events_to_show:
            return

        self.view_cli.display_list(events_to_show, "events")


    def show_events_without_support(self) -> None:
        events_to_show = self.get_events_with_optional_filter(support_contact_required=False)

        if not events_to_show:
            return
        
        self.view_cli.display_list(events_to_show, "events")


    def instance_creation(self, object_type: str) -> None:
        print('nous sommes dans instance Creation')
        if object_type.lower() == "collaborators":
            print('nous sommes dans instance Creation pour les collaborators')
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
            print('nous sommes dans instance Creation pour les contracts')
            self.view_cli.clear_screen()
            print(f"Creating contract for client... of type {object_type}...")
            clients = CRMFunctions.get_all_objects('clients')
            contracts = CRMFunctions.get_all_objects('contracts')
            print(f'the clients are {clients}')
            print(f'the contracts are {contracts}')
            if not clients:
                print("No clients for the moment")
                return
            selected_contract = self.select_object_from(clients, "contracts")
            selected_client = self.select_object_from(clients, "contracts")

            if not selected_client:
                return print("No client selected.")

            self.create_contract_for(selected_client)
        else:
            print("Invalid object type specified.")
            return


    def create_contract_for(self, client: Client) -> None:
        print('create function atteinte')
        self.view_cli.clear_screen()
        self.view_cli.display_object_details(client)
        self.view_cli.display_info_message(f"You are creating a new contract for: {client.name}")

        # Get contract data from the user
        data_contract = self.view_cli.get_data_for_create_contract()
        data_contract["client_infos"] = client
        data_contract["commercial_contact"] = client.commercial_contact

        try:
            # Create the contract using CRM service
            new_contract = self.services_crm.create_contract(**data_contract)
            self.view_cli.display_info_message("Contract created successfully.")
            self.view_cli.display_object_details(new_contract)

        except ValidationError as e:
            # Handle validation error
            self.view_cli.display_error_message(f"Validation error: {e}")
        except DatabaseError:
            # Handle database error
            self.view_cli.display_error_message("A database error occurred. Please try again later.")
        except Exception as e:
            # Handle unexpected error
            self.view_cli.display_error_message(f"An unexpected error occurred: {e}")


    def instance_modification(self, object_type: str) -> None:
        self.view_cli.clear_screen()
        if object_type.lower() == "contracts":
            our_objects = CRMFunctions.get_all_objects("contracts")
        else:
            our_objects = CRMFunctions.get_all_objects(object_type)

        if not our_objects:
            return

        selected_object = self.select_object_from(our_objects, object_type)

        if not selected_object:
            return

        self.modify_object(selected_object)


    def select_object_from(self, list_of_objects: List[Any], object_type: str, message: Optional[str] = None) -> Optional[Any]:
        print('on rentre dans la fonction select object from')
        self.view_cli.clear_screen()
        print('list of objects', list_of_objects)
        self.view_cli.display_objects_for_selection(list_of_objects)

        if message:
            self.view_cli.display_info_message(message)

        objects_ids = [obj.id for obj in list_of_objects]
        print('object type dans select object from', object_type)
        selected_object_id = self.view_cli.prompt_for_selection_by_id(objects_ids, object_type)

        selected_object = next((obj for obj in list_of_objects if obj.id == selected_object_id), None)

        if not selected_object:
            self.view_cli.display_error_message(f"We couldn't find the {object_type}. Please try again later.")
        print(f"Selected object: {selected_object}")
        return selected_object
    

    def modify_object(self, selected_item: Any) -> None:
        if isinstance(selected_item, Client):
            print("Client modification not implemented yet.")
        elif isinstance(selected_item, Contract):
            
            self.view_cli.clear_screen()
            self.view_cli.display_item_details(selected_item)
            contract_data = self.view_cli.get_data_for_modify_contract()

            if not contract_data:
                self.view_cli.display_info_message("No modifications were made.")
                return
            
            try:
                contract_modified = self.services_crm.modify_contract(selected_item, contract_data)
                self.view_cli.clear_screen()
                self.view_cli.display_object_details(contract_modified)
                self.view_cli.display_info_message("The contract has been modified successfully.")
                return
            except ValidationError as e:
                self.view_cli.display_error_message(str(e))
            except DatabaseError:
                self.view_cli.display_error_message("I encountered a problem with the database. Please try again later.")
            except Exception as e:
                self.view_cli.display_error_message(str(e))
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


    def modify_support_contact(self) -> None:
        self.view_cli.clear_screen()

        events = self.get_events_with_optional_filter(support_contact_required=None)
        if not events:
            return
        print(events, 'events')
        selected_event = self.select_object_from(events, object_type="Events")
        if not selected_event:
            return

        support_collaborators = self.get_support_collaborators()
        print(support_collaborators, "le type de support_collaborators")
        if not support_collaborators:
            return
        
        selected_support_collaborator = self.select_object_from(support_collaborators,
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


    def get_events_with_optional_filter(self, support_contact_required: Optional[bool] = None) -> List[Evenement]:
        try:
            events = self.services_crm.get_all_events_with_optional_filter(support_contact_required)
        except DatabaseError:
            self.view_cli.display_error_message("I encountered a problem with the database. Please try again later.")
            return []
        except Exception as e:
            self.view_cli.display_error_message(f"{e}")
            return []

        if not events:
            self.view_cli.display_info_message("There are no events available to display.")

        return events


    def get_support_collaborators(self) -> List[Collaborator]:
        try:
            support_collaborators = self.services_crm.get_support_collaborators()
        except DatabaseError:
            self.view_cli.display_error_message("I encountered a problem with the database. Please try again later.")
            return []
        except Exception as e:
            self.view_cli.display_error_message(str(e))
            return []

        if not support_collaborators:
            self.view_cli.display_info_message("There not support collaborators to display.")

        return support_collaborators


    def add_support_contact_to_event(self, event: Evenement, support_contact: Collaborator) -> Evenement:
        try:
            print("event", event, "support_contact", event.client.id)
            event_with_new_support_contact = self.services_crm.add_support_contact_to_event(event, support_contact)
            print(event_with_new_support_contact, "event with new support contact")
            return event_with_new_support_contact
        except DatabaseError:
            self.view_cli.display_error_message("I encountered a problem with the database. Please try again later.")
        except Exception as e:
            self.view_cli.display_error_message(str(e))
