from etools_permissions.models import Permission


def prepare_permission_choices(models):
    for model in models:
        if isinstance(model, Permission):
            model._meta.get_field('user_type').choices = model.USER_TYPES
