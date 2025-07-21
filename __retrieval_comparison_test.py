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
        
        # Setup prompt template - Using factual FAQ prompt for better evaluation
        template = (
            "You are a factual FAQ assistant.\n"
            "Answer **only** with sentences copied verbatim from the provided CONTEXT.\n"
            "If none of the context sentences answer the question, reply exactly:\n"
            "   \"I'm not sure based on our docs.\"\n\n"
            "--------\n\n"

            "### EXAMPLE 1\n"
            "CONTEXT:\n"
            "\"Q: What is your refund policy?\n"
            "A: Annual plans may be cancelled within 30 days for a prorated refund.\"\n\n"
            "Q: What is your refund policy?\n"
            "A: Annual plans may be cancelled within 30 days for a prorated refund.\n\n"
            "--------\n\n"

            "### EXAMPLE 2\n"
            "CONTEXT:\n"
            "\"Q: How do I reset my password?\n"
            "A: Click 'Forgot password?' on the login page and follow the link.\"\n\n"
            "Q: Can I deploy on Kubernetes?\n"
            "A: I'm not sure based on our docs.\n\n"
            "--------\n\n"
            
            "### EXAMPLE 3\n"
            "CONTEXT:\n"
            "\"Q: How do I reset my password?\n"
            "A: Click 'Forgot password?' on the login page and follow the link.\"\n\n"
            "Q: Can I reset my memory card?\n"
            "A: I'm not sure based on our docs.\n\n"
            "--------\n\n"
            "### NOW\n"
            "CONTEXT:\n"
            "{context}\n\n"
            "Q: {query}\n"
            "A:"
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
            "question": "Can i deploy on Docker?",
            "category": "Deployment Query",
            "description": "Deployment-related question - no answer available in knowledge base",
            "expected_strength": "semantic"
        },
        {
            "question": "Why is the sky blue?",
            "category": "Irrelevant Query",
            "description": "Question completely unrelated to knowledge base content",
            "expected_strength": "none"
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
            
            # Enhanced scoring for better quality assessment
            answer = method_result.get("answer", "")
            context_length = method_result.get("context_length", 0)
            
            # Quality scoring based on multiple factors
            score = 0
            
            # Answer completeness (0-3 points)
            if len(answer) > 100:  # Substantial answer
                score += 3
            elif len(answer) > 50:  # Medium answer
                score += 2
            elif len(answer) > 20:  # Short answer
                score += 1
            
            # Context relevance (0-2 points)
            if context_length > 200:  # Rich context
                score += 2
            elif context_length > 50:  # Some context
                score += 1
            
            # Answer quality indicators (0-3 points)
            if "I'm not sure based on our docs" not in answer.lower():
                if "not sure" not in answer.lower() and "don't know" not in answer.lower():
                    score += 3  # Confident answer
                else:
                    score += 1  # Uncertain but trying
            else:
                score += 2  # Properly handled unknown case
            
            # Bonus for factual answers (0-2 points)
            if any(keyword in answer.lower() for keyword in ['annual', 'policy', 'security', 'soc', 'compliance']):
                score += 2  # Contains relevant facts
                
            question_performance[method_name] = score
        
        # Determine winner for this question
        if question_performance:
            winner = max(question_performance.items(), key=lambda x: x[1])
            method_scores[winner[0]]["wins"] += 1
            
            category_analysis[category]["performance"] = question_performance
    
    # Print summary
    print_subsection("Performance Summary")
    
    total_questions = len([r for r in results if "methods" in r])
    
    print(f"📊 Overall Results ({total_questions} questions tested):\n")
    
    for method_name, stats in method_scores.items():
        avg_time = stats["total_time"] / total_questions if total_questions > 0 else 0
        win_rate = (stats["wins"] / total_questions * 100) if total_questions > 0 else 0
        
        print(f"� {method_name}:")
        print(f"   🏆 Wins: {stats['wins']}/{total_questions} ({win_rate:.1f}%)")
        print(f"   ⏱️  Average Response Time: {avg_time:.2f}s")
        print(f"   ⚡ Speed Rating: {'Fast' if avg_time < 3 else 'Moderate' if avg_time < 6 else 'Slow'}")
        print(f"   ❌ Errors: {stats['error_count']}")
        print(f"   📈 Reliability: {((total_questions - stats['error_count']) / total_questions * 100):.1f}%")
        print()
    
    print_subsection("Detailed Performance Analysis")
    
    # Calculate average scores per method
    method_avg_scores = {}
    for method_name in method_scores.keys():
        total_score = 0
        scored_questions = 0
        
        for result in results:
            if "methods" not in result:
                continue
            method_result = result["methods"].get(method_name)
            if method_result and "error" not in method_result:
                # Recalculate score for analysis
                answer = method_result.get("answer", "")
                context_length = method_result.get("context_length", 0)
                
                score = 0
                if len(answer) > 100: score += 3
                elif len(answer) > 50: score += 2
                elif len(answer) > 20: score += 1
                
                if context_length > 200: score += 2
                elif context_length > 50: score += 1
                
                if "I'm not sure based on our docs" not in answer.lower():
                    if "not sure" not in answer.lower() and "don't know" not in answer.lower():
                        score += 3
                    else:
                        score += 1
                else:
                    score += 2
                
                if any(keyword in answer.lower() for keyword in ['annual', 'policy', 'security', 'soc', 'compliance']):
                    score += 2
                
                total_score += score
                scored_questions += 1
        
        method_avg_scores[method_name] = total_score / scored_questions if scored_questions > 0 else 0
    
    print("📊 Quality Scores (max 10 points):")
    for method_name, avg_score in method_avg_scores.items():
        quality_rating = "Excellent" if avg_score >= 8 else "Good" if avg_score >= 6 else "Fair" if avg_score >= 4 else "Poor"
        print(f"   {method_name}: {avg_score:.1f}/10 ({quality_rating})")
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
    
    # Enhanced Recommendations
    print_subsection("🎯 Strategic Recommendations")
    
    best_overall = max(method_scores.items(), key=lambda x: x[1]["wins"])
    fastest = min(method_scores.items(), key=lambda x: x[1]["total_time"])
    most_reliable = max(method_scores.items(), 
                       key=lambda x: (total_questions - x[1]["error_count"]))
    
    print(f"🏆 Best Overall Performance: {best_overall[0]}")
    print(f"⚡ Fastest Method: {fastest[0]} ({fastest[1]['total_time']/total_questions:.2f}s avg)")
    print(f"🛡️  Most Reliable: {most_reliable[0]} ({most_reliable[1]['error_count']} errors)")
    
    print("\n💡 Key Insights:")
    
    # Analyze patterns
    semantic_wins = method_scores["Semantic Only"]["wins"]
    bm25_wins = method_scores["BM25 Only"]["wins"] 
    hybrid_wins = method_scores["Hybrid (Combined)"]["wins"]
    
    if hybrid_wins >= max(semantic_wins, bm25_wins):
        print("   🎯 Hybrid approach shows best overall results")
        print("   📊 Combines strengths of both semantic and keyword search")
    elif semantic_wins > bm25_wins:
        print("   🧠 Semantic search dominates in this knowledge base")
        print("   📝 Conceptual understanding provides better results")
    else:
        print("   🔍 Keyword search (BM25) performs better")
        print("   📋 Exact term matching is crucial for this domain")
    
    # Time analysis
    avg_times = {name: stats["total_time"]/total_questions 
                for name, stats in method_scores.items()}
    fastest_method = min(avg_times.items(), key=lambda x: x[1])
    
    print(f"\n⏱️  Performance Characteristics:")
    print(f"   • Response times range from {min(avg_times.values()):.1f}s to {max(avg_times.values()):.1f}s")
    print(f"   • {fastest_method[0]} is fastest at {fastest_method[1]:.1f}s average")
    
    # Quality vs Speed trade-off analysis
    best_quality = max(method_avg_scores.items(), key=lambda x: x[1])
    print(f"\n🎭 Quality vs Speed Analysis:")
    print(f"   • Highest quality: {best_quality[0]} ({best_quality[1]:.1f}/10)")
    print(f"   • Speed champion: {fastest_method[0]} ({fastest_method[1]:.1f}s)")
    
    if best_quality[0] == fastest_method[0]:
        print("   ✨ Best method excels in both quality and speed!")
    else:
        print("   ⚖️  Trade-off exists between quality and speed")
    
    print("\n🚀 Deployment Recommendations:")
    print("   • Use Hybrid for best overall results and robustness")
    print("   • Use Semantic for conceptual/similarity queries")
    print("   • Use BM25 for exact keyword/technical term matching")
    print("   • Consider query patterns and response time requirements")


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
            print("📋 Summary of Changes Made:")
            print("   ✅ Updated to use factual FAQ prompt for better evaluation")
            print("   ✅ Reduced test questions to 6 representative cases")
            print("   ✅ Enhanced scoring system (0-10 points)")
            print("   ✅ Added detailed performance metrics and insights")
            print("   ✅ Improved quality vs speed analysis")
            print("   ✅ Added strategic deployment recommendations")
            print("\n📁 Check the generated JSON file for detailed results.")
            print("🚀 Use these insights to optimize your RAG retrieval strategy!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user.")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
