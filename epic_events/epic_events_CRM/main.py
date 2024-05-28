import os
import django
import sentry_sdk
from dotenv import load_dotenv
from controllers.crm_controllers import CRMController

load_dotenv()

sentry_dsn = os.getenv('SENTRY_DSN')

sentry_sdk.init(
    dsn=sentry_dsn,
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

def setup_django():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "epic_events_CRM.settings")
    django.setup()


setup_django()


def main():
    main_controller = CRMController()
    main_controller.start()


if __name__ == "__main__":
    main()
