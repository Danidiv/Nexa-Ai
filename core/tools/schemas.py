import inspect
from typing import Any, Callable, get_args, get_origin


def type_to_string(annotation: Any) -> str:
    """
    Convert a Python type annotation into a simple
    type name suitable for an AI tool schema.
    """

    if annotation is inspect.Parameter.empty:
        return "unknown"

    origin = get_origin(annotation)

    if origin is not None:

        args = get_args(annotation)

        if origin is list:
            return "array"

        if origin is dict:
            return "object"

        if args:
            names = [
                type_to_string(arg)
                for arg in args
            ]

            return " | ".join(names)

        return str(origin)

    if annotation is str:
        return "string"

    if annotation is int:
        return "integer"

    if annotation is float:
        return "number"

    if annotation is bool:
        return "boolean"

    if annotation is None or annotation is type(None):
        return "null"

    if annotation is Any:
        return "any"

    if isinstance(annotation, type):
        return annotation.__name__

    return str(annotation)


def build_tool_schema(
    name: str,
    function: Callable[..., Any],
) -> dict[str, Any]:
    """
    Build a tool schema from the actual Python function signature.
    """

    try:
        signature = inspect.signature(function)

    except (TypeError, ValueError):

        return {
            "name": name,
            "arguments": [],
        }

    arguments = []

    for parameter_name, parameter in signature.parameters.items():

        if parameter.kind in (
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        ):
            continue

        required = (
            parameter.default is inspect.Parameter.empty
        )

        annotation = parameter.annotation

        arguments.append(
            {
                "name": parameter_name,
                "required": required,
                "type": type_to_string(annotation),
            }
        )

    return {
        "name": name,
        "arguments": arguments,
    }


def build_all_tool_schemas(
    tools: dict[str, Callable[..., Any]],
) -> list[dict[str, Any]]:
    """
    Build schemas for all registered tools.
    """

    return [
        build_tool_schema(
            name,
            function,
        )
        for name, function in tools.items()
    ]


def build_tool_prompt(
    tools: dict[str, Callable[..., Any]],
) -> str:
    """
    Convert tool schemas into a compact prompt.
    """

    schemas = build_all_tool_schemas(tools)

    lines = []

    lines.append("AVAILABLE TOOL SIGNATURES:")
    lines.append("")

    for tool in schemas:

        lines.append(tool["name"])

        arguments = tool["arguments"]

        if not arguments:

            lines.append(
                "  arguments: none"
            )

        else:

            lines.append(
                "  arguments:"
            )

            for argument in arguments:

                required_text = (
                    "required"
                    if argument["required"]
                    else "optional"
                )

                lines.append(
                    f"    - {argument['name']} "
                    f"({required_text}, "
                    f"type={argument['type']})"
                )

        lines.append("")

    return "\n".join(lines)