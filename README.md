# UNICEF Realm

Realm deals with Authorization only.
Authentication is considered outside the scope, and is expected it will be handled by a request to an Azure AD instance.
Any backend overriding for authentication needs to inherit from `realm.models.backends.RealmBackend`


## Objective

Create a package that handles authorization of users, that may or may not require `workspace` and/or `organization` relationships relative to the user.

Allow the following scenarios to be set by the application:

 - User Only: User object is related directly to permissions/groups
 - User and Workspace: User joined with a Workspace is related to permissions/groups
 - User, Workspace, and Organization: User joined with both a Workspace and an Organization is related to permissions/groups

The package should allow setting overrides to determine which option to be used.

eg:
AUTH_REQUIRES_ORGANIZATION = True
AUTH_REQUIRES_WORKSPACE = True


## Requirements

The following packages are being used, and so we can safely expect them to be present.
- Django
- DjangoRestFramework
- django-tenant-schemas


## Possible Option

### Django

#### Models

Create `Realm` model that is a join of `User`, `Workspace`, and `Organization` with `Workspace`, and `Organization` being nullable. Based on settings, can determine if we expect `Workspace`, and/or `Organization` is required when saved etc.
This model should have the same methods as `PermissionsMixin` class, and it is expected that this object will be used when calling `has_perms`

Overwrite `User` class, and its `PermissionsMixin` methods, to either default with error saying that `Realm` object is needed. Or add some checks if user only associated with one `Workspace`, and/or `Organization` or they are not needed then just use the `User` object, but this will probably result in duplication of code (maybe). Preference would be to fail on `User.has_perms` redirecting user to `Realm.has_users`, just makes it clearer.

Add utility `get_realm(request)` function in same vein as `get_user(request)`
Add `set_realm(request, realm)` function in same vein as `login(request, user, backend=None)`

May need to handle the helper functions for common logic between `User` and `AnonymouseUser`

- `_user_get_all_permissions`
- `_user_has_perm`
- `_user_has_module_perms`


#### Backends

Customize `ModelBackend` overwriting all the permission methods, to make use of the `Realm` object


### DjangoRestFramework

Overwrite/customize the following permission classes;

- `DjangoModelPermissions`: overwrite `has_permission` and replace `user.has_perms` calls with new custom call in Django.
- `DjangoObjectPermissions`: overwrite `has_object_permission` and replace `user.has_perms` calls with new custom call in Django

Both of these methods recieve the `request` object as a parameter, and so we can extract `Workspace` and/or `Organization` from that as and when needed, based on settings. If required and not present we can either raise `Http404` or return `False` at this point. If information is provided, we can create a `realm` object and call `has_perm` on it, that mimics the `user.has_perms`


### Django Tenant Schemas

`django-tenant-schemas` should not actually be required for this package, but since we use it, it is best to incorporate in our example to ensure no surprises.


## Testing Prototype

Using each scenario defined above in `Objective`
Using default authentication (on UserModel)

For each of the GET, OPTIONS, HEAD, POST, PUT, PATCH, and DELETE methods;

 1. Make request as anonymous user
 2. Make request as authenticated user no permissions
 3. Make request as authenticated user with direct permissions (not using group)
 4. Make request as authenticated user with group permissions
 5. Make request as authenticated user with module/object permissions


## Setup

### Settings

Add the package to your `INSTALLED_APPS`

    INSTALLED_APPS [
        ...
        'realm',
        ...
    ]

Change the authentication backend

    AUTHENTICATION_BACKEND = 'realm.backends.RealmBackend'

Add the following settings;

    AUTH_REQUIRES_ORGANIZATION = True
    AUTH_REQUIRES_WORKSPACE= True
    ORGANIZATION_MODEL = 'example.Organization'
    WORKSPACE_MODEL = 'tenant.Workspace'
