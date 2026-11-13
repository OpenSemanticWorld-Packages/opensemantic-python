"""Tests for deriving the wiki page title of a Property from its name."""

import pytest


def _classes(version):
    if version == "v2":
        from opensemantic.core import AnnotationProperty, Item, QuantityProperty
    else:
        from opensemantic.core.v1 import AnnotationProperty, Item, QuantityProperty
    return AnnotationProperty, QuantityProperty, Item


LABEL = [{"text": "label"}]


@pytest.mark.parametrize("version", ["v2", "v1"])
@pytest.mark.parametrize("cls_index", [0, 1])
def test_property_title_from_name(version, cls_index):
    cls = _classes(version)[cls_index]
    prop = cls(name="HasTestValue", label=LABEL)
    assert prop.get_title() == "HasTestValue"
    assert prop.get_iri() == "Property:HasTestValue"


@pytest.mark.parametrize("version", ["v2", "v1"])
def test_property_explicit_meta_title_wins(version):
    prop_cls = _classes(version)[0]
    prop = prop_cls(
        name="HasTestValue",
        label=LABEL,
        meta={"wiki_page": {"title": "Custom"}},
    )
    assert prop.get_title() == "Custom"
    assert prop.get_iri() == "Property:Custom"


@pytest.mark.parametrize("version", ["v2", "v1"])
def test_non_property_title_is_osw_id(version):
    item_cls = _classes(version)[2]
    item = item_cls(label=LABEL, name="SomeName")
    assert item.get_title() == f"OSW{item.uuid.hex}"
    assert item.get_iri() == f"Item:OSW{item.uuid.hex}"


@pytest.mark.parametrize("version", ["v2", "v1"])
def test_property_with_empty_name_falls_back_to_osw_id(version):
    prop_cls = _classes(version)[0]
    prop = prop_cls(name="HasTestValue", label=LABEL)
    # the model rejects None as name, so an empty string is the only unset value
    prop.name = ""
    assert prop.get_title() == f"OSW{prop.uuid.hex}"
    assert prop.get_iri() == f"Property:OSW{prop.uuid.hex}"


@pytest.mark.parametrize("version", ["v2", "v1"])
def test_property_name_derived_from_label_is_used_as_title(version):
    prop_cls = _classes(version)[0]
    prop = prop_cls(label=LABEL)
    assert prop.name
    assert prop.get_title() == prop.name
