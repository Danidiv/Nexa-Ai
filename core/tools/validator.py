import inspect
from typing import Any, Callable

from .schemas import type_to_string


class ToolValidationError:
    """
    Represents a validation error without raising an exception.
    """

    def __init__(
        self,
        message: str,
    ):
        self.message = message

    def __str__(self):
        return self.message


def _is_type_compatible(
    value: Any,
    expected_type: Any,
) -> bool:
    """
    Check whether a runtime value is compatible with
    the expected Python annotation.
    """

    if expected_type is inspect.Parameter.empty:
        return True

    if expected_type is Any:
        return True

    # None / NoneType
    if expected_type is type(None):
        return value is None

    # Simple built-in types
    if expected_type is str:
        return isinstance(value, str)

    if expected_type is int:
        return isinstance(value, int) and not isinstance(value, bool)

    if expected_type is float:
        return isinstance(value, (int, float)) and not isinstance(value, bool)

    if expected_type is bool:
        return isinstance(value, bool)

    # Generic types
    origin = getattr(expected_type, "__origin__", None)

    if origin is list:
        return isinstance(value, list)

    if origin is dict:
        return isinstance(value, dict)

    # Optional / Union
    args = getattr(expected_type, "__args__", None)

    if args:
        return any(
            _is_type_compatible(
                value,
                arg,
            )
            for arg in args
        )

    # Normal classes
    try:
        return isinstance(
            value,
            expected_type,
        )

    except TypeError:
        # Unknown annotation.
        # Don't reject the tool call based on it.
        return True


def validate_tool_arguments(
    tool_name: str,
    arguments: Any,
    tools: dict[str, Callable[..., Any]],
) -> tuple[bool, str]:
    """
    Validate a model-generated tool call before execution.

    Returns:

        (True, "OK")

    or:

        (False, "ERROR: ...")
    """

    # --------------------------------------------------------
    # Tool existence
    # --------------------------------------------------------

    if tool_name not in tools:

        return (
            False,
            f"ERROR: Unknown tool: {tool_name}",
        )

    # --------------------------------------------------------
    # Arguments must be a JSON object
    # --------------------------------------------------------

    if not isinstance(arguments, dict):

        return (
            False,
            (
                f"ERROR validating {tool_name}: "
                "arguments must be a JSON object"
            ),
        )

    tool = tools[tool_name]

    try:

        signature = inspect.signature(tool)

    except (TypeError, ValueError):

        return (
            True,
            "OK",
        )

    parameters = signature.parameters

    # --------------------------------------------------------
    # Check unknown arguments
    # --------------------------------------------------------

    for argument_name in arguments:

        if argument_name not in parameters:

            return (
                False,
                (
                    f"ERROR validating {tool_name}: "
                    f"unknown argument '{argument_name}'"
                ),
            )

    # --------------------------------------------------------
    # Check required arguments
    # --------------------------------------------------------

    for parameter_name, parameter in parameters.items():

        if parameter.kind in (
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        ):
            continue

        if (
            parameter.default is inspect.Parameter.empty
            and parameter_name not in arguments
        ):

            return (
                False,
                (
                    f"ERROR validating {tool_name}: "
                    f"missing required argument "
                    f"'{parameter_name}'"
                ),
            )

    # --------------------------------------------------------
    # Check argument types
    # --------------------------------------------------------

    for parameter_name, value in arguments.items():

        parameter = parameters[parameter_name]

        if parameter.annotation is inspect.Parameter.empty:
            continue

        if not _is_type_compatible(
            value,
            parameter.annotation,
        ):

            expected = type_to_string(
                parameter.annotation
            )

            actual = type(value).__name__

            return (
                False,
                (
                    f"ERROR validating {tool_name}: "
                    f"argument '{parameter_name}' "
                    f"expected {expected}, "
                    f"got {actual}"
                ),
            )

    # --------------------------------------------------------
    # Everything is valid
    # --------------------------------------------------------

    return (
        True,
        "OK",
    )