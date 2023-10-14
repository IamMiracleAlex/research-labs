import random
from databanks.models import DataBank


def global_context(request):
    databanks = list(DataBank.objects.all())

    return {
        "databanks": random.sample(databanks, len(databanks)),
    }
