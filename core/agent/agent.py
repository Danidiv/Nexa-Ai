import json

from ..tools.defaults import create_default_registry
from ..tools.schemas import (
    build_all_tool_schemas,
    build_tool_prompt,
)


# ============================================================
# TOOL REGISTRY
# ============================================================

TOOL_REGISTRY = create_default_registry()


# ============================================================
# TOOL EXECUTION
# ============================================================

def execute_tool(tool_name, arguments):
    """
    Execute a registered Aziz AI tool.

    The model provides:

        {
            "action": "tool_name",
            "arguments": {
                ...
            }
        }

    The arguments are passed to the registered Python function.
    """

    return TOOL_REGISTRY.execute(
        tool_name,
        arguments,
    )


# ============================================================
# TOOL SCHEMA
# ============================================================

def get_tool_schema():
    """
    Return automatically generated schemas for all
    registered tools.
    """

    return build_all_tool_schemas(
        TOOL_REGISTRY.all()
    )


def get_tool_prompt():
    """
    Convert the registered tool schemas into a compact
    prompt that can be included in the system prompt.
    """

    return build_tool_prompt(
        TOOL_REGISTRY.all()
    )


# ============================================================
# TOOL CALL PARSER
# ============================================================

def parse_tool_call(text):
    """
    Extract the first JSON tool call from the model response.

    Supported formats:

    1. Raw JSON

    2. JSON inside ```json ... ```

    3. JSON embedded inside other text
    """

    if not isinstance(text, str):
        return None

    text = text.strip()

    if not text:
        return None

    # --------------------------------------------------------
    # First try: entire response is JSON
    # --------------------------------------------------------

    try:

        data = json.loads(text)

        if isinstance(data, dict) and "action" in data:
            return data

    except json.JSONDecodeError:
        pass

    # --------------------------------------------------------
    # Second try: JSON inside markdown code block
    # --------------------------------------------------------

    if "```json" in text:

        try:

            block = text.split(
                "```json",
                1
            )[1]

            block = block.split(
                "```",
                1
            )[0].strip()

            data = json.loads(block)

            if isinstance(data, dict) and "action" in data:
                return data

        except (
            json.JSONDecodeError,
            IndexError,
        ):
            pass

    # --------------------------------------------------------
    # Third try: find first JSON object
    # --------------------------------------------------------

    decoder = json.JSONDecoder()

    for i, char in enumerate(text):

        if char != "{":
            continue

        try:

            data, _ = decoder.raw_decode(
                text[i:]
            )

            if isinstance(data, dict) and "action" in data:
                return data

        except json.JSONDecodeError:
            continue

    return None


# ============================================================
# DEBUG / TOOL INFORMATION
# ============================================================

def print_tool_schema():
    """
    Print the currently registered tools and their schemas.
    """

    print("=" * 60)
    print("AZIZ AI TOOL SCHEMA")
    print("=" * 60)
    print()

    print(get_tool_prompt())


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    print_tool_schema()