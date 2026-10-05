from core.tools.defaults import create_default_registry
from core.tools.validator import validate_tool_arguments


def test(
    registry,
    tool_name,
    arguments,
):
    """
    Run one validation test and print the result.
    """

    valid, message = validate_tool_arguments(
        tool_name,
        arguments,
        registry.all(),
    )

    status = "PASS" if valid else "REJECT"

    print(
        f"[{status}] "
        f"{tool_name}: "
        f"{message}"
    )


def main():

    print("=" * 60)
    print("AZIZ AI TOOL VALIDATION TEST")
    print("=" * 60)
    print()

    registry = create_default_registry()

    # --------------------------------------------------------
    # VALID CALL
    # --------------------------------------------------------

    test(
        registry,
        "write_file",
        {
            "path": "validator_test.txt",
            "content": "Hello Validator",
        },
    )

    # --------------------------------------------------------
    # MISSING REQUIRED ARGUMENT
    # --------------------------------------------------------

    test(
        registry,
        "write_file",
        {
            "path": "validator_test.txt",
        },
    )

    # --------------------------------------------------------
    # UNKNOWN ARGUMENT
    # --------------------------------------------------------

    test(
        registry,
        "write_file",
        {
            "path": "validator_test.txt",
            "content": "Hello",
            "wrong_parameter": "bad",
        },
    )

    # --------------------------------------------------------
    # WRONG TYPE
    # --------------------------------------------------------

    test(
        registry,
        "run_python",
        {
            "path": 123,
        },
    )

    # --------------------------------------------------------
    # VALID OPTIONAL ARGUMENT
    # --------------------------------------------------------

    test(
        registry,
        "run_python",
        {
            "path": "test.py",
            "timeout": 10,
        },
    )

    # --------------------------------------------------------
    # UNKNOWN TOOL
    # --------------------------------------------------------

    test(
        registry,
        "does_not_exist",
        {},
    )

    print()
    print("Validation tests complete.")


if __name__ == "__main__":
    main()