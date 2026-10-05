from typing import Any, Callable


class ToolRegistry:
    """
    Central registry for Aziz AI tools.

    Responsible for:
    - registering tools
    - finding tools
    - executing tools
    - listing registered tools
    """

    def __init__(self):
        self._tools: dict[str, Callable[..., Any]] = {}

    def register(
        self,
        name: str,
        function: Callable[..., Any],
    ) -> None:
        """
        Register a Python function as an Aziz AI tool.
        """

        if name in self._tools:
            raise ValueError(
                f"Tool already registered: {name}"
            )

        self._tools[name] = function

    def get(
        self,
        name: str,
    ) -> Callable[..., Any]:
        """
        Return a registered tool.
        """

        if name not in self._tools:
            raise KeyError(
                f"Unknown tool: {name}"
            )

        return self._tools[name]

    def has(self, name: str) -> bool:
        """
        Check whether a tool exists.
        """

        return name in self._tools

    def names(self) -> list[str]:
        """
        Return all registered tool names.
        """

        return list(self._tools.keys())

    def all(self) -> dict[str, Callable[..., Any]]:
        """
        Return a copy of all registered tools.
        """

        return dict(self._tools)

    def execute(
        self,
        tool_name: str,
        arguments: dict[str, Any],
    ) -> Any:
        """
        Execute a registered tool safely.
        """

        if not self.has(tool_name):
            return (
                f"ERROR: Unknown tool: {tool_name}"
            )

        if not isinstance(arguments, dict):
            return (
                f"ERROR executing {tool_name}: "
                "arguments must be a JSON object"
            )

        try:

            tool = self.get(tool_name)

            return tool(**arguments)

        except TypeError as e:

            return (
                f"ERROR executing {tool_name}: "
                f"{e}"
            )

        except Exception as e:

            return (
                f"ERROR executing {tool_name}: "
                f"{type(e).__name__}: {e}"
            )