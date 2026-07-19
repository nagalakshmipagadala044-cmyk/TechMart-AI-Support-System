import os
import sys
from groq import Groq
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from rag.retriever import get_retriever

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

PRODUCT_SYSTEM_PROMPT = """You are the Product Agent for TechMart Electronics customer support.

You handle product features, pricing, availability, delivery tracking, and warranty questions.

Guidelines:
- Be helpful and knowledgeable
- Use the provided company policy context for accurate pricing/delivery/warranty answers
- Never invent specific stock levels or delivery dates you don't have
- Keep responses concise -- 2-4 sentences unless a comparison is needed
"""

class ProductAgent:
    def __init__(self):
        self.system_prompt = PRODUCT_SYSTEM_PROMPT
        self.retriever = get_retriever()

    def handle(self, message: str, conversation_history: list = None):
        context = self.retriever.get_context_string(message, top_k=3)
        augmented_prompt = f"Relevant company policy:\n{context}\n\nCustomer message: {message}"

        messages = [{"role": "system", "content": self.system_prompt}]
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": augmented_prompt})

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.4,
        )
        return response.choices[0].message.content.strip()


if __name__ == "__main__":
    agent = ProductAgent()
    test_message = "What's your price match policy?"
    reply = agent.handle(test_message)
    print(f"Customer: {test_message}\n")
    print(f"Product Agent: {reply}")