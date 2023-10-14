from django.apps import apps


# get all registered models in the project
# we will need them to enable us extract their permissions
_MODELS = [model.__name__.lower() for model in apps.get_models()]

# the various groups to be created and their roles
ROLE_DICT = {
    "Super Administrators": {
        "view": _MODELS,
        "delete": (model for model in _MODELS),
        "change": (model for model in _MODELS),
        "add": (model for model in _MODELS),
    },
    "Managing Engineers": {
        "view": _MODELS,
        "delete": (model for model in _MODELS),
        "change": (model for model in _MODELS),
        "add": (model for model in _MODELS),
    },
    "Premium Users": {
        "view": [
            "post",
        ],
        "delete": [],
        "change": [],
        "add": [],
    },
    # A new group with permissions goes here...
}
