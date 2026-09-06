from ollama import chat

MODEL_NAME = "qwen3:4b-instruct"


class LLMService:
    def __init__(self, model_name: str = MODEL_NAME):
        self.model_name = model_name

    def generate_answer(self, question: str, context: str) -> str:
        system_prompt = """
You are EvidenceAI, a document question-answering assistant.

Your job is to answer questions ONLY using the provided document evidence.

Rules:
1. Do not use outside knowledge.
2. Do not invent facts.
3. Every factual statement must have at least one citation.
4. Use the evidence labels exactly as provided, such as [1], [2], or [1][3].
5. Place citations immediately after the statement they support.
6. If the evidence does not contain enough information to answer the question,
   say exactly:
   "The document does not provide enough information to answer the question."
7. Keep the answer concise and factual.
8. Do not create citations that do not exist.
9. Do not include a separate Sources section. EvidenceAI provides sources separately.
"""

        response = chat(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": (
                        f"DOCUMENT EVIDENCE:\n\n{context}\n\n"
                        f"QUESTION:\n\n{question}"
                    ),
                },
            ],
        )

        return response.message.content.strip()