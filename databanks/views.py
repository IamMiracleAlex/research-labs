from django.views import generic

from databanks.models import DataBank
from posts.utils import get_single_random_obj


class DataBankListView(generic.ListView):
    queryset = DataBank.objects.filter(status=DataBank.PUBLISHED).order_by('-created_at')
    context_object_name = 'databanks'
    template_name = 'databanks/databank_list_new.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["featured"] = get_single_random_obj(self.get_queryset())
        return context
    


class DataBankDetailView(generic.DetailView):
    model = DataBank
    context_object_name = 'databank'
    template_name = 'databanks/databank_detail.html'
