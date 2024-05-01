import os
import django
import json

def setup_django():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epic_events_CRM.settings")
    django.setup()


setup_django()

from views.crm_views import CRMView # Views
from services.crm_functions import CRMFunctions # Services
from controllers.crm_controllers import CRMController # Controllers


def main():
    main_controller = CRMController()
    main_controller.start()


if __name__ == "__main__":
    main()
