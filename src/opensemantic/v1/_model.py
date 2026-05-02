"""
This module is to be imported in the dynamically created and updated entity.py module.
"""

from typing import TYPE_CHECKING, Literal, Optional, Type, TypeVar, Union
from uuid import UUID, uuid4

from oold.model.v1 import LinkedBaseModel
from pydantic.v1 import BaseModel, Field, constr

from opensemantic.custom_types import NoneType

T = TypeVar("T", bound=BaseModel)

# This is dirty, but required for autocompletion:
# https://stackoverflow.com/questions/62884543/pydantic-autocompletion-in-vs-code
# Ideally, solved by custom templates in the future:
# https://github.com/koxudaxi/datamodel-code-generator/issues/860
# ToDo: Still needed?

if TYPE_CHECKING:
    from dataclasses import dataclass as _basemodel_decorator
else:
    _basemodel_decorator = lambda x: x  # noqa: E731

# ToDo: from osw.utils.strings import pascal_case


def pascal_case(st: str) -> str:
    """converts a string to PascalCase

    Parameters
    ----------
    st
        the string to convert to PascalCase

    Returns
    -------
        The string in PascalCase
    """
    if not st.isalnum():
        st = "".join(x for x in st.title() if x.isalnum())
    return st[0].upper() + st[1:]


def custom_issubclass(obj: Union[type, T], class_name: str) -> bool:
    """
    Custom issubclass function that checks if the object is a subclass of a class
    with the given name.

    Parameters
    ----------
    obj : object
        The object to check.
    class_name : str
        The name of the class to check against.

    Returns
    -------
    bool
        True if the object is a subclass of the class with the given name,
        False otherwise.
    """

    def check_bases(cls, name):
        if hasattr(cls, "__name__") and cls.__name__ == name:
            return True
        if not hasattr(cls, "__bases__"):
            return False
        for base in cls.__bases__:
            if check_bases(base, name):
                return True
        return False

    return check_bases(obj, class_name)


def custom_isinstance(obj: Union[type, T], class_name: str) -> bool:
    """
    Custom isinstance function that checks if the object is an instance of a class with
    the given name.

    Parameters
    ----------
    obj : object
        The object to check.
    class_name : str
        The name of the class to check against.

    Returns
    -------
    bool
        True if the object is an instance of the class with the given name,
        False otherwise.
    """
    if not hasattr(obj, "__class__"):
        return False

    return custom_issubclass(obj.__class__, class_name)


@_basemodel_decorator
class OswBaseModel(LinkedBaseModel):

    class Config:
        """Configuration for the OswBaseModel"""

        # strict = False
        # extra = "ignore"
        # Additional fields are ignored
        validate_assignment = True
        # Ensures that the assignment of a value to a field is validated
        smart_union = True
        # To avoid unexpected coercing of types, the smart_union option is enabled
        # See: https://docs.pydantic.dev/1.10/usage/model_config/#smart-union
        # Not required in v2 as this will become the new default

    def __init__(self, **data):
        if data.get("name") is None and data.get("label"):
            label = data["label"]
            if isinstance(label, list) and len(label) > 0:
                first = label[0]
                text = first.text if hasattr(first, "text") else first.get("text")
                if text:
                    data["name"] = pascal_case(text)
        if "uuid" not in data:
            # If no uuid is provided, generate a new one
            data["uuid"] = OswBaseModel._init_uuid(**data)
        super().__init__(**data)

    @classmethod
    def get_cls_iri(cls) -> str:
        schema = {}
        # pydantic v1
        if hasattr(cls, "__config__"):
            if hasattr(cls.__config__, "schema_extra"):
                schema = cls.__config__.schema_extra

        title = schema.get("title", None)
        if title is not None and title in [
            "Entity",
            "Category",
            "Item",
            "Property",
            "AnnotationProperty",
            "ObjectProperty",
            "DataProperty",
            "QuantityProperty",
        ]:
            return "Category:" + title

        elif "uuid" in schema:
            namespace = "Category"
            osw_id = "OSW" + schema["uuid"].replace("-", "")
            iri = f"{namespace}:{osw_id}"
            return iri
        else:
            return super().get_cls_iri()

    @classmethod
    def _init_uuid(cls, **data) -> UUID:
        """Generates a random UUID for the entity if not provided during initialization.
        This method can be overridden to generate a UUID based on the data, e.g.
        for using a UUIDv5 based on the name:
        ```python
        def _get_uuid(**data) -> UUID:
            namespace_uuid = uuid.UUID("0dd6c54a-b162-4552-bab9-9942ccaf4f41")
            return uuid.uuid5(namespace_uuid, data["name"])
        ```
        """

        # default: random UUID
        return uuid4()

    def full_dict(self, **kwargs):  # extent BaseClass export function
        d = super().dict(**kwargs)
        for key in ("_osl_template", "_osl_footer"):
            if hasattr(self, key):
                d[key] = getattr(self, key)
                # Include selected private properties. note: private properties are not
                #  considered as discriminator
        return d

    # cast() and cast_none_to_default() are inherited from
    # LinkedBaseModel (oold.model.v1)

    def get_uuid(self) -> Union[str, UUID, NoneType]:
        """Getter for the attribute 'uuid' of the entity

        Returns
        -------
            The uuid as a string or None if the uuid could not be determined
        """
        return getattr(self, "uuid", None)

    def get_osw_id(self) -> Union[str, NoneType]:
        """Determines the OSW-ID based on the entity's uuid.

        Returns
        -------
            The OSW-ID as a string or None if the OSW-ID could not be determined
        """
        return get_osw_id(self)

    def get_namespace(self) -> Union[str, NoneType]:
        """Determines the wiki namespace based on the entity's type/class

        Returns
        -------
            The namespace as a string or None if the namespace could not be determined
        """
        return get_namespace(self)

    def get_title(self) -> Union[str, NoneType]:
        """Determines the wiki page title based on the entity's data

        Returns
        -------
            The title as a string or None if the title could not be determined
        """
        return get_title(self)

    def get_iri(self) -> Union[str, NoneType]:
        """Determines the IRI / wiki full title (namespace:title) based on the entity's
        data

        Returns
        -------
            The full title as a string or None if the title could not be determined.
        """
        return get_full_title(self)


def get_osw_id(entity: Union[OswBaseModel, Type[OswBaseModel]]) -> Union[str, NoneType]:
    """Determines the OSW-ID based on the entity's data - either from the entity's
    attribute 'osw_id' or 'uuid'.

    Parameters
    ----------
    entity
        The entity to determine the OSW-ID for

    Returns
    -------
        The OSW-ID as a string or None if the OSW-ID could not be determined
    """
    osw_id = getattr(entity, "osw_id", None)
    uuid = entity.get_uuid()
    from_uuid = None if uuid is None else f"OSW{str(uuid).replace('-', '')}"
    if osw_id is None:
        return from_uuid
    # For composite subobject IDs (OSW<parent>#OSW<child>), validate the child part
    osw_id_to_check = osw_id
    if "#" in osw_id:
        osw_id_to_check = osw_id.split("#", 1)[1]
    if osw_id_to_check != from_uuid:
        raise ValueError(f"OSW-ID does not match UUID: {osw_id} != {from_uuid}")
    return osw_id


def get_namespace(
    entity: Union[OswBaseModel, Type[OswBaseModel]],
) -> Union[str, NoneType]:
    """Determines the wiki namespace based on the entity's type/class

    Parameters
    ----------
    entity
        The entity to determine the namespace for

    Returns
    -------
        The namespace as a string or None if the namespace could not be determined
    """
    namespace = None

    if hasattr(entity, "meta") and entity.meta and entity.meta.wiki_page:
        if entity.meta.wiki_page.namespace:
            namespace = entity.meta.wiki_page.namespace

    if namespace is None:
        if custom_issubclass(entity, "Entity"):
            namespace = "Category"
        elif custom_isinstance(entity, "Category"):
            namespace = "Category"
        elif custom_issubclass(entity, "Characteristic"):
            namespace = "Category"
        elif custom_isinstance(entity, "Item"):
            namespace = "Item"
        elif custom_isinstance(entity, "Property"):
            namespace = "Property"
        elif custom_isinstance(entity, "WikiFile"):
            namespace = "File"

    return namespace


def get_title(entity: OswBaseModel) -> Union[str, NoneType]:
    """Determines the wiki page title based on the entity's data

    Parameters
    ----------
    entity
        the entity to determine the title for

    Returns
    -------
        the title as a string or None if the title could not be determined
    """
    title = None

    if hasattr(entity, "meta") and entity.meta and entity.meta.wiki_page:
        if entity.meta.wiki_page.title:
            title = entity.meta.wiki_page.title

    if title is None:
        title = get_osw_id(entity)

    return title


def get_full_title(entity: OswBaseModel) -> Union[str, NoneType]:
    """determines the wiki full title (namespace:title) based on the entity's data

    Parameters
    ----------
    entity
        the entity to determine the full title for

    Returns
    -------
        the full title as a string or None if the title could not be determined
    """
    namespace = get_namespace(entity)
    title = get_title(entity)
    if namespace is not None and title is not None:
        return namespace + ":" + title
    elif title is not None:
        return title


class Ontology(OswBaseModel):
    iri: str
    prefix: str
    name: str
    prefix_name: str
    link: str


class Label(OswBaseModel):
    text: constr(min_length=1) = Field(..., title="Text")
    lang: Optional[Literal["en", "de"]] = Field("en", title="Lang code")
