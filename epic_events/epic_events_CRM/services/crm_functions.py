from crm.models import Collaborator
from crm.models import Evenement
from crm.models import Contract
from crm.models import Client
from crm.models import Role
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate
from django.db import DatabaseError
from django.db.models import Model
from typing import List, Optional, Any
from django.contrib.auth.models import Group


class CRMFunctions:
    @staticmethod
    def authenticate_collaborator(username: str, password: str):
        user = authenticate(username=username, password=password)
        if user is not None:
            return user
        else:
            raise ValidationError("Incorrect username or password")


    @staticmethod
    def register_collaborator(first_name: str, last_name: str, username: str, password: str, email: str, role_name: str, 
                            employee_number: str) -> Collaborator :
        try:
            if Collaborator.objects.filter(username=username).exists():
                raise ValidationError(f"The username: {username} is already in use.")
            if Collaborator.objects.filter(email=email).exists():
                raise ValidationError(f"The email: {email} is already in use.")
            if Collaborator.objects.filter(employee_number=employee_number).exists():
                raise ValidationError(f"The employee number: {employee_number} is already in use.")

            role, created = Role.objects.get_or_create(name=role_name)

            collaborator = Collaborator(first_name=first_name,
                                        last_name=last_name,
                                        username=username,
                                        email=email,
                                        role=role,
                                        employee_number=employee_number)

            collaborator.set_password(password)
            collaborator.full_clean()
            collaborator.save()

            return collaborator
        except ValidationError as e:
            raise e


    @staticmethod
    def get_all_objects(object_type: str) -> Optional[List[Any]]:
        try:
            if object_type.lower() == "collaborators":
                return Collaborator.objects.all()
            elif object_type.lower() == "contracts":
                return Contract.objects.all()
            elif object_type.lower() == "events":
                return Evenement.objects.all()
            else:
                print("Invalid object type specified.")
                return []
        except Exception as e:
            print(f"Error retrieving objects: {e}")
            return []


    @staticmethod
    def select_collaborator_from(self, list_of_collaborators: List[Collaborator],
                                message: Optional[str] = None) -> Optional[Collaborator]:

        self.view_cli.clear_screen()
        self.view_cli.display_collaborators_for_selection(list_of_collaborators)

        if message:
            self.view_cli.display_info_message(message)

        collaborators_ids = [collaborator.id for collaborator in list_of_collaborators]
        selected_collaborator_id = self.view_cli.prompt_for_selection_by_id(collaborators_ids, "Collaborator")
        selected_collaborator = next((collaborator for collaborator in list_of_collaborators
                                    if collaborator.id == selected_collaborator_id), None)

        if not selected_collaborator:
            self.view_cli.display_error_message("We couldn't find the collaborator. Please try again later.")

        return selected_collaborator


    @staticmethod
    def modify_item(selected_item: Model, modifications: dict) -> Model:
        try:
            for key, value in modifications.items():
                setattr(selected_item, key, value)

            selected_item.full_clean()
            selected_item.save()
            return selected_item

        except ValidationError as e:
            error_message = f"Validation error while modifying the {selected_item.__class__.__name__}: {e}"
            print(error_message)
            raise ValidationError(error_message) from e
        except DatabaseError as e:
            print("Problem with database access:", e)
            raise DatabaseError("Problem with database access") from e
        except Exception as e:
            error_message = f"Unexpected error modifying {selected_item.__class__.__name__}: {e}"
            print(error_message)
            raise Exception(error_message) from e


    @staticmethod
    def modify_collaborator(collaborator: Collaborator, modifications: dict) -> Collaborator:
        if 'username' in modifications and Collaborator.objects.exclude(id=collaborator.id).filter(
                username=modifications['username']).exists():
            raise ValidationError(
                f"The username: {modifications['username']} is already in use by another collaborator.")

        if 'email' in modifications and Collaborator.objects.exclude(id=collaborator.id).filter(
                email=modifications['email']).exists():
            raise ValidationError(f"The email: {modifications['email']} is already in use by another collaborator.")

        if 'employee_number' in modifications and Collaborator.objects.exclude(id=collaborator.id).filter(
                employee_number=modifications['employee_number']).exists():
            raise ValidationError(
                f"The employee number: {modifications['employee_number']} is already in use by another collaborator.")

        role_modified = False

        if 'role_name' in modifications:
            new_role_name = modifications.pop('role_name')
            if collaborator.role.name != new_role_name:
                role_modified = True
                role, created = Role.objects.get_or_create(name=new_role_name)
                collaborator.role = role

        for field, value in modifications.items():
            setattr(collaborator, field, value)

        try:
            if role_modified:
                collaborator.groups.clear()
                role_to_group = {
                    'management': 'management_team',
                    'sales': 'sales_team',
                    'support': 'support_team',
                }
                new_group_name = role_to_group.get(collaborator.role.name)
                if new_group_name:
                    new_group, _ = Group.objects.get_or_create(name=new_group_name)
                    collaborator.groups.add(new_group)

            collaborator.save()
            print(f"The Collaborator {collaborator.username} has been modified.")


        except ValidationError as e:
            raise ValidationError(f"Validation error: {e}") from e
        except DatabaseError as e:
            raise DatabaseError("Problem with database access") from e
        except Exception as e:
            raise Exception("Unexpected error updating collaborator.") from e
        return collaborator


    @staticmethod
    def delete_collaborator(collaborator: Collaborator) -> None:
        try:
            collaborator.delete()
        except DatabaseError as e:
            raise DatabaseError(f"Problem with database access") from e
        except Exception as e:
            raise Exception("Unexpected error deleting collaborator") from e
