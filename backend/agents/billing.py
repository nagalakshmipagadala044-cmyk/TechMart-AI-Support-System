import os
import sys
from groq import Groq
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from rag.retriever import get_retriever

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

BILLING_SYSTEM_PROMPT = """You are the Billing Agent for TechMart Electronics customer support.

You handle payments, subscriptions, invoices, refunds, and order cancellations.

Guidelines:
- Be empathetic but efficient
- Ask for order/transaction ID if not provided
- Use the provided company policy context to give accurate, specific answers (return windows, refund timelines, etc.) instead of generic responses
- Never invent account-specific details (balances, transaction status)
- If also technical, note Technical Support is looped in
- Keep responses concise -- 2-4 sentences
"""

class BillingAgent:
    def __init__(self):
        self.system_prompt = BILLING_SYSTEM_PROMPT
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
    agent = BillingAgent()
    test_message = "How many days do I have to return a product?"
    reply = agent.handle(test_message)
    print(f"Customer: {test_message}\n")
    print(f"Billing Agent: {reply}")