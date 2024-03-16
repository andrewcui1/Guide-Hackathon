from langchain.retrievers import (
    ContextualCompressionRetriever,
)
from langchain.retrievers.document_compressors import (
    DocumentCompressorPipeline,
    EmbeddingsFilter,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS


class ContextCompressor:
    def __init__(self, documents, embeddings, max_results=5, **kwargs):
        self.max_results = max_results
        self.documents = documents
        self.kwargs = kwargs
        self.embeddings = embeddings

    def _get_contextual_retriever(self):

        #TODO we can experiment with these args
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        relevance_filter = EmbeddingsFilter(embeddings=self.embeddings, similarity_threshold=0.5)
        pipeline_compressor = DocumentCompressorPipeline(
            transformers=[relevance_filter]
        )
        print(self.documents)
        retriever = FAISS.from_documents(self.documents, self.embeddings).as_retriever()
        contextual_retriever = ContextualCompressionRetriever(
            base_compressor=pipeline_compressor, base_retriever=retriever
        )
        return contextual_retriever

    def _pretty_print_docs(self, docs, top_n):
        return f"\n".join(f"Source: {d.metadata.get('source')}\n"
                          f"Content: {d.page_content}\n"
                          for i, d in enumerate(docs) if i < top_n)

    def get_context(self, query, max_results=5):
        compressed_docs = self._get_contextual_retriever()
        relevant_docs = compressed_docs.get_relevant_documents(query)
        return self._pretty_print_docs(relevant_docs, max_results)