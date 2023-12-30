from ix.chains.fixture_src.common import VERBOSE
from ix.chains.fixture_src.targets import LLM_TARGET, MEMORY_TARGET, PROMPT_TARGET

FUNCTION_SCHEMA = {
    "class_path": "ix.chains.functions.FunctionSchema",
    "type": "schema",
    "name": "Function Schema",
    "description": "Describes a function using json. Compatible with OpenAI",
    "fields": [
        {
            "name": "name",
            "type": "string",
            "default": "",
        },
        {
            "name": "description",
            "type": "string",
            "default": "",
        },
        {
            "name": "parameters",
            "type": "json",
            "default": "",
        },
    ],
}

FUNCTION_OUTPUT_PARSER = {
    "class_path": "ix.chains.functions.OpenAIFunctionParser",
    "type": "output_parser",
    "name": "Function Output Parser",
    "description": "Parses the output of a function",
    "fields": [
        {
            "name": "parse_json",
            "type": "boolean",
            "default": False,
        }
    ],
}

PARSE_FUNCTION_CALL_CLASS_PATH = "ix.runnable.output_parser.ParseFunctionCall"
PARSE_FUNCTION_CALL = {
    "class_path": PARSE_FUNCTION_CALL_CLASS_PATH,
    "type": "chain",
    "name": "Parse Function Call",
    "description": "Parse a function call from an AI Message",
    "fields": [],
    "connectors": [
        {
            "key": "in",
            "type": "target",
            "label": "AI Message",
            "source_type": "llm",
        },
        {
            "key": "out",
            "type": "source",
            "label": "Function Call",
            "source_type": "flow",
        },
    ],
}

FUNCTION_CALL = {
    "name": "function_call",
    "type": "string",
}

OPENAPI_CHAIN_CLASS_PATH = "ix.chains.openapi.get_openapi_chain_async"
OPENAPI_CHAIN = {
    "class_path": OPENAPI_CHAIN_CLASS_PATH,
    "type": "chain",
    "name": "OpenAPI with OpenAI Functions",
    "description": "Chain that uses OpenAI Functions to call OpenAPI endpoints.",
    "connectors": [LLM_TARGET, MEMORY_TARGET, PROMPT_TARGET],
    "fields": [
        VERBOSE,
        {
            "name": "spec",
            "type": "string",
            "label": "OpenAPI URL",
            "style": {
                "width": "500px",
            },
        },
    ],
}

OPENAI_FUNCTIONS = [
    FUNCTION_SCHEMA,
    FUNCTION_OUTPUT_PARSER,
    PARSE_FUNCTION_CALL,
    OPENAPI_CHAIN,
]
