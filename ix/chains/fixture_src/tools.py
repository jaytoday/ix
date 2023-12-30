from ix.chains.fixture_src.targets import (
    CHAIN_TARGET,
)
from langchain.utilities import (
    ArxivAPIWrapper,
    BingSearchAPIWrapper,
    DuckDuckGoSearchAPIWrapper,
    GoogleSearchAPIWrapper,
    GoogleSerperAPIWrapper,
    GraphQLAPIWrapper,
    LambdaWrapper,
    PubMedAPIWrapper,
    WikipediaAPIWrapper,
    ZapierNLAWrapper,
)

from ix.api.components.types import NodeTypeField
from ix.chains.fixture_src.common import VERBOSE

NAME = {
    "name": "name",
    "type": "str",
    "default": "",
    "style": {"width": "100%"},
}

DESCRIPTION = {
    "name": "description",
    "type": "str",
    "default": "",
    "input_type": "textarea",
    "style": {"width": "100%"},
}

RETURN_DIRECT = {
    "name": "return_direct",
    "type": "boolean",
    "default": False,
}

TOOL_BASE_FIELDS = [RETURN_DIRECT, VERBOSE]

ARXIV_SEARCH = {
    "class_path": "ix.tools.arxiv.get_arxiv",
    "type": "tool",
    "name": " search",
    "description": "Tool that searches Arxiv for a given query.",
    "fields": TOOL_BASE_FIELDS
    + NodeTypeField.get_fields(
        ArxivAPIWrapper,
        include=[
            "top_k_results",
            "ARXIV_MAX_QUERY_LENGTH",
            "load_max_docs",
            "load_all_available_meta",
            "doc_content_chars_max",
        ],
    ),
}

BING_SEARCH = {
    "class_path": "ix.tools.bing.get_bing_search",
    "type": "tool",
    "name": "Bing Search",
    "description": "Tool that searches Bing for a given query.",
    "fields": TOOL_BASE_FIELDS
    + NodeTypeField.get_fields(
        BingSearchAPIWrapper,
        include=["bing_subscription_key", "bing_search_url", "k"],
        field_options={
            "bing_subscription_key": {
                "input_type": "secret",
                "secret_key": "Bing",
            },
            "bing_search_url": {
                "style": {"width": "100%"},
            },
        },
    ),
}

CHAIN_AS_TOOL = {
    "class_path": "ix.chains.tools.chain_as_tool",
    "type": "tool",
    "name": "Chain Tool",
    "description": "Tool that runs a chain. Any chain may be converted into a tool.",
    "connectors": [CHAIN_TARGET],
    "fields": [NAME, DESCRIPTION] + TOOL_BASE_FIELDS,
}

DUCK_DUCK_GO_SEARCH = {
    "class_path": "ix.tools.duckduckgo.get_ddg_search",
    "type": "tool",
    "name": "DuckDuckGo Search",
    "description": "Tool that searches DuckDuckGo for a given query.",
    "fields": TOOL_BASE_FIELDS
    + NodeTypeField.get_fields(
        DuckDuckGoSearchAPIWrapper,
        include=["k", "region", "safesearch", "time", "max_results"],
    ),
}

GOOGLE_SEARCH = {
    "class_path": "ix.tools.google.get_google_search",
    "type": "tool",
    "name": "Google Search",
    "description": "Tool that searches Google for a given query.",
    "fields": TOOL_BASE_FIELDS
    + NodeTypeField.get_fields(
        GoogleSearchAPIWrapper,
        include=["google_api_key", "google_cse_id", "k", "siterestrict"],
        field_options={
            "google_api_key": {
                "input_type": "secret",
                "secret_key": "Google Search API",
            },
            "google_cse_id": {
                "input_type": "secret",
                "secret_key": "Google Search API",
            },
        },
    ),
}

GOOGLE_SERPER = {
    "class_path": "ix.tools.google.get_google_serper",
    "type": "tool",
    "name": "Google Serper",
    "description": "Tool that searches Google for a given query.",
    "fields": TOOL_BASE_FIELDS
    + NodeTypeField.get_fields(
        GoogleSerperAPIWrapper,
        include=["k", "gl", "hl", "type", "tbs", "serper_api_key"],
        field_options={
            "serper_api_key": {
                "input_type": "secret",
                "secret_key": "Serper API",
            },
        },
    ),
}

GRAPHQL_TOOL = {
    "class_path": "ix.tools.graphql.get_graphql_tool",
    "type": "tool",
    "name": "GraphQL Tool",
    "description": "Tool that searches GraphQL for a given query.",
    "fields": TOOL_BASE_FIELDS
    + NodeTypeField.get_fields(GraphQLAPIWrapper, include=["graphql_endpoint"]),
}

LAMBDA_API = {
    "class_path": "ix.tools.lambda_api.get_lambda_api",
    "type": "tool",
    "name": "Lambda API",
    "description": "Tool that searches Lambda for a given query.",
    "fields": TOOL_BASE_FIELDS
    + NodeTypeField.get_fields(
        LambdaWrapper,
        include=["function_name", "awslambda_tool_name", "awslambda_tool_description"],
    ),
}

PUB_MED = {
    "name": "Pubmed",
    "description": "Pubmed search engine",
    "class_path": "ix.tools.pubmed.get_pubmed",
    "type": "tool",
    "fields": TOOL_BASE_FIELDS
    + NodeTypeField.get_fields(
        PubMedAPIWrapper,
        include=[
            "max_retry",
            "top_k_results",
            "ARXIV_MAX_QUERY_LENGTH",
            "doc_content_chars_max",
            "email",
        ],
    ),
}

WIKIPEDIA = {
    "name": "Wikipedia",
    "description": "Wikipedia search engine",
    "class_path": "ix.tools.wikipedia.get_wikipedia",
    "type": "tool",
    "fields": TOOL_BASE_FIELDS
    + NodeTypeField.get_fields(
        WikipediaAPIWrapper,
        include=[
            "top_k_results",
            "lang",
            "load_all_available_meta",
            "doc_content_chars_max",
        ],
    ),
}

METAPHOR_SEARCH_CLASS_PATH = "ix.tools.metaphor.get_metaphor_search"
METAPHOR_CONTENTS_CLASS_PATH = "ix.tools.metaphor.get_metaphor_contents"
METAPHOR_FIND_SIMILAR_CLASS_PATH = "ix.tools.metaphor.get_metaphor_find_similar"
METAPHOR_API_KEY = {
    "name": "metaphor_api_key",
    "label": "Metaphor API Key",
    "type": "str",
    "input_type": "secret",
    "secret_key": "Metaphor API",
    "required": True,
}
METAPHOR_SEARCH = {
    "name": "Metaphor search",
    "description": "Metaphor search queries",
    "class_path": METAPHOR_SEARCH_CLASS_PATH,
    "type": "tool",
    "fields": TOOL_BASE_FIELDS + [METAPHOR_API_KEY],
}

METAPHOR_CONTENTS = {
    "name": "Metaphor page contents",
    "description": "Metaphor page contents",
    "class_path": METAPHOR_CONTENTS_CLASS_PATH,
    "type": "tool",
    "fields": TOOL_BASE_FIELDS + [METAPHOR_API_KEY],
}

METAPHOR_SIMILAR = {
    "name": "Metaphor find similar",
    "description": "Metaphor find similar pages",
    "class_path": METAPHOR_FIND_SIMILAR_CLASS_PATH,
    "type": "tool",
    "fields": TOOL_BASE_FIELDS + [METAPHOR_API_KEY],
}


WOLFRAM = {
    "name": "Wolfram Alpha",
    "description": "Wolfram Alpha search engine for math and science",
    "class_path": "ix.tools.wolfram_alpha.get_wolfram_alpha",
    "display_type": "node",
    "type": "tool",
    "fields": TOOL_BASE_FIELDS
    + [
        {
            "name": "wolfram_alpha_app_id",
            "label": "Wolfram Alpha App ID",
            "type": "str",
            "input_type": "secret",
            "secret_key": "Wolfram Alpha API",
        },
    ],
}

ZAPIER = {
    "name": "Zapier",
    "description": "Tools for interacting with Zapier tasks",
    "class_path": "ix.tools.zapier.zapier_toolkit",
    "type": "tool",
    "fields": NodeTypeField.get_fields(
        ZapierNLAWrapper,
        include=[
            "zapier_nla_api_key",
            "zapier_nla_oauth_access_token",
            "zapier_nla_api_base",
        ],
        field_options={
            "zapier_nla_api_key": {
                "label": "API Key",
                "input_type": "secret",
                "secret_key": "Zapier NLA API",
            },
            "zapier_nla_oauth_access_token": {
                "label": "OAuth Token",
                "input_type": "secret",
                "secret_key": "Zapier NLA OAuth",
            },
            "zapier_nla_api_base": {
                "label": "API Base",
                "style": {"width": "100%"},
            },
        },
    ),
}

TOOLS = [
    ARXIV_SEARCH,
    BING_SEARCH,
    CHAIN_AS_TOOL,
    DUCK_DUCK_GO_SEARCH,
    GOOGLE_SEARCH,
    GOOGLE_SERPER,
    GRAPHQL_TOOL,
    LAMBDA_API,
    PUB_MED,
    WIKIPEDIA,
    METAPHOR_SEARCH,
    METAPHOR_CONTENTS,
    METAPHOR_SIMILAR,
    WOLFRAM,
    ZAPIER,
]
