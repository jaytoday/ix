from typing import Dict, Any, Optional, List

from langchain.schema import BaseMemory, BaseMessage
from langchain.schema.runnable import RunnableSerializable, RunnableConfig
from langchain.schema.runnable.utils import Input, Output


class LoadMemory(RunnableSerializable[Input, Output]):
    output_key: str = "memories"
    """Output key for loaded memories. Must match the key in the memory component."""

    memory_inputs: List[str] = None
    """Keys from input to load."""

    memory: BaseMemory
    """Memory component to load from."""

    @classmethod
    def is_lc_serializable(cls) -> bool:
        """Is this class serializable?"""
        return True

    def invoke(
        self,
        input: Dict[str, Any],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ):
        memory_input = (
            {key: input.get(key, None) for key in self.memory_inputs}
            if self.memory_inputs
            else input
        )

        memories = self.memory.load_memory_variables(memory_input)
        return memories[self.output_key]


class SaveMemory(RunnableSerializable[Input, Output]):
    input_keys: List[str] = ["input"]
    """Keys from input to save memory input."""

    output_keys: List[str] = ["output"]
    """Keys from input to save as memory output."""

    memory: BaseMemory
    """Memory component instance to save to."""

    @classmethod
    def is_lc_serializable(cls) -> bool:
        """Is this class serializable?"""
        return True

    def invoke(
        self,
        input: Dict[str, Any],
        config: Optional[RunnableConfig] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        memory_inputs = {key: input.get(key, None) for key in self.input_keys}
        memory_outputs = {}
        for key in self.output_keys:
            if key in input:
                output = input[key]
                if isinstance(output, BaseMessage):
                    output = output.content
                if "content" in output:
                    output = output["content"]
                memory_outputs[key] = output

        self.memory.save_context(memory_inputs, memory_outputs)

        # no new output, pass through all inputs
        return input
