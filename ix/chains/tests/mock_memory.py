from typing import Dict, Any, List

from langchain.schema import BaseMemory


class MockMemory(BaseMemory):
    """
    Mock memory that returns a fixed set of values
    Used for testing only.
    """

    memory_variable: str = "memories"
    value_map: Dict[str, str] = {"chat_history": "mock memory"}
    session_id: str = "mock_session_id"
    supports_session: bool = True

    @property
    def memory_variables(self) -> List[str]:
        return list(self.value_map.keys())

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        return {self.memory_variable: self.value_map}

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        pass

    def clear(self) -> None:
        pass
