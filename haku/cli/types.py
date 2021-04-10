import re

from click import ParamType

from haku.shelf import Filter
from haku.utils import get_editor, get_editor_args


class FilterType(ParamType):
    """Filter option type"""

    name = "filter"

    def convert(self, value, param, ctx):
        return Filter.stringified(value)


class ReType(ParamType):
    """Regex type"""

    name = "regex"

    def __init__(self, *mandatory_named_groups):
        self.mandatory_named_groups = mandatory_named_groups

    def convert(self, value, param, ctx):
        try:
            compiled = re.compile(value)
        except re.error:
            return self.fail(f"{value} is not a valid regex", param, ctx)

        groups = compiled.groupindex
        mng = self.mandatory_named_groups
        groups_ok = all([group in groups for group in mng])

        if not groups_ok:
            missing = [group for group in mng if group not in groups]
            missing = f"missing required groups [{', '.join(missing)}] in {value}"
            return self.fail(missing, param, ctx)

        return compiled


class EditorType(ParamType):
    """Editor type"""

    name = "editor"

    def convert(self, value, param, ctx):
        if value.strip() == "":
            value = get_editor()

        args = get_editor_args(value)
        return " ".join([value, *args])
