from decouple import config

from .base import *


if config('ENVIRONMENT') == "prod":
    from .prod import *

elif config('ENVIRONMENT') == "local":
    from .local import *

else:
    raise NotImplementedError('Make sure there is an ENVIRONMENT variable')    