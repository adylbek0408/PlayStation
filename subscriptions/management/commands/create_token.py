from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


class Command(BaseCommand):
    help = 'Creates a token for a user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the user')

    def handle(self, *args, **options):
        username = options['username']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f'User "{username}" does not exist')

        token, created = Token.objects.get_or_create(user=user)
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created token {token.key} for user {user.username}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Retrieved existing token {token.key} for user {user.username}'))