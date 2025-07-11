from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Create a standalone superuser without company'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        username = input("Username: ").strip()
        email = input("Email: ").strip()
        password = input("Password: ").strip()

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR("Username already exists."))
            return

        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        # Ensure no company or staff record is created
        user.company = None
        user.save()

        self.stdout.write(self.style.SUCCESS("Superuser created successfully."))
