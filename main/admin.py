from django.contrib import admin
from .models import TrainedModels


# Register your models here.
@admin.register(TrainedModels)
class TrainedModelsAdmin(admin.ModelAdmin):
    list_display = ['name']
    # list_filter = ['']
    # fields = ['']
    # inlines = []
    # raw_id_fields = ['']
    # readonly_fields = ['']
    # search_fields = ['']
    # ordering = ['']
