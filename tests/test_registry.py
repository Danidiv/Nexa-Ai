from core.tools.defaults import create_default_registry
from core.tools.schemas import build_all_tool_schemas


def main():

    registry = create_default_registry()

    print("=" * 60)
    print("AZIZ AI TOOL REGISTRY TEST")
    print("=" * 60)

    print()
    print("Registered tools:")

    for name in registry.names():
        print(f"  - {name}")

    print()
    print(f"Total tools: {len(registry.names())}")

    print()
    print("Tool schemas:")

    schemas = build_all_tool_schemas(
        registry.all()
    )

    for schema in schemas:

        print()
        print(schema["name"])

        for argument in schema["arguments"]:

            print(
                f"  - {argument['name']} "
                f"required={argument['required']} "
                f"type={argument['type']}"
            )


if __name__ == "__main__":
    main()