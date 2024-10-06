import autoapi
import autoapi.documenters
from rich import print
from autoapi._objects import PythonObject


def build_signatures(object: PythonObject):
    name = object.short_name
    if hasattr(object, "constructor"):
        object = object.constructor

    sigs = [(object.obj["args"], object.obj["return_annotation"])]
    sigs.extend(object.obj["overloads"])

    for args, ret in sigs:
        arg_string = ""
        for modifier, arg_name, _, default in args:
            modifier = modifier or ""
            arg_name = arg_name or ""
            default = default or ""

            if default:
                default = "=" + default
            arg_string += f", {modifier}{arg_name}{default}"

        if arg_string:
            arg_string = arg_string[2:]

        yield f"| :sg:`{name}({arg_string})`"


class AutopgDocumenter(autoapi.documenters.AutoapiDocumenter):
    def format_signature(self, **kwargs):
        return ""

    def get_doc(self, encoding=None, ignore=1):
        if self.object.docstring:
            return super().get_doc(encoding, ignore)

        # If we don't already have docs, check if a python implementation exists of this
        # module and return its docstring if it does
        python_object = self.env.autoapi_all_objects.get(
            self.object.id.replace("pygame", "src_py"), None
        )
        if python_object is not None:
            return [python_object.docstring.splitlines()]

        return [""]

    def process_doc(self, docstrings: list[str]):
        for docstring in docstrings:
            if not docstring:
                continue

            yield f"| :sl:`{docstring[0]}`"

            if "args" in self.object.obj or hasattr(self.object, "constructor"):
                yield from build_signatures(self.object)

            yield from docstring[1:]

        yield ""


def setup(app):
    names = [
        "function",
        "property",
        "decorator",
        "class",
        "method",
        "data",
        "attribute",
        "module",
        "exception",
    ]

    for name in names:
        capitalized = name.capitalize()
        app.add_autodocumenter(
            type(
                f"Autopg{capitalized}Documenter",
                (
                    AutopgDocumenter,
                    getattr(autoapi.documenters, f"Autoapi{capitalized}Documenter"),
                ),
                {"objtype": f"pg{name}"},
            )
        )
