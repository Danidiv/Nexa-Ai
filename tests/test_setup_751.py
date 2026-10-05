from services.completion_product_spec import build_product_spec, valid_product_spec, ProductSpec


def main():
    obj = build_product_spec(
        "sample",
        "build a customer management dashboard",
        ["login", "customers", "search"],
        ["responsive UI", "PostgreSQL"],
        ["user can log in", "customer search returns matching records"],
    )
    assert valid_product_spec(obj)
    assert obj.task_id == "sample"
    assert obj.features == ("login", "customers", "search")
    assert obj.constraints == ("responsive UI", "PostgreSQL")
    assert obj.acceptance_criteria[0] == "user can log in"
    tampered = ProductSpec(
        obj.task_id, obj.goal, obj.features, obj.constraints,
        ("tampered",) + obj.acceptance_criteria[1:], obj.digest_value
    )
    assert not valid_product_spec(tampered)
    try:
        build_product_spec("sample", "goal", [""])
    except ValueError:
        pass
    else:
        raise AssertionError("empty feature must be rejected")
    print("[PASS] Setup 7.51 Product Requirement Specification")


if __name__ == "__main__":
    main()
