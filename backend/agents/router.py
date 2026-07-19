import os
import sys #for path handling
import json #response parsing
from groq import Groq
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from vectorstore.faiss_store import IntentVectorStore #for intent detection
from database.memory import ConversationMemory
from agents.billing import BillingAgent
from agents.technical import TechnicalAgent
from agents.product import ProductAgent
from agents.complaint import ComplaintAgent
from agents.faq import FAQAgent

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

CATEGORY_TO_AGENT = {
    "billing_charge_dispute": "billing",
    "payment_issue": "billing",
    "refund_request": "billing",
    "order_cancellation": "billing",
    "delivery_tracking": "product",
    "technical_issue": "technical",
    "account_verification": "technical",
    "account_security": "technical",
}

AGENT_REGISTRY = {
    "billing": BillingAgent(),
    "technical": TechnicalAgent(),
    "product": ProductAgent(),
    "complaint": ComplaintAgent(),
    "faq": FAQAgent(),
}

class AgentRouter:
    def __init__(self):
        self.vector_store = IntentVectorStore()
        self.memory = ConversationMemory()

    def _decide_agents(self, message: str):
        predicted_category, matches = self.vector_store.get_top_category(message, top_k=5)
        suggested_agent = CATEGORY_TO_AGENT.get(predicted_category, "faq")

        example_matches = "\n".join([f"- {m['query']} (category: {m['category']})" for m in matches])

        prompt = f"""You are an intent routing system for TechMart Electronics customer support.

Customer message: "{message}"

Closest matches from past examples:
{example_matches}

Suggested primary agent: {suggested_agent}
Available agents: billing, technical, product, complaint, faq

Some messages need MULTIPLE agents. Respond ONLY with valid JSON:
{{"agents": ["agent1", "agent2"], "reasoning": "brief explanation"}}
"""
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )

        try:
            result = json.loads(response.choices[0].message.content.strip())
        except json.JSONDecodeError:
            result = {"agents": [suggested_agent], "reasoning": "Fallback to FAISS prediction"}

        return result.get("agents", [suggested_agent]), result.get("reasoning", ""), predicted_category

    def handle_message(self, session_id: str, message: str):
        """
        Full pipeline: decide agent(s) -> fetch history -> call agent(s) -> save -> return
        """
        agents_to_use, reasoning, category = self._decide_agents(message)

        # Save the user's message first
        self.memory.add_message(session_id, "user", message)

        # Get recent history for context (excludes the message we just added, for cleanliness)
        history = self.memory.get_history(session_id, limit=6)

        # Call each relevant agent
        responses = {}
        for agent_name in agents_to_use:
            agent = AGENT_REGISTRY.get(agent_name, AGENT_REGISTRY["faq"])
            reply = agent.handle(message, conversation_history=history)
            responses[agent_name] = reply
            self.memory.add_message(session_id, "assistant", reply, agent=agent_name)

        return {
            "agents_used": agents_to_use,
            "reasoning": reasoning,
            "predicted_category": category,
            "responses": responses
        }


if __name__ == "__main__":
    router = AgentRouter()
    result = router.handle_message("test-session-2", "I paid yesterday but Premium is still locked.")

    print(f"Agents used: {result['agents_used']}")
    print(f"Reasoning: {result['reasoning']}\n")
    for agent, reply in result["responses"].items():
        print(f"[{agent.upper()}]: {reply}\n")