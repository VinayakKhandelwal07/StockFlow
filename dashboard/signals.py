from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver
from .models import Company, Order, AuditTrail, User, Staff
import logging
from user.middleware import get_current_user

logger = logging.getLogger(__name__)


def get_order_user(instance):
    """
    Helper to get the user who performed an action on an Order.
    Prioritize reviewed_by, fallback to staff.
    """
    return getattr(instance, 'reviewed_by', None) or getattr(instance, 'staff', None)


def safe_create_audit_trail(*, user, action, model, event_category, method, object_id, company, summary):
    """
    Safely create an AuditTrail entry.
    Company is either a Company instance or None.
    """
    try:
        AuditTrail.objects.create(
            user=user,
            action=action,
            model=model,
            event_category=event_category,
            method=method,
            object_id=object_id,
            company=company,
            summary=summary,
        )
    except Exception as e:
        logger.error(f"Failed to create AuditTrail: {e} (user={user}, action={action}, model={model}, object_id={object_id})")


@receiver(post_save, sender=Order)
def log_order_save(sender, instance, created, **kwargs):
    user = get_current_user() or get_order_user(instance)
    if not user:
        logger.warning(f"No user found for Order #{instance.company_order_id} when saving.")
        return

    action = 'created' if created else 'updated'
    method = 'CREATE' if created else 'UPDATE'
    summary = (
        f'Order #{instance.company_order_id} created with status {instance.order_status}'
        if created else
        f'Order #{instance.company_order_id} updated. Current status: {instance.order_status}'
    )

    # Pass the company instance directly; it's safe here because Order still exists
    safe_create_audit_trail(
        user=user,
        action=action,
        model='Order',
        event_category='Order Management',
        method=method,
        object_id=instance.company_order_id,
        company=instance.company,
        summary=summary,
    )
    logger.info(f"Audit log created for Order #{instance.company_order_id} ({action}) by {user.username}")


@receiver(post_delete, sender=Order)
def log_order_delete(sender, instance, **kwargs):
    user = get_current_user() or get_order_user(instance)
    if not user:
        logger.warning(f"No user found for Order #{instance.company_order_id} when deleting.")
        return

    # IMPORTANT: company=None because the order is deleted; FK must be null to avoid error
    safe_create_audit_trail(
        user=user,
        action='delete',
        model='Order',
        event_category='Order Management',
        method='DELETE',
        object_id=instance.company_order_id,
        company=None,
        summary=f'Order #{instance.company_order_id} deleted',
    )
    logger.info(f"Audit log created for Order #{instance.company_order_id} (deleted) by {user.username}")


@receiver(post_save, sender=User)
def create_or_update_staff(sender, instance, created, **kwargs):
    """
    Create or update Staff profile for non-superuser and non-staff users.
    """
    if instance.is_superuser or instance.is_staff:
        return

    if created:
        Staff.objects.create(user=instance)
    else:
        if hasattr(instance, 'staff'):
            instance.staff.save()
        else:
            Staff.objects.create(user=instance)


@receiver(post_delete, sender=Staff)
def delete_user_when_staff_deleted(sender, instance, **kwargs):
    """
    Delete the User when Staff is deleted unless the user is superuser.
    """
    try:
        user = instance.user
        if not user.is_superuser:
            user.delete()
    except User.DoesNotExist:
        pass


@receiver(pre_delete, sender=Company)
def log_company_deletion(sender, instance, **kwargs):
    user = get_current_user()
    if not user:
        logger.warning(f"No user found when deleting Company '{instance.name}'.")
        return

    # Company is about to be deleted, so company=None to avoid FK violation
    try:
        AuditTrail.objects.create(
            user=user,
            action='delete',
            model='Company',
            event_category='Company Management',
            method='DELETE',
            object_id=instance.pk,
            company=None,
            summary=f'Company "{instance.name}" deleted',
        )
        logger.info(f"Audit log created for Company '{instance.name}' deletion by {user.username}")
    except Exception as e:
        logger.error(f"Failed to log audit trail for Company deletion '{instance.name}': {e}")
