import json
import logging
import traceback

import sqlparse
from django import forms
from django.conf import settings

logger = logging.getLogger(__name__)


class MonacoEditor:
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        attrs = {
            "monaco-editor": "true",
            "data-language": "html",
            "data-wordwrap": "off",
            "data-minimap": "false",
        }
        attrs.update(context["widget"]["attrs"])
        context["widget"]["attrs"] = attrs
        return context

    class Media:
        js = (
            "monaco_editor/monaco.config.js",
            "https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.30.1/min/vs/loader.min.js",  # noqa
        )
        css = {"screen": ("monaco_editor/monaco.custom.css",)}


class MonacoEditorWidget(MonacoEditor, forms.Textarea): ...


class RawPrettyJSONWidget(forms.Textarea):
    def format_value(self, value):
        try:
            value = json.dumps(json.loads(value), indent=4, sort_keys=True)
            # these lines will try to adjust size of TextArea to fit to content
            row_lengths = [len(r) for r in value.split("\n")]
            self.attrs["rows"] = min(max(len(row_lengths) + 2, 10), 30)
            self.attrs["cols"] = min(max(max(row_lengths) + 2, 40), 120)
            return value
        except Exception as e:
            traceback.print_exc()
            logger.warning(f"Error while formatting JSON: {e}")
            return super().format_value(value)


class RawPrettySQLWidget(forms.Textarea):
    def format_value(self, value):
        return sqlparse.format(
            value or "", reindent=True, keyword_case="upper"
        )


class PrettyJSONWidget(RawPrettyJSONWidget, MonacoEditor): ...


class PrettySQLWidget(RawPrettySQLWidget, MonacoEditor): ...


class SelectMultipleChoices(forms.SelectMultiple):
    def optgroups(self, name, value, attr=None):
        default = (None, [], 0)
        selected_options = [default]
        selected_choices = []
        has_selected = False
        if value and value[0]:
            selected_choices = value[0].split(",")
        for option_value, option_label in self.choices:
            selected = str(option_value) in selected_choices and (
                has_selected is False or self.allow_multiple_selected
            )
            has_selected |= selected
            index = len(default[1])
            subgroup = default[1]
            subgroup.append(
                self.create_option(
                    name, option_value, option_label, selected, index
                )
            )
        return selected_options


class AutocompleteChoices(SelectMultipleChoices):
    def __init__(self, attrs=None, choices=()):
        super().__init__(attrs)
        self.choices = choices

    def build_attrs(self, *args, **kwargs):
        attrs = super().build_attrs(*args, **kwargs)
        attrs.setdefault("class", "")
        class_whitespace = " " if attrs["class"] else ""
        attrs.update({
            "data-allow-clear": json.dumps(not self.is_required),
            "data-placeholder": "",
            "class": (
                f"{attrs['class']}{class_whitespace}"
                "admin-array-of-choices-autocomplete"
            ),
            "data-theme": "admin-array-of-choices-autocomplete",
        })
        return attrs

    @property
    def media(self):
        extra = "" if settings.DEBUG else ".min"
        return forms.Media(
            js=(
                f"admin/js/vendor/jquery/jquery{extra}.js",
                f"admin/js/vendor/select2/select2.full{extra}.js",
                "admin/js/jquery.init.js",
                "array-autocomplete/autocomplete.js",
            ),
            css={
                "screen": (
                    f"admin/css/vendor/select2/select2{extra}.css",
                    "admin/css/autocomplete.css",
                    "array-autocomplete/autocomplete.css",
                ),
            },
        )
