import re

def validate_citations(answer: str, source_count: int) -> str:
    citation_numbers = [
        int(number)
        for number in re.findall(r"\[(\d+)\]", answer)
    ]

    invalid_citations = [
        number
        for number in citation_numbers
        if number < 1 or number > source_count
    ]

    if invalid_citations:
        raise ValueError(
            f"LLM generated invalid citation numbers: {invalid_citations}"
        )

    return answer

class RAGService:
    def __init__(
        self,
        embedding_service,
        vector_store,
        llm_service,
    ):
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.llm_service = llm_service

    def answer_question(
        self,
        question: str,
        top_k: int = 5,
    ) -> dict:

        query_embedding = self.embedding_service.embed_query(
            question
        )

        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        if not documents:
            return {
                "answer": (
                    "I could not find relevant evidence "
                    "in the uploaded documents."
                ),
                "sources": [],
            }

        evidence_parts = []

        for index, (document, metadata) in enumerate(
            zip(documents, metadatas),
            start=1,
        ):
            source_label = f"[{index}]"

            evidence_parts.append(
                f"{source_label} "
                f"{metadata['document']} "
                f"(Page {metadata['page']}):\n"
                f"{document}"
            )

        context = "\n\n".join(evidence_parts)

        answer = self.llm_service.generate_answer(
            question=question,
            context=context,
        )

        answer = validate_citations(
            answer=answer,
            source_count=len(metadatas),
        )

        sources = []

        for index, (document, metadata) in enumerate(
            zip(documents, metadatas),
            start=1,
        ):
            sources.append(
                {
                    "id": index,
                    "document_id": metadata["document_id"],
                    "document": metadata["document"],
                    "page": metadata["page"],
                    "text": document,
                }
            )

        return {
            "answer": answer,
            "sources": sources,
            "distances": distances,
        }