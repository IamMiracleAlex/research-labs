from users.constants import ROLE_DICT
from django.contrib.auth.models import Group, Permission


def create_groups_with_permissions():
    '''
    A helper function for creating groups with assigned permissions
    [Description] To add a new group and permissions, modify the
    ROLE_DICT object in annotation.constants
    '''
    # get groups from ROLES object
    groups = ROLE_DICT.keys()

    # loop through the list to get or create a group
    for group in list(groups):
        # create or get the group
        try:
            # ensure that the group was created or gotten
            group_obj, _ = Group.objects.get_or_create(name=group)
        except Exception:
            raise ValueError(
                "Something went wrong trying to create or get a group"
            )

        # compute all permission codenames as string using the fetch_perms
        # helper function
        permissions = fetch_perms(ROLE_DICT.get(group))

        permission_models = []
        # get permission objects using the codename
        for perm_codename in permissions:
            # using pythons assignment expression (PEP 572) here to reduce
            # the number of lines of code and for a cleaner code
            if (perm := Permission.objects.filter(codename=perm_codename)):
                permission_models.append(perm.first())

        # assign the permission objects to the group
        group_obj.permissions.add(*permission_models)
        print(f"{len(permission_models)} permissions assigned to {group}")
    print("Process completed!!!")


def fetch_perms(group):
    '''helper function to generate permissions'''
    # get all permission prefixes from the group i.e. view, add etc
    _perm_prefixes = list(group.keys())
    permissions = []
    for prefix in _perm_prefixes:
        perm = ['{}_{}'.format(prefix, model) for model in group.get(prefix)]
        permissions += perm
    return permissions
