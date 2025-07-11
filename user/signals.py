# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.contrib.auth import get_user_model
# User = get_user_model()
# from dashboard.models import Staff

# @receiver(post_save, sender=User)
# def create_staff_profile(sender, instance, created, **kwargs):
#     if created:
#         Staff.objects.create(user=instance)

# @receiver(post_save, sender=User)
# def save_staff_profile(sender, instance, **kwargs):
#     if hasattr(instance, 'staff'):
#         instance.staff.save()
