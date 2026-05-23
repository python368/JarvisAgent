
import os
from typing import AsyncGenerator, Dict, List, Optional

import google.generativeai as genai
from google.generativeai.types import GenerationConfig

from models.base_client import LLMClient
from utils.logger import logger


class GoogleClient(LLMClient):
    """
    Google Gemini API 客户端。
    """

    def __init__(self, api_key: Optional[str] = None):
        if api_key is None:
            api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.error("Google API Key 未设置。请在环境变量中设置 GOOGLE_API_KEY。")
            raise ValueError("Google API Key 未设置。")
        genai.configure(api_key=api_key)

    async def chat_completion(self, messages: List[Dict], model: str = "gemini-pro", **kwargs) -> AsyncGenerator[str, None]:
        try:
            # 将消息格式转换为 Gemini 兼容格式
            formatted_messages = []
            for message in messages:
                role = "user" if message["role"] == "user" else "model"
                formatted_messages.append({"role": role, "parts": [message["content"]]})

            # 提取 GenerationConfig 参数
            generation_config_params = {
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 0.95),
                "top_k": kwargs.get("top_k", 40),
                "max_output_tokens": kwargs.get("max_tokens", 1024),
            }
            generation_config = GenerationConfig(**generation_config_params)

            model_instance = genai.GenerativeModel(model_name=model)
            response = await model_instance.generate_content_async(
                contents=formatted_messages,
                generation_config=generation_config,
                stream=True
            )
            async for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.error(f"Google API 聊天完成时发生错误: {e}")
            raise

    async def get_available_models(self) -> List[str]:
        # 这是一个简化的示例，您可能需要根据实际情况查询 Google API 以获取可用模型列表。
        return ["gemini-pro", "gemini-pro-vision"]


