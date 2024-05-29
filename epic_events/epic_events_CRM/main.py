import os
import django
from dotenv import load_dotenv

load_dotenv()

def setup_django():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epic_events_CRM.settings")
    django.setup()

setup_django()

import sentry_sdk
from controllers.crm_controllers import CRMController

sentry_dsn = os.getenv('SENTRY_DSN')

sentry_sdk.init(
    dsn=sentry_dsn,
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

def main():
    main_controller = CRMController()
    main_controller.start()

if __name__ == "__main__":
    main()
