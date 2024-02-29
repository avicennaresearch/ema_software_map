import logging

from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.contrib.admin import widgets
from django.contrib.postgres.fields.array import ArrayField
from django.db.models import JSONField
from djangoql.admin import DjangoQLSearchMixin

from ema_comparison.widgets import (
    AutocompleteChoices,
    PrettyJSONWidget,
    SelectMultipleChoices,
)

logger = logging.getLogger(__name__)
admin.site.site_header = "Avicenna Research"
admin.site.site_title = "Avicenna Research"
admin.site.index_title = "Avicenna Research Administration"


def unregister_django_admin() -> None:
    if settings.DEBUG or settings.ADMIN_ALLOWED_ALL:
        logger.warning(
            "All models are available through django admin in debug mode!"
        )
        return
    models = apps.get_models()
    allowed_model = [
        apps.get_model(*i.split("."))
        for i in settings.ADMIN_ALLOWED_MODELS
        if i
    ]
    for model in models:
        try:
            if (
                model._meta.app_label not in settings.ADMIN_ALLOWED_APPS
                and model not in allowed_model
            ):
                admin.site.unregister(model)
        except admin.sites.NotRegistered:
            logger.debug(
                f"{model._meta.app_label}.{model._meta.object_name} "
                "is not registered!"
            )


class BaseAdminConfigs(DjangoQLSearchMixin):
    formfield_overrides = {
        JSONField: {
            "widget": PrettyJSONWidget({
                "monaco-editor": "true",
                "data-language": "json",
                "data-wordwrap": "on",
                "data-tabsize": "4",
                "data-minimap": "true",
            })
        },
    }

    array_choices_autocomplete_fields = ()
    display_as_charfield = ()

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if isinstance(db_field, ArrayField) and db_field.base_field.choices:
            return self.formfield_for_arrayfield_of_choices(
                db_field, request, **kwargs
            )

        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)

        if db_field.name in self.display_as_charfield:
            formfield.widget = widgets.AdminTextInputWidget()

        return formfield

    def formfield_for_arrayfield_of_choices(self, db_field, request, **kwargs):
        if db_field.name in self.array_choices_autocomplete_fields:
            kwargs["widget"] = AutocompleteChoices(
                choices=db_field.base_field.get_choices(
                    include_blank=db_field.blank, blank_choice=[("", "None")]
                )
            )
        else:
            kwargs["widget"] = SelectMultipleChoices(
                choices=db_field.base_field.get_choices(
                    include_blank=db_field.blank, blank_choice=[("", "None")]
                )
            )
        return db_field.formfield(**kwargs)


class BaseAdmin(BaseAdminConfigs, admin.ModelAdmin): ...
