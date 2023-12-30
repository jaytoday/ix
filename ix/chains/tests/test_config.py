from abc import ABC
from enum import Enum
from typing import Literal, Optional

from langchain.chains.conversational_retrieval.base import (
    BaseConversationalRetrievalChain,
)
from langchain.chat_models.base import BaseChatModel
from langchain.llms.fireworks import Fireworks
from langchain.llms.llamacpp import LlamaCpp
from langchain.vectorstores.base import VectorStoreRetriever

import pytest
from langchain.vectorstores.chroma import Chroma
from pydantic import BaseModel, SecretStr
from ix.api.components.types import NodeTypeField, InputType


class ChoicesEnum(str, Enum):
    CPP = "cpp"
    GO = "go"


class MockModel(BaseModel):
    field1: str
    field2: int
    field3: bool = False
    literal: Literal["foo", "bar"] = "bar"
    field_with_default: str = "default"
    optional: Optional[str] = None
    choices_enum: ChoicesEnum
    secret_key: Optional[SecretStr] = None

    @classmethod
    def loader(
        cls,
        choices_enum: ChoicesEnum,
        field1: str,
        field2: int,
        field3: bool = False,
        field_with_default: str = "default",
        literal: Literal["foo", "bar"] = "bar",
        optional: Optional[str] = None,
    ):
        pass


class TestABC(ABC):
    field1: str
    field2: int
    field3: bool = False
    field_with_default: str = "default"
    literal: Literal["foo", "bar"] = "bar"
    optional: Optional[str] = None
    choices_enum: ChoicesEnum


@pytest.fixture
def field_overrides():
    return {
        "field1": {
            "name": "field1",
            "label": "Custom Field 1",
            "type": "str",
            "default": "custom_default",
        }
    }


@pytest.fixture
def valid_field_config():
    return {
        "name": "test_field",
        "label": "Test Field",
        "type": "int",
        "default": 0,
        "required": True,
    }


class TestFieldConfig:
    def test_slider_without_min_max(self, valid_field_config):
        valid_field_config["input_type"] = InputType.SLIDER
        with pytest.raises(
            ValueError, match="'min' and 'max' are required for 'SLIDER' input type."
        ):
            NodeTypeField(**valid_field_config)

    def test_select_without_choices(self, valid_field_config):
        valid_field_config["input_type"] = InputType.SELECT
        with pytest.raises(
            ValueError, match="'choices' are required for 'SELECT' input type."
        ):
            NodeTypeField(**valid_field_config)

    def test_slider_without_step(self, valid_field_config):
        valid_field_config["input_type"] = InputType.SLIDER
        valid_field_config["min"] = 0
        valid_field_config["max"] = 100
        with pytest.raises(
            ValueError, match="'step' is required for 'SLIDER' input type."
        ):
            NodeTypeField(**valid_field_config)


class GetFieldsBase:
    """Base for common tests for getting fields from a model or method"""

    field_source = None

    def test_field_kwargs(self, field_overrides):
        """field options may be passed as kwargs."""
        fields = NodeTypeField.get_fields(
            self.field_source,
            **field_overrides,
        )
        field = fields[0]
        assert field["name"] == "field1"

    def test_field_with_default(self, field_overrides):
        fields = NodeTypeField.get_fields(
            self.field_source,
            include=["field_with_default"],
            field_options=field_overrides,
        )

        field = fields[0] if fields[0]["name"] == "field_with_default" else fields[1]
        assert field["default"] == "default"

    def test_get_literal_field(self, field_overrides):
        fields = NodeTypeField.get_fields(
            self.field_source,
            include=["literal"],
            field_options=field_overrides,
        )

        field = fields[0] if fields[0]["name"] == "literal" else fields[1]
        assert field["choices"] == [
            {"value": "foo", "label": "Foo"},
            {"value": "bar", "label": "Bar"},
        ]

    def test_get_fields_overrides_include(self, field_overrides):
        expected_fields_include = [
            NodeTypeField(
                name="field1",
                label="Custom Field 1",
                type="str",
                default="custom_default",
                required=True,
            ).model_dump(),
            NodeTypeField(
                name="field2", label="Field2", type="int", default=None, required=True
            ).model_dump(),
        ]

        assert (
            NodeTypeField.get_fields(
                self.field_source,
                include=["field1", "field2"],
                field_options=field_overrides,
            )
            == expected_fields_include
        )

    def test_get_fields_literal(self, field_overrides):
        expected = [
            NodeTypeField(
                name="literal",
                label="Literal",
                type="str",
                input_type="select",
                default="bar",
                required=False,
                choices=[
                    {"value": "foo", "label": "Foo"},
                    {"value": "bar", "label": "Bar"},
                ],
            ).model_dump(),
        ]

        assert (
            NodeTypeField.get_fields(
                self.field_source,
                include=["literal"],
            )
            == expected
        )

    def test_get_fields_optional(self, field_overrides):
        expected = [
            NodeTypeField(
                name="optional",
                label="Optional",
                default=None,
                type="str",
                required=False,
            ).model_dump(),
        ]

        assert (
            NodeTypeField.get_fields(
                self.field_source,
                include=["optional"],
            )
            == expected
        )

    def test_get_fields_overrides_exclude(self, field_overrides):
        expected_fields_exclude = [
            NodeTypeField(
                name="field2", label="Field2", type="int", default=None, required=True
            ).model_dump(),
            NodeTypeField(
                name="field3",
                label="Field3",
                type="boolean",
                default=False,
                required=False,
            ).model_dump(),
        ]

        assert (
            NodeTypeField.get_fields(
                self.field_source,
                include=["field1", "field2", "field3"],
                exclude=["field1"],
                field_options=field_overrides,
            )
            == expected_fields_exclude
        )

    def test_get_enum_choices(self, field_overrides):
        expected = [
            NodeTypeField(
                name="choices_enum",
                label="Choices_enum",
                default=None,
                type="str",
                input_type="select",
                required=True,
                choices=[
                    {"label": "CPP", "value": "cpp"},
                    {"label": "GO", "value": "go"},
                ],
            ).model_dump(),
        ]

        fields = NodeTypeField.get_fields(
            self.field_source,
            include=["choices_enum"],
        )
        assert fields == expected


class TestGetFieldsFromModel(GetFieldsBase):
    field_source = MockModel

    def test_exclude_non_allowed_type(self, field_overrides):
        # Extend TestModel with a field of non-allowed type
        class TestModel2(BaseModel):
            field1: str
            field2: int
            field3: bool = False
            field4: MockModel  # non-allowed type

        expected_fields = [
            NodeTypeField(
                name="field1", label="Field1", type="str", default=None, required=True
            ).model_dump(),
            NodeTypeField(
                name="field2", label="Field2", type="int", default=None, required=True
            ).model_dump(),
        ]

        assert (
            NodeTypeField.get_fields(TestModel2, include=["field1", "field2", "field4"])
            == expected_fields
        )

    def test_secret(self):
        actual = NodeTypeField.get_fields(
            MockModel,
            include=["secret_key"],
        )
        expected = [
            NodeTypeField(
                name="secret_key",
                label="Secret_key",
                type="str",
                required=False,
                input_type="secret",
                secret_key=None,
            ).model_dump()
        ]
        assert actual == expected


class TestGetFieldsFromMethod(GetFieldsBase):
    field_source = MockModel.loader


class TestGetFieldsFromABC(GetFieldsBase):
    field_source = TestABC


class TestTroubleCases:
    def test_default_string(self):
        """
        Defaults weren't being detected properly for
        pydantic v1 models.
        """
        fields = NodeTypeField.get_fields(
            VectorStoreRetriever,
            include=[
                "search_type",
            ],
        )

        assert fields[0]["default"] == "similarity"

    def test_checkbox(self):
        """Checkbox wasn't being detected properly.

        input_field needs to be optional for boolean fields to
        default to checkbox because it's handled in the UI
        """
        fields = NodeTypeField.get_fields(
            BaseChatModel,
            include=[
                "verbose",
            ],
        )
        assert fields[0]["type"] == "bool"
        assert fields[0]["input_type"] is None

    def test_optional_str(self):
        """Testing Optional[str] field from Chroma.__init__"""
        actual = NodeTypeField.get_fields(
            Chroma.__init__,
            include=[
                "persist_directory",
            ],
        )

        assert actual[0]["required"] is False
        assert actual[0]["default"] is None
        assert actual[0]["type"] == "str"

    def test_optional_bool(self):
        """Testing Optional[bool] field from BaseConversationalRetrievalChain"""
        actual = NodeTypeField.get_fields(
            BaseConversationalRetrievalChain,
            include=[
                "rephrase_question",
            ],
        )
        assert actual[0]["required"] is False
        assert actual[0]["default"] is True
        assert actual[0]["type"] == "bool"

    def test_optional_int(self):
        """Testing Optional[int] field from LlamaCpp"""
        actual = NodeTypeField.get_fields(
            LlamaCpp,
            include=[
                "top_k",
            ],
        )
        assert actual[0]["required"] is False
        assert actual[0]["default"] == 40
        assert actual[0]["type"] == "int"

    def test_optional_list(self):
        """Testing Optional[List[str]] field from LlamaCpp"""
        actual = NodeTypeField.get_fields(
            LlamaCpp,
            include=[
                "stop",
            ],
        )
        assert actual[0]["required"] is False
        assert actual[0]["default"] == []
        assert actual[0]["type"] == "list"

    def test_secret_str(self):
        fields = NodeTypeField.get_fields(
            Fireworks,
            include=["fireworks_api_key"],
            field_options={
                "fireworks_api_key": {
                    "input_type": "secret",
                    "secret_key": "Fireworks.ai API",
                    "style": {"width": "100%"},
                },
            },
        )

        assert fields[0]["type"] == "str", fields[0]
        assert fields[0]["input_type"] == "secret", fields[0]
        assert fields[0]["secret_key"] == "Fireworks.ai API", fields[0]
