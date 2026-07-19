import os
import sys
from groq import Groq
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from rag.retriever import DocumentRetriever

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

FAQ_SYSTEM_PROMPT = """You are the FAQ Agent for TechMart Electronics customer support.

You handle general company policy questions, account setup, and contact info.

Guidelines:
- Be direct and efficient
- Use the provided company policy context to answer accurately
- If a question belongs to a specialized agent, say so
- Keep responses short -- 1-3 sentences
"""

class FAQAgent:
    def __init__(self):
        self.system_prompt = FAQ_SYSTEM_PROMPT
        self.retriever = DocumentRetriever()

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
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()


if __name__ == "__main__":
    agent = FAQAgent()
    test_message = "What are your store hours?"
    reply = agent.handle(test_message)
    print(f"Customer: {test_message}\n")
    print(f"FAQ Agent: {reply}")