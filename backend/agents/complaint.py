import os
import sys
from groq import Groq
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from rag.retriever import get_retriever
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

COMPLAINT_SYSTEM_PROMPT = """You are the Complaint Agent for TechMart Electronics customer support.

You handle dissatisfaction, escalations, and requests to speak with a manager.

Guidelines:
- Lead with genuine acknowledgment of frustration
- Never be defensive or dismissive
- Use company policy context where relevant to explain next steps accurately
- Offer a concrete next step, not just an apology
- Keep responses warm but concise -- 2-4 sentences
"""

class ComplaintAgent:
    def __init__(self):
        self.system_prompt = COMPLAINT_SYSTEM_PROMPT
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
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()


if __name__ == "__main__":
    agent = ComplaintAgent()
    test_message = "I've contacted support 3 times and nothing's fixed. I want a refund."
    reply = agent.handle(test_message)
    print(f"Customer: {test_message}\n")
    print(f"Complaint Agent: {reply}")