from django.contrib import admin
from .models import Component, ComponentRelation
from .form import ComponentForm

# Register your models here.


class ComponentRelationAdminInline(admin.TabularInline):
    model = ComponentRelation
    extra = 1
    fk_name = "from_component"


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    form = ComponentForm
    inlines = (
        ComponentRelationAdminInline,
    )

    list_display = (
        "name",
        "type_tag",
        "get_number_of_parts",
    )
