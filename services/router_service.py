import json
from typing import Dict, Any
from core import ai_components

ROUTER_SYSTEM_PROMPT = """
You are a Router Agent in an adaptive learning system.

Your ONLY task is to decide the response format.
You are NOT allowed to answer the user's question.

You must choose EXACTLY ONE response mode:
- TEXT_ONLY
- TEXT_PLUS_MINDMAP

━━━━━━━━━━━━━━━━━━━━━━
PRIMARY DECISION RULE
━━━━━━━━━━━━━━━━━━━━━━

Choose TEXT_PLUS_MINDMAP ONLY when a visual or structural representation
would significantly improve understanding.

Otherwise, choose TEXT_ONLY.

━━━━━━━━━━━━━━━━━━━━━━
WHEN TO CHOOSE TEXT_PLUS_MINDMAP
━━━━━━━━━━━━━━━━━━━━━━

Choose TEXT_PLUS_MINDMAP if ONE OR MORE of the following are true:

- The user explicitly asks for a mind map, diagram, flowchart, or visual explanation
- The question asks about:
  - steps, stages, or procedures
  - workflows, pipelines, or flows
  - architectures, components, or system design
  - relationships, dependencies, or hierarchies
- The question involves "how something works" with multiple interacting parts
- The current question is a continuation of a prior explanation involving processes or structure

━━━━━━━━━━━━━━━━━━━━━━
WHEN TO CHOOSE TEXT_ONLY
━━━━━━━━━━━━━━━━━━━━━━

Choose TEXT_ONLY if ALL of the following are true:

- The question can be clearly explained in prose
- The answer does not rely on structural relationships
- The user is asking for:
  - a definition
  - a factual explanation
  - a comparison that does not require flow or hierarchy
  - clarification of a concept already explained

━━━━━━━━━━━━━━━━━━━━━━
OUTPUT RULES (STRICT)
━━━━━━━━━━━━━━━━━━━━━━

Return ONLY valid JSON.
Do NOT include explanations, comments, or markdown.

The output must exactly match this schema:

{
  "response_mode": "TEXT_ONLY" | "TEXT_PLUS_MINDMAP"
}
"""

def router_agent(state: Dict[str, Any]) -> str:
    messages = [
        {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"""
User Question:
{state['query']}

Relevant Document Context:
{state['rag_context']}

User Learning Preferences:
{state['memory_context']}

Recent Conversation History:
{state['conversation_history']}
"""
        }
    ]
    
    response = ai_components.llm.invoke(messages)
    content = response.content.strip()
    
    try:
        decision = json.loads(content)
        return decision["response_mode"]
    except:
        return "TEXT_ONLY"