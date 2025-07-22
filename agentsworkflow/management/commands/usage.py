from django.core.management.base import BaseCommand
from .utils import retrive_data, update_database, categorize_emails


class Command(BaseCommand):
    help = "Run the email agent logic for a specific user"

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to process emails for')

    def handle(self, *args, **kwargs):
        username = kwargs['username']
        self.stdout.write(self.style.SUCCESS(f"Running email agent for: {username}"))

        try:
            answer = retrive_data(username)
            self.stdout.write(self.style.SUCCESS(f"Data Retrieved:\n{answer}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error: {e}"))
