import os
import sys
from groq import Groq
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from rag.retriever import DocumentRetriever

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

TECHNICAL_SYSTEM_PROMPT = """You are the Technical Support Agent for TechMart Electronics customer support.

You handle login issues, account verification, installation, bugs, and feature access problems.

Guidelines:
- Be methodical -- ask for specifics that help isolate the issue
- Use the provided company policy context for accurate installation/setup answers
- Never invent system status information
- If also billing-related, note Billing is looped in
- Keep responses concise -- 2-4 sentences unless a step-by-step fix is needed
"""

class TechnicalAgent:
    def __init__(self):
        self.system_prompt = TECHNICAL_SYSTEM_PROMPT
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
            temperature=0.4,
        )
        return response.choices[0].message.content.strip()


if __name__ == "__main__":
    agent = TechnicalAgent()
    test_message = "Do I need professional installation for my TV?"
    reply = agent.handle(test_message)
    print(f"Customer: {test_message}\n")
    print(f"Technical Agent: {reply}")