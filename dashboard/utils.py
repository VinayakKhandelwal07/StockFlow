from .models import AuditTrail

def log_user_action(user, action, model='Order', method='manual', object_id=None):
    summary = f"{model} {action} by {user.get_full_name() or user.username}"
    AuditTrail.objects.create(
        user=user,
        action=action,
        model=model,
        event_category='Order Management',
        method=method.upper(),
        object_id=object_id,
        summary=summary,
    )
