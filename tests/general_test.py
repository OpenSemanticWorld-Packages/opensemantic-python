from opensemantic import OswBaseModel
from opensemantic.v1 import OswBaseModel as OswBaseModel_v1


def test_opensemantic():

    # Create an instance of OswBaseModel
    model = OswBaseModel()

    # Check if the instance is created successfully
    assert isinstance(
        model, OswBaseModel
    ), "Failed to create an instance of OswBaseModel"

    model_v1 = OswBaseModel_v1()

    assert isinstance(
        model_v1, OswBaseModel_v1
    ), "Failed to create an instance of OswBaseModel_v1"


def test_model_instance_constructor_v2():
    """OswBaseModel(other_model, extra=...) passes through to LinkedBaseModel."""
    from oold.model import LinkedBaseModel

    class ModelA(LinkedBaseModel):
        value: float = 0.0

    class ModelB(LinkedBaseModel):
        value: float = 0.0
        extra: str = "default"

    a = ModelA(value=42.0)
    b = ModelB(a, extra="custom")
    assert b.value == 42.0
    assert b.extra == "custom"

    # Test with a subclass that has uuid (like Entity)
    class WithUuid(OswBaseModel):
        from uuid import UUID as _UUID

        uuid: _UUID = None
        value: float = 0.0

    u1 = WithUuid(value=1.0)
    u2 = WithUuid(u1, value=2.0)
    assert u2.uuid == u1.uuid
    assert u2.value == 2.0


def test_model_instance_constructor_v1():
    """OswBaseModel_v1(other_model, extra=...) passes through."""
    from oold.model.v1 import LinkedBaseModel

    class ModelA(LinkedBaseModel):
        value: float = 0.0

    class ModelB(LinkedBaseModel):
        value: float = 0.0
        extra: str = "default"

    a = ModelA(value=42.0)
    b = ModelB(a, extra="custom")
    assert b.value == 42.0
    assert b.extra == "custom"

    # Test with a subclass that has uuid
    class WithUuid(OswBaseModel_v1):
        from uuid import UUID as _UUID

        uuid: _UUID = None
        value: float = 0.0

    u1 = WithUuid(value=1.0)
    u2 = WithUuid(u1, value=2.0)
    assert u2.uuid == u1.uuid
    assert u2.value == 2.0


if __name__ == "__main__":
    test_opensemantic()
    print("All tests passed!")

    from packaging.version import Version

    # <semantic version of the source schema>.post<version of the builder>
    # schema 0.1.0, builder 0.23.1 => 0.1.0.post000023001 (release)
    # schema 0.1.0, builder 0.23.1 => 0.1.0.dev000023001 (pre-release)
    print(
        sorted(
            [
                "1.0",
                "1.0a",
                "1.0.dev",
                "1.0b",
                "1.0rc1",
                "1.0.post1",
                "1.0.post2",
                "1.0.post1.dev1",
                "1.0.post1.dev2",
                "1.0.dev2",
            ],
            key=Version,
        )
    )
    print(sorted(["0.1.0.post000023001", "0.1.0.dev000023001"], key=Version))
    print(
        sorted(
            ["0.1.0.post000023002", "0.1.0.post000023001", "0.2.0.post000023001"],
            key=Version,
        )
    )
