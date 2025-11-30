from django.core.management.base import BaseCommand, CommandError
from accounts.models import User

class Command(BaseCommand):
    help = 'Sets is_staff to True for a specified user.'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='The username of the user to make staff.')

    def handle(self, *args, **options):
        username = options['username']
        try:
            user = User.objects.get(username=username)
            user.is_staff = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully set {username} as staff.'))
        except User.DoesNotExist:
            raise CommandError(f'User "{username}" does not exist.')
        except Exception as e:
            raise CommandError(f'An error occurred: {e}')
