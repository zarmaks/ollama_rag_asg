"""
Retrieval Methods Comparison Test για το FAQ-RAG System.

Συγκρίνει 3 διαφορετικές μεθόδους retrieval:
1. Semantic Search μόνο (Vector Embeddings)
2. BM25 μόνο (Keyword Search)  
3. Hybrid (Combined/Ensemble)

Τρέξε το με: python retrieval_comparison_test.py
Βεβαιώσου ότι το Ollama τρέχει με nomic-embed-text και mistral models.
"""

import requests
import time
import json
from pathlib import Path

# Import για τη δημιουργία custom retrievers
import sys
sys.path.append('src')

from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from src.parser import load_knowledge

BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Helper για όμορφο formatting."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def print_subsection(title: str):
    """Helper για υποτμήματα."""
    print(f"\n{'-'*60}")
    print(f"  {title}")
    print(f"{'-'*60}")


class RetrievalTestService:
    """Custom service για testing διαφορετικών retrieval methods."""
    
    def __init__(self, docs, method="hybrid"):
        """
        Initialize with specific retrieval method.
        
        Args:
            docs: Parsed knowledge base documents
            method: "semantic", "bm25", or "hybrid"
        """
        self.method = method
        self.docs = docs
        
        # Initialize embeddings and LLM
        self.emb = OllamaEmbeddings(
            model="nomic-embed-text",
            base_url="http://localhost:11434"
        )
        
        self.llm = OllamaLLM(
            model="mistral",
            base_url="http://localhost:11434", 
            temperature=0.3
        )
        
        # Create retrievers based on method
        self._setup_retrievers()
        
        # Setup prompt template
        template = (
            "You are a helpful FAQ assistant.\n"
            "Based on the following Q&A pairs, answer the user's question.\n"
            "If the answer is not in the context, say so politely.\n\n"
            "Context:\n{context}\n\n"
            "Question: {query}\n\n"
            "Answer:"
        )
        self.prompt = ChatPromptTemplate.from_template(template)
        
        # Create chain
        self.chain = (
            {"context": self._get_context, "query": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
    
    def _setup_retrievers(self):
        """Setup retrievers based on method."""
        
        if self.method in ["semantic", "hybrid"]:
            # Create vector store
            self.vdb = Chroma.from_documents(
                self.docs, 
                self.emb,
                persist_directory=f"test_chroma_db_{self.method}"
            )
            self.semantic_retriever = self.vdb.as_retriever(
                search_kwargs={"k": 3}
            )
        
        if self.method in ["bm25", "hybrid"]:
            # Create BM25 retriever
            self.bm25_retriever = BM25Retriever.from_documents(
                self.docs, k=3
            )
        
        # Set primary retriever based on method
        if self.method == "semantic":
            self.retriever = self.semantic_retriever
        elif self.method == "bm25":
            self.retriever = self.bm25_retriever
        elif self.method == "hybrid":
            # Create ensemble retriever
            self.retriever = EnsembleRetriever(
                retrievers=[self.semantic_retriever, self.bm25_retriever],
                weights=[0.5, 0.5]  # Equal weight to both methods
            )
    
    def _get_context(self, inputs) -> str:
        """Get context using the configured retriever."""
        question = inputs["query"] if isinstance(inputs, dict) else str(inputs)
        docs = self.retriever.invoke(question)
        return "\n\n".join(d.page_content for d in docs)
    
    def get_raw_results(self, question: str) -> dict:
        """Get raw retrieval results without LLM processing."""
        docs = self.retriever.invoke(question)
        
        return {
            "method": self.method,
            "question": question,
            "num_results": len(docs),
            "results": [
                {
                    "content": doc.page_content,
                    "metadata": getattr(doc, 'metadata', {}),
                    "score": getattr(doc, 'score', None)
                }
                for doc in docs
            ]
        }
    
    def answer_with_context(self, question: str) -> dict:
        """Get both context and final answer."""
        # Get raw context
        context = self._get_context({"query": question})
        
        # Get LLM answer
        answer = self.chain.invoke({"query": question})
        
        return {
            "method": self.method,
            "question": question,
            "context": context,
            "answer": answer,
            "context_length": len(context)
        }


def load_test_questions():
    """Load test questions designed to test different retrieval strengths."""
    return [
        {
            "question": "What is the refund policy?",
            "category": "Direct Keyword Match",
            "description": "Should work well with BM25 (exact keyword 'refund')",
            "expected_strength": "bm25"
        },
        {
            "question": "I want to get my money back",
            "category": "Semantic Similarity",
            "description": "Should work better with semantic search (similar meaning to refund)",
            "expected_strength": "semantic"
        },
        {
            "question": "How much does Professional tier cost?",
            "category": "Mixed Keywords",
            "description": "Has specific terms, should work with both methods",
            "expected_strength": "hybrid"
        },
        {
            "question": "What security measures do you have?",
            "category": "Semantic Query",
            "description": "Related to 'data protection' - semantic should excel",
            "expected_strength": "semantic"
        },
        {
            "question": "SOC 2 compliance certification",
            "category": "Exact Technical Terms",
            "description": "Specific acronym - BM25 should excel",
            "expected_strength": "bm25"
        },
        {
            "question": "How do I troubleshoot when something goes wrong?",
            "category": "Conceptual Query",
            "description": "Related to deployment issues - semantic understanding needed",
            "expected_strength": "semantic"
        },
        {
            "question": "API rate limiting details",
            "category": "Technical Keywords",
            "description": "Specific terms - good for BM25",
            "expected_strength": "bm25"
        },
        {
            "question": "How secure is my information?",
            "category": "Security Concepts",
            "description": "Conceptual security question - semantic should help",
            "expected_strength": "semantic"
        },
        {
            "question": "forgotten password help",
            "category": "Informal Language",
            "description": "Informal phrasing vs 'forgot password' - semantic should bridge gap",
            "expected_strength": "semantic"
        },
        {
            "question": "Professional pricing 149 dollars monthly",
            "category": "Keyword Dense",
            "description": "Many exact keywords - BM25 should excel",
            "expected_strength": "bm25"
        }
    ]


def test_retrieval_comparison():
    """Main test comparing all three retrieval methods."""
    print_section("Retrieval Methods Comparison Test")
    
    print("🔄 Loading knowledge base...")
    try:
        docs = load_knowledge("knowledge_base.txt")
        print(f"✅ Loaded {len(docs)} documents from knowledge base")
    except Exception as e:
        print(f"❌ Failed to load knowledge base: {str(e)}")
        return
    
    print("🔄 Initializing retrieval services...")
    try:
        semantic_service = RetrievalTestService(docs, "semantic")
        bm25_service = RetrievalTestService(docs, "bm25")
        hybrid_service = RetrievalTestService(docs, "hybrid")
        print("✅ All retrieval services initialized")
    except Exception as e:
        print(f"❌ Failed to initialize services: {str(e)}")
        return
    
    services = {
        "Semantic Only": semantic_service,
        "BM25 Only": bm25_service,
        "Hybrid (Combined)": hybrid_service
    }
    
    test_questions = load_test_questions()
    
    print(f"🔄 Testing {len(test_questions)} questions across 3 retrieval methods...")
    
    results = []
    
    for i, test_case in enumerate(test_questions):
        question = test_case["question"]
        category = test_case["category"]
        expected_strength = test_case["expected_strength"]
        
        print_subsection(f"Test {i+1}: {category}")
        print(f"❓ Question: '{question}'")
        print(f"🎯 Expected Best Method: {expected_strength.upper()}")
        print(f"💡 Reason: {test_case['description']}")
        
        question_results = {
            "question": question,
            "category": category,
            "expected_strength": expected_strength,
            "methods": {}
        }
        
        for method_name, service in services.items():
            print(f"\n🔍 Testing {method_name}...")
            
            try:
                start_time = time.time()
                
                # Get raw retrieval results
                raw_results = service.get_raw_results(question)
                
                # Get answer with context
                full_results = service.answer_with_context(question)
                
                end_time = time.time()
                response_time = end_time - start_time
                
                question_results["methods"][method_name] = {
                    "response_time": response_time,
                    "num_results": raw_results["num_results"],
                    "context_length": full_results["context_length"],
                    "answer": full_results["answer"],
                    "context": full_results["context"][:500] + "..." if len(full_results["context"]) > 500 else full_results["context"],
                    "raw_results": raw_results["results"][:2]  # First 2 results
                }
                
                print(f"   ⏱️  Time: {response_time:.2f}s")
                print(f"   📊 Results: {raw_results['num_results']} docs")
                print(f"   📝 Context Length: {full_results['context_length']} chars")
                print(f"   🎯 Answer Preview: {full_results['answer'][:100]}...")
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                question_results["methods"][method_name] = {
                    "error": str(e)
                }
        
        results.append(question_results)
        
        # Brief pause between questions
        time.sleep(1)
    
    return results


def analyze_results(results):
    """Analyze and summarize the comparison results."""
    print_section("Results Analysis & Summary")
    
    if not results:
        print("❌ No results to analyze")
        return
    
    method_scores = {
        "Semantic Only": {"wins": 0, "total_time": 0, "error_count": 0},
        "BM25 Only": {"wins": 0, "total_time": 0, "error_count": 0},
        "Hybrid (Combined)": {"wins": 0, "total_time": 0, "error_count": 0}
    }
    
    category_analysis = {}
    
    for result in results:
        if "methods" not in result:
            continue
            
        category = result["category"]
        expected = result["expected_strength"]
        
        if category not in category_analysis:
            category_analysis[category] = {
                "expected": expected,
                "performance": {}
            }
        
        question_performance = {}
        
        # Analyze each method's performance for this question
        for method_name, method_result in result["methods"].items():
            if "error" in method_result:
                method_scores[method_name]["error_count"] += 1
                continue
                
            method_scores[method_name]["total_time"] += method_result["response_time"]
            
            # Score based on answer quality indicators
            answer = method_result.get("answer", "")
            context_length = method_result.get("context_length", 0)
            
            # Simple scoring based on answer length and context relevance
            score = 0
            if len(answer) > 50:  # Has substantial answer
                score += 2
            if context_length > 100:  # Has meaningful context
                score += 2
            if "I don't know" not in answer and "not sure" not in answer:
                score += 1
                
            question_performance[method_name] = score
        
        # Determine winner for this question
        if question_performance:
            winner = max(question_performance.items(), key=lambda x: x[1])
            method_scores[winner[0]]["wins"] += 1
            
            category_analysis[category]["performance"] = question_performance
    
    # Print summary
    print_subsection("Performance Summary")
    
    total_questions = len([r for r in results if "methods" in r])
    
    for method_name, stats in method_scores.items():
        avg_time = stats["total_time"] / total_questions if total_questions > 0 else 0
        win_rate = (stats["wins"] / total_questions * 100) if total_questions > 0 else 0
        
        print(f"📊 {method_name}:")
        print(f"   🏆 Wins: {stats['wins']}/{total_questions} ({win_rate:.1f}%)")
        print(f"   ⏱️  Avg Time: {avg_time:.2f}s")
        print(f"   ❌ Errors: {stats['error_count']}")
        print()
    
    print_subsection("Category Analysis")
    
    for category, analysis in category_analysis.items():
        print(f"📁 {category}:")
        print(f"   🎯 Expected Best: {analysis['expected'].upper()}")
        
        if analysis["performance"]:
            sorted_performance = sorted(
                analysis["performance"].items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            print("   📊 Actual Performance:")
            for method, score in sorted_performance:
                print(f"      {method}: {score}/5")
        print()
    
    # Recommendations
    print_subsection("Recommendations")
    
    best_overall = max(method_scores.items(), key=lambda x: x[1]["wins"])
    fastest = min(method_scores.items(), key=lambda x: x[1]["total_time"])
    
    print(f"🏆 Best Overall Performance: {best_overall[0]}")
    print(f"⚡ Fastest Method: {fastest[0]}")
    
    print("\n💡 Insights:")
    print("   - Semantic search excels at conceptual/similarity queries")
    print("   - BM25 excels at exact keyword matches and technical terms")
    print("   - Hybrid combines strengths but may be slower")
    print("   - Consider your query patterns when choosing approach")


def save_detailed_results(results, filename="retrieval_comparison_results.json"):
    """Save detailed results to JSON file for further analysis."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"💾 Detailed results saved to {filename}")
    except Exception as e:
        print(f"⚠️  Could not save results: {str(e)}")


def main():
    """Main function to run the retrieval comparison test."""
    print("🚀 Retrieval Methods Comparison Test")
    print("="*80)
    print("This test compares Semantic, BM25, and Hybrid retrieval methods")
    print("Make sure Ollama is running with nomic-embed-text and mistral models")
    
    # Check if knowledge base exists
    if not Path("knowledge_base.txt").exists():
        print("❌ knowledge_base.txt not found!")
        return
    
    print("\n⏸️  Press Enter to start the retrieval comparison test...")
    input()
    
    try:
        # Run the main test
        results = test_retrieval_comparison()
        
        if results:
            # Analyze and summarize results
            analyze_results(results)
            
            # Save detailed results
            save_detailed_results(results)
            
            print_section("🎉 Test Complete!")
            print("Check the generated JSON file for detailed results.")
            print("Use these insights to optimize your RAG retrieval strategy!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user.")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
