from typing import Any, Dict, List, Optional


class ModelGateway:
    """
    Common interface for all AI model providers.

    The agent should communicate with this class instead of
    directly communicating with LM Studio/OpenAI/etc.
    """

    def chat(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ) -> str:
        raise NotImplementedError