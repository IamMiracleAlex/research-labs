from django.contrib import admin

from databanks.models import DataBank
from databanks.forms import DataBankAdminForm


@admin.register(DataBank)
class DataBankAdmin(admin.ModelAdmin):
    form = DataBankAdminForm
