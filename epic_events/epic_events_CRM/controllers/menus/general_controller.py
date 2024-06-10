from crm.models import Collaborator, Client, Contract, Evenement
from services.crm_functions import CRMFunctions
from views.menus.general_view import GeneralView
from typing import Any, List, Optional
from django.core.exceptions import ValidationError
from django.db import DatabaseError
from sentry_sdk import capture_message, capture_exception


class GeneralController:

    def __init__(self, collaborator: Collaborator,
                services_crm: CRMFunctions,
                general_view: GeneralView):
        self.collaborator = collaborator
        self.services_crm = services_crm
        self.general_view = general_view

    def instance_creation(self, object_type: str) -> None:
            """
            instance_creation takes the object_type str as parameter, 
            check for permissions, and call the appropriate function
            """
            # check for permissions
            if object_type.lower() == "clients":
                if not self.collaborator.has_perm("crm.add_client"):
                    capture_message(f"Unauthorized access attempt by collaborator: {self.collaborator.username}"
                                f" to manage {object_type}.", level="info")
                    self.general_view.display_error_message(f"You do not have permission to manage {object_type}.")
                    return
            elif object_type.lower() == "collaborators":
                if not self.collaborator.has_perm("crm.manage_collaborators"):
                    capture_message(f"Unauthorized access attempt by collaborator: {self.collaborator.username}"
                                f" to manage {object_type}.", level="info")
                    self.general_view.display_error_message(f"You do not have permission to manage {object_type}.")
                    return
            elif object_type.lower() == "contracts":
                if not self.collaborator.has_perm("crm.manage_contracts_creation_modification"):
                    capture_message(f"Unauthorized access attempt by collaborator: {self.collaborator.username}"
                                    f" to manage {object_type}.", level="info")
                    self.general_view.display_error_message(f"You do not have permission to manage {object_type}.")
                    return
            elif object_type.lower() == "events":
                permissions = self.collaborator.get_all_permissions()

                print("Permissions de l'utilisateur :")

                for perm in permissions:
                    print(perm)

                print("our object type", object_type)
                if not self.collaborator.has_perm("crm.add_event"):
                    capture_message(f"Unauthorized access attempt by collaborator: {self.collaborator.username}"
                                    f" to manage {object_type}.", level="info")
                    self.general_view.display_error_message(f"You do not have permission to manage {object_type}.")
                    return
            else :
                print(f"Invalid object type specified : {object_type}.")
                return
            # Check for the kind of object to create
            if object_type.lower() == "collaborators":
                while True:
                    self.general_view.clear_screen()
                    self.general_view.display_info_message("Registering new collaborator...")
                    data_collaborator = self.general_view.get_data_for_create_object("collaborators")
                    print(data_collaborator)
                    try:
                        collaborator = self.services_crm.register_collaborator(**data_collaborator)
                        self.general_view.clear_screen()
                        self.general_view.display_info_message("User registered successfully!")
                        break
                    except Exception as e:
                        self.general_view.display_error_message(str(e))
                        break
            elif object_type.lower() == "contracts":
                self.general_view.clear_screen()
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
            elif object_type.lower() == "clients":
                self.general_view.clear_screen()
                self.general_view.display_info_message("Creating a new client...")
                client_data = self.general_view.get_data_for_create_object('clients')
                print(client_data)
                client_data['commercial_contact'] = self.collaborator
                try:
                    print("client data :", client_data)
                    client = self.services_crm.create_client(**client_data)
                    self.general_view.clear_screen()
                    self.general_view.display_item_details(client)
                    self.general_view.display_info_message("Client created successfully!")
                except Exception as e:
                    self.general_view.display_error_message(str(e))
            elif object_type.lower() == "events":
                self.general_view.clear_screen()
                signed_contracts = self.get_contracts_assigned_to(self.collaborator.id, filter_type="signed")
                print('signed contracts', signed_contracts)
                if not signed_contracts:
                    return

                selected_contract = self.select_object_from(signed_contracts, "Events")
                if not selected_contract:
                    return

                self.create_event_for_signed_contract(selected_contract)
            else:
                print("Invalid object type specified.")
                return


    def get_contracts_assigned_to(self, collaborator_id: int, filter_type: str = None) -> List[Contract]:
        """
        Get the contracts assigned to the collaborator
        """
        try:
            print('nous sommes dans le try de get contract assigned to', collaborator_id, filter_type)

            contracts = self.services_crm.get_filtered_contracts_for_collaborator(collaborator_id, filter_type)
        except ValueError as e:
            capture_exception(e)
            self.general_view.display_error_message(str(e))
            return []
        except DatabaseError:
            capture_exception(e)
            self.general_view.display_error_message("I encountered a problem with the database. Please try again later.")
            return []
        except Exception as e:
            capture_exception(e)
            self.general_view.display_error_message(str(e))
            return []

        if not contracts:
            self.general_view.display_info_message("There are no contracts to display")
        return contracts


    def create_event_for_signed_contract(self, signed_contract: Contract) -> None:
        """
        Create an event for a signed contract by getting the data for the event
        and attaching the contract to it
        """
        self.general_view.clear_screen()
        self.general_view.display_object_details(signed_contract)
        event_data = self.general_view.get_data_for_add_new_event()

        event_data["contract"] = signed_contract

        try:
            print('event data', event_data)
            new_event = self.services_crm.create_event(**event_data)
            print('new event', new_event)
            self.general_view.display_object_details(new_event)
            self.general_view.display_info_message("Event created successfully.")
        except ValidationError as e:
            capture_exception(e)
            self.general_view.display_error_message(f"Validation error: {e}")
        except DatabaseError:
            capture_exception(e)
            self.general_view.display_error_message("I encountered a problem with the database. Please try again later.")
        except Exception as e:
            capture_exception(e)
            self.general_view.display_error_message(str(e))


    def select_object_from(self, list_of_objects: List[Any], object_type: str, message: Optional[str] = None) -> Optional[Any]:
        """
        select_object_from takes the list_of_objects and the object_type as parameters, 
        call a function to display it, prompt for id via another function and return a list 
        of objects matching the id prompted
        """
        self.general_view.clear_screen()

        print('list of objects', list_of_objects)

        self.general_view.display_objects_for_selection(list_of_objects)

        if message:
            self.general_view.display_info_message(message)

        objects_ids = [obj.id for obj in list_of_objects]
        print('object type dans select object from', object_type, objects_ids)
        selected_object_id = self.general_view.prompt_for_selection_by_id(objects_ids, object_type)

        selected_object = next((obj for obj in list_of_objects if obj.id == selected_object_id), None)

        if not selected_object:
            self.general_view.display_error_message(f"We couldn't find the {object_type}. Please try again later.")
        print(f"Selected object: {selected_object}")
        return selected_object


    def create_contract_for(self, client: Client) -> None:
        """
        create_contract_for takes the client as parameter, 
        call a function to gather data to create a contract,
        and call the appropriate function to create it
        """
        self.general_view.clear_screen()
        self.general_view.display_object_details(client)
        self.general_view.display_info_message(f"You are creating a new contract for: {client.name}")

        # Get contract data from the user
        data_contract = self.general_view.get_data_for_create_object('contracts')
        data_contract["client_infos"] = client
        data_contract["commercial_contact"] = client.commercial_contact

        try:
            # Create the contract using CRM service
            new_contract = self.services_crm.create_contract(**data_contract)
            self.general_view.display_info_message("Contract created successfully.")
            self.general_view.display_item_details(new_contract)

        except ValidationError as e:
            capture_exception(e)
            # Handle validation error
            self.general_view.display_error_message(f"Validation error: {e}")
            capture_exception(e)
        except DatabaseError:
            # Handle database error
            capture_exception(e)
            self.general_view.display_error_message("A database error occurred. Please try again later.")
        except Exception as e:
            capture_exception(e)
            # Handle unexpected error
            self.general_view.display_error_message(f"An unexpected error occurred: {e}")


    def instance_modification(self, object_type: str) -> None:
        """
        instance_modification takes the object_type str as parameter, 
        retrieve all objects of the type, display them to the user and 
        redirect him to the modify_object function
        """
        self.general_view.clear_screen()
        print(f"Modifying {object_type}...")
        if object_type.lower() == "contracts":
            our_objects = CRMFunctions.get_all_objects("contracts")
        else:
            print(f"Getting all {object_type}...")
            our_objects = CRMFunctions.get_all_objects(object_type)
            print('apres')
            print(our_objects, 'la liste des objets')
        if not our_objects:
            return
        print(our_objects, 'la liste des objets')
        selected_object = self.select_object_from(our_objects, object_type)

        if not selected_object:
            return
        self.modify_object(selected_object)


    def modify_object(self, selected_item: Any) -> None:
        """
        modify_object takes the selected_item as parameter, 
        check for its type, gather the data to modify it, 
        and call the appropriate function to modify it
        """
        print('on rentre dans la fonction modify object')
        if isinstance(selected_item, Client):

            self.general_view.clear_screen()
            self.general_view.display_item_details(selected_item)
            modifications = self.general_view.get_data_for_client_modification()

            # Checks if no modifications were provided.
            if not modifications:
                # Informs the user that no modifications were made and exits.
                self.general_view.display_info_message("No modifications were made.")
                return

            try:
                # Attempts to modify the client using the provided data
                client_modified = self.services_crm.modify_client(selected_item, modifications)
                self.general_view.clear_screen()
                self.general_view.display_item_details(client_modified)
                self.general_view.display_info_message("The client has been modified successfully.")
            except ValidationError as e:
                self.general_view.display_error_message(str(e))
            except DatabaseError:
                self.general_view.display_error_message("I encountered a problem with the database. Please try again.")
            except Exception as e:
                self.general_view.display_error_message(str(e))
        elif isinstance(selected_item, Contract):
            
            self.general_view.clear_screen()
            self.general_view.display_item_details(selected_item)
            contract_data = self.general_view.get_data_for_modify_contract()

            if not contract_data:
                self.general_view.display_info_message("No modifications were made.")
                return
            
            try:
                contract_modified = self.services_crm.modify_contract(selected_item, contract_data)
                self.general_view.clear_screen()
                self.general_view.display_object_details(contract_modified)
                self.general_view.display_info_message("The contract has been modified successfully.")
                return
            except ValidationError as e:
                self.general_view.display_error_message(str(e))
            except DatabaseError:
                self.general_view.display_error_message("I encountered a problem with the database. Please try again later.")
            except Exception as e:
                self.general_view.display_error_message(str(e))
        elif isinstance(selected_item, Collaborator):
            print("Colaborator modification.", {selected_item})
            while True:
                self.general_view.display_item_details(selected_item)
                collaborator_data = self.general_view.get_data_for_modify_collaborator(selected_item.get_full_name())

                if not collaborator_data:
                    self.general_view.display_info_message("No modifications were made.")
                    return

                try:
                    collaborator_modified = self.services_crm.modify_collaborator(selected_item, collaborator_data)
                    self.general_view.clear_screen()
                    self.general_view.display_item_details(collaborator_modified)
                    self.general_view.display_info_message("The collaborator has been modified successfully.")
                    break
                except Exception as e:
                    self.general_view.display_error_message(str(e))
                    break
        elif isinstance(selected_item, Evenement):
            self.general_view.clear_screen()
            self.general_view.display_item_details(selected_item)
            event_data = self.general_view.get_data_for_modify_event()

            if not event_data:
                self.general_view.display_info_message("No modifications were made.")
                return

            try:
                event_modified = self.general_view.modify_event(selected_item, event_data)
                self.general_view.clear_screen()
                self.general_view.display_item_details(event_modified)
                self.general_view.display_info_message("The event has been modified successfully.")
            except ValidationError as e:
                self.general_view.display_error_message(str(e))
            except DatabaseError:
                self.general_view.display_error_message("I encountered a problem with the database. Please try again later.")
            except Exception as e:
                self.general_view.display_error_message(str(e))
        elif isinstance(selected_item, Contract):
            self.general_view.clear_screen()
            self.general_view.display_contract_details(selected_item)

            modifications = self.general_view.get_data_for_contract_modification()

            if not modifications:

                self.general_view.display_info_message("No modifications were made.")
                return

            try:
                contract_modified = self.services_crm.modify_contract(selected_item, modifications)
                self.general_view.clear_screen()

                self.general_view.display_item_details(contract_modified)

                self.general_view.display_info_message("The contract has been modified successfully.")
                return
            except ValidationError as e:
                capture_exception(e)
                self.general_view.display_error_message(str(e))
            except DatabaseError:
                capture_exception(e)
                self.general_view.display_error_message("I encountered a problem with the database. Please try again later.")
            except Exception as e:
                capture_exception(e)
                self.general_view.display_error_message(str(e))
        else:
            print("Unsupported item type for modification:", type(selected_item))


    def get_events_for_collaborator(self, collaborator_id: int) -> List[Evenement]:
        """
        get_events_for_collaborator takes the collaborator_id as parameter, 
        call the appropriate function to retrieve the events for the collaborator, 
        and return the list of events
        """
        try:
            events = self.services_crm.get_events_for_collaborator(collaborator_id)

        except DatabaseError:
            self.general_view.display_error_message("I encountered a problem with the database. Please again later.")
            return []
        except Exception as e:
            self.general_view.display_error_message(str(e))
            return []

        if not events:
            self.general_view.display_info_message("There is no events available to display.")

        return events


    def show_all_objects(self, object_type: str) -> None:
        """
        show_all_objects takes the object_type str as parameter,
        check for permissions, retrieve all objects of the type, 
        display them to the user, and return the list of objects
        """
        self.general_view.clear_screen()
        objects = CRMFunctions.get_all_objects(object_type)

        if not objects:
            print(f"No {object_type} found.")
            return

        if object_type.lower() == "collaborators":
            if not self.collaborator.has_perm("crm.manage_collaborators"):
                capture_message(f"Unauthorized access attempt by collaborator: {self.collaborator.username}"
                            f" to manage {object_type}.", level="info")
                self.general_view.display_error_message(f"You do not have permission to manage {object_type}.")
                return
        elif object_type.lower() == "contracts":
            if not self.collaborator.has_perm("crm.view_contract"):
                capture_message(f"Unauthorized access attempt by collaborator: {self.collaborator.username}"
                            f" to manage {object_type}.", level="info")

                self.general_view.display_error_message(f"You do not have permission to manage {object_type}.")
                return
        elif object_type.lower() == "events":
            if not self.collaborator.has_perm("crm.view_event"):
                capture_message(f"Unauthorized access attempt by collaborator: {self.collaborator.username}"
                            f" to manage {object_type}.", level="info")

                self.general_view.display_error_message(f"You do not have permission to manage {object_type}.")
                return
        else :
            print(f"Invalid object type specified : {object_type}.")
            return

        if object_type.lower() == "clients":
            self.general_view.display_list(objects, object_type)
        elif object_type.lower() == "contracts" or object_type.lower() == "contracts2":
            self.general_view.display_list(objects, "contracts")
        elif object_type.lower() == "events":
            self.general_view.display_list(objects, object_type)
