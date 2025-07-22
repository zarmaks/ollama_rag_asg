"""
RAG vs Context Injection Comparison Test για το FAQ-RAG System.

Συγκρίνει 2 διαφορετικές προσεγγίσεις:
1. Hybrid RAG (EnsembleRetriever με semantic + BM25)
2. Context Injection (όλο το knowledge base ως context)

Τρέξε το με: python rag_vs_context_injection_test.py
Βεβαιώσου ότι το Ollama τρέχει με nomic-embed-text και mistral models.
"""

import time
import json
from pathlib import Path

# Import για τη δημιουργία custom services
import sys
sys.path.append('src')

from src.parser import load_knowledge
from src.rag import FAQRAGService, ContextInjectionService


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


def load_comparison_questions():
    """Load test questions designed to compare RAG vs Context Injection."""
    return [
        {
            "question": "What is the refund policy?",
            "category": "Direct FAQ Match",
            "description": "Exact match question that exists in knowledge base",
            "expected_winner": "both",
            "difficulty": "easy"
        },
        {
            "question": "How much does the Professional plan cost?",
            "category": "Specific Information",
            "description": "Specific pricing information question",
            "expected_winner": "both", 
            "difficulty": "easy"
        },
        {
            "question": "What security measures do you have in place?",
            "category": "Conceptual Query",
            "description": "Broader security question requiring understanding",
            "expected_winner": "context_injection",
            "difficulty": "medium"
        },
        {
            "question": "I want to get my money back, how do I do that?",
            "category": "Semantic Match",
            "description": "Related to refund but phrased differently",
            "expected_winner": "rag",
            "difficulty": "medium"
        },
        {
            "question": "Can I use your service for enterprise deployment?",
            "category": "Complex Query",
            "description": "May require multiple pieces of information",
            "expected_winner": "context_injection",
            "difficulty": "hard"
        },
        {
            "question": "Can I deploy on Docker containers?",
            "category": "Unknown Information", 
            "description": "Question not answered in knowledge base",
            "expected_winner": "both",
            "difficulty": "hard"
        },
        {
            "question": "What happens if I exceed API limits?",
            "category": "Policy Question",
            "description": "Specific policy question about rate limiting",
            "expected_winner": "both",
            "difficulty": "medium"
        },
        {
            "question": "How does your pricing compare to competitors?",
            "category": "Unanswerable",
            "description": "Question requiring external knowledge", 
            "expected_winner": "both",
            "difficulty": "hard"
        }
    ]


def evaluate_answer_quality(answer: str, question: str, category: str) -> dict:
    """Evaluate the quality of an answer."""
    metrics = {
        "length": len(answer),
        "has_factual_content": False,
        "admits_uncertainty": False,
        "is_helpful": False,
        "factual_score": 0
    }
    
    answer_lower = answer.lower()
    
    # Check if it admits uncertainty appropriately
    uncertainty_phrases = [
        "i'm not sure based on our docs",
        "not sure",
        "don't know", 
        "cannot find",
        "not available"
    ]
    metrics["admits_uncertainty"] = any(phrase in answer_lower for phrase in uncertainty_phrases)
    
    # Check for factual content based on category
    factual_keywords = {
        "Direct FAQ Match": ["refund", "policy", "annual", "30 days", "prorated"],
        "Specific Information": ["professional", "plan", "cost", "price", "$", "149", "monthly"],
        "Conceptual Query": ["security", "encryption", "protection", "soc", "compliance"],
        "Semantic Match": ["refund", "cancel", "money back", "policy"],
        "Complex Query": ["enterprise", "deployment", "business", "scale"],
        "Policy Question": ["api", "rate", "limit", "quota", "throttle"],
    }
    
    category_keywords = factual_keywords.get(category, [])
    metrics["has_factual_content"] = any(keyword in answer_lower for keyword in category_keywords)
    
    # Calculate factual score (0-10)
    score = 0
    
    # Length score (0-2 points)
    if len(answer) > 100:
        score += 2
    elif len(answer) > 50:
        score += 1
    
    # Factual content (0-4 points)
    if metrics["has_factual_content"]:
        keyword_matches = sum(1 for keyword in category_keywords if keyword in answer_lower)
        score += min(4, keyword_matches * 2)
    
    # Appropriate uncertainty handling (0-3 points)
    if category in ["Unknown Information", "Unanswerable"]:
        if metrics["admits_uncertainty"]:
            score += 3  # Good - admits when it doesn't know
    else:
        if not metrics["admits_uncertainty"]:
            score += 3  # Good - confident when it should know
    
    # Helpfulness (0-1 point)
    if not answer_lower.startswith("i'm sorry") or metrics["has_factual_content"]:
        score += 1
    
    metrics["factual_score"] = score
    metrics["is_helpful"] = score >= 5
    
    return metrics


def run_comparison_test():
    """Main test comparing RAG vs Context Injection."""
    print_section("RAG vs Context Injection Comparison Test")
    
    print("🔄 Loading knowledge base...")
    try:
        docs = load_knowledge("data/knowledge_base.txt")
        print(f"✅ Loaded {len(docs)} documents from knowledge base")
    except Exception as e:
        print(f"❌ Failed to load knowledge base: {str(e)}")
        return None
    
    print("🔄 Initializing services...")
    try:
        rag_service = FAQRAGService(docs)
        context_service = ContextInjectionService(docs)
        print("✅ Both services initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize services: {str(e)}")
        return None
    
    services = {
        "Hybrid RAG": rag_service,
        "Context Injection": context_service
    }
    
    test_questions = load_comparison_questions()
    
    print(f"🔄 Testing {len(test_questions)} questions with both approaches...")
    
    results = []
    
    for i, test_case in enumerate(test_questions):
        question = test_case["question"]
        category = test_case["category"]
        difficulty = test_case["difficulty"]
        expected_winner = test_case["expected_winner"]
        
        print_subsection(f"Test {i+1}: {category} ({difficulty.upper()})")
        print(f"❓ Question: '{question}'")
        print(f"🎯 Expected Winner: {expected_winner.upper()}")
        print(f"💡 Reason: {test_case['description']}")
        
        question_results = {
            "question": question,
            "category": category,
            "difficulty": difficulty,
            "expected_winner": expected_winner,
            "methods": {}
        }
        
        for method_name, service in services.items():
            print(f"\n🔍 Testing {method_name}...")
            
            try:
                start_time = time.time()
                answer = service.answer(question)
                end_time = time.time()
                response_time = end_time - start_time
                
                # Evaluate answer quality
                quality_metrics = evaluate_answer_quality(answer, question, category)
                
                question_results["methods"][method_name] = {
                    "answer": answer,
                    "response_time": response_time,
                    "quality_metrics": quality_metrics
                }
                
                print(f"   ⏱️  Response Time: {response_time:.2f}s")
                print(f"   📊 Quality Score: {quality_metrics['factual_score']}/10")
                print(f"   📝 Answer Length: {quality_metrics['length']} chars")
                print(f"   🎯 Has Facts: {'Yes' if quality_metrics['has_factual_content'] else 'No'}")
                print(f"   🤷 Admits Uncertainty: {'Yes' if quality_metrics['admits_uncertainty'] else 'No'}")
                print(f"   💬 Answer Preview: {answer[:100]}...")
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")
                question_results["methods"][method_name] = {
                    "error": str(e)
                }
        
        results.append(question_results)
        
        # Brief pause between questions
        time.sleep(1)
    
    return results


def analyze_comparison_results(results):
    """Analyze and summarize the comparison results."""
    print_section("Comparative Analysis & Insights")
    
    if not results:
        print("❌ No results to analyze")
        return
    
    # Initialize performance tracking
    performance_stats = {
        "Hybrid RAG": {
            "wins": 0, 
            "total_time": 0, 
            "total_quality": 0, 
            "error_count": 0,
            "factual_answers": 0,
            "appropriate_uncertainty": 0
        },
        "Context Injection": {
            "wins": 0,
            "total_time": 0, 
            "total_quality": 0, 
            "error_count": 0,
            "factual_answers": 0,
            "appropriate_uncertainty": 0
        }
    }
    
    difficulty_analysis = {"easy": {}, "medium": {}, "hard": {}}
    category_analysis = {}
    
    total_questions = len(results)
    
    for result in results:
        if "methods" not in result:
            continue
            
        category = result["category"]
        difficulty = result["difficulty"]
        expected_winner = result["expected_winner"]
        
        # Initialize category analysis
        if category not in category_analysis:
            category_analysis[category] = {"rag_better": 0, "context_better": 0, "tie": 0}
        
        question_scores = {}
        
        # Analyze each method's performance
        for method_name, method_result in result["methods"].items():
            if "error" in method_result:
                performance_stats[method_name]["error_count"] += 1
                continue
                
            quality = method_result["quality_metrics"]["factual_score"]
            response_time = method_result["response_time"]
            has_facts = method_result["quality_metrics"]["has_factual_content"]
            admits_uncertainty = method_result["quality_metrics"]["admits_uncertainty"]
            
            performance_stats[method_name]["total_time"] += response_time
            performance_stats[method_name]["total_quality"] += quality
            
            if has_facts:
                performance_stats[method_name]["factual_answers"] += 1
                
            # Check if uncertainty is appropriate
            if category in ["Unknown Information", "Unanswerable"]:
                if admits_uncertainty:
                    performance_stats[method_name]["appropriate_uncertainty"] += 1
            else:
                if not admits_uncertainty:
                    performance_stats[method_name]["appropriate_uncertainty"] += 1
            
            question_scores[method_name] = quality
        
        # Determine winner for this question
        if len(question_scores) == 2:
            rag_score = question_scores.get("Hybrid RAG", 0)
            context_score = question_scores.get("Context Injection", 0)
            
            if rag_score > context_score:
                performance_stats["Hybrid RAG"]["wins"] += 1
                category_analysis[category]["rag_better"] += 1
            elif context_score > rag_score:
                performance_stats["Context Injection"]["wins"] += 1
                category_analysis[category]["context_better"] += 1
            else:
                category_analysis[category]["tie"] += 1
    
    # Print detailed analysis
    print_subsection("📊 Overall Performance Summary")
    
    print(f"Total Questions Tested: {total_questions}\n")
    
    for method_name, stats in performance_stats.items():
        successful_questions = total_questions - stats["error_count"]
        avg_time = stats["total_time"] / successful_questions if successful_questions > 0 else 0
        avg_quality = stats["total_quality"] / successful_questions if successful_questions > 0 else 0
        win_rate = (stats["wins"] / total_questions * 100) if total_questions > 0 else 0
        factual_rate = (stats["factual_answers"] / successful_questions * 100) if successful_questions > 0 else 0
        uncertainty_rate = (stats["appropriate_uncertainty"] / successful_questions * 100) if successful_questions > 0 else 0
        
        print(f"🔍 **{method_name}**:")
        print(f"   🏆 Wins: {stats['wins']}/{total_questions} ({win_rate:.1f}%)")
        print(f"   📊 Avg Quality Score: {avg_quality:.1f}/10")
        print(f"   ⏱️  Avg Response Time: {avg_time:.2f}s")
        print(f"   📈 Factual Content Rate: {factual_rate:.1f}%")
        print(f"   🎯 Appropriate Uncertainty: {uncertainty_rate:.1f}%")
        print(f"   ❌ Error Count: {stats['error_count']}")
        print(f"   ✅ Success Rate: {(successful_questions/total_questions*100):.1f}%")
        print()
    
    print_subsection("📋 Category Performance Analysis")
    
    for category, analysis in category_analysis.items():
        total_cat = analysis["rag_better"] + analysis["context_better"] + analysis["tie"]
        if total_cat > 0:
            print(f"📁 **{category}**:")
            print(f"   🤖 RAG Better: {analysis['rag_better']}/{total_cat}")
            print(f"   📚 Context Better: {analysis['context_better']}/{total_cat}")
            print(f"   🤝 Ties: {analysis['tie']}/{total_cat}")
            
            if analysis["rag_better"] > analysis["context_better"]:
                print(f"   🎯 Winner: Hybrid RAG")
            elif analysis["context_better"] > analysis["rag_better"]:
                print(f"   🎯 Winner: Context Injection")
            else:
                print(f"   🎯 Result: Even match")
            print()
    
    print_subsection("🎯 Strategic Recommendations")
    
    # Determine overall winner
    rag_wins = performance_stats["Hybrid RAG"]["wins"]
    context_wins = performance_stats["Context Injection"]["wins"]
    rag_quality = performance_stats["Hybrid RAG"]["total_quality"] / total_questions
    context_quality = performance_stats["Context Injection"]["total_quality"] / total_questions
    rag_time = performance_stats["Hybrid RAG"]["total_time"] / total_questions
    context_time = performance_stats["Context Injection"]["total_time"] / total_questions
    
    print("📊 **Key Findings:**")
    
    if rag_wins > context_wins:
        print(f"   🏆 Hybrid RAG wins more questions ({rag_wins} vs {context_wins})")
    elif context_wins > rag_wins:
        print(f"   🏆 Context Injection wins more questions ({context_wins} vs {rag_wins})")
    else:
        print(f"   🤝 Even split in wins ({rag_wins} each)")
    
    if rag_quality > context_quality:
        print(f"   📊 RAG has higher avg quality ({rag_quality:.1f} vs {context_quality:.1f})")
    else:
        print(f"   📊 Context Injection has higher avg quality ({context_quality:.1f} vs {rag_quality:.1f})")
    
    if rag_time < context_time:
        print(f"   ⚡ RAG is faster ({rag_time:.2f}s vs {context_time:.2f}s)")
    else:
        print(f"   ⚡ Context Injection is faster ({context_time:.2f}s vs {rag_time:.2f}s)")
    
    print("\n🚀 **Deployment Guidance:**")
    
    if rag_wins > context_wins and rag_quality > context_quality:
        print("   ✅ **Recommend: Hybrid RAG**")
        print("   📝 Better performance and quality overall")
    elif context_wins > rag_wins and context_quality > rag_quality:
        print("   ✅ **Recommend: Context Injection**")
        print("   📝 More comprehensive and higher quality")
    else:
        print("   ⚖️  **Recommend: Hybrid approach based on use case**")
    
    print("\n   📋 **Use Cases:**")
    print("   • Hybrid RAG: Better for specific, targeted questions")
    print("   • Context Injection: Better for complex, multi-part questions")
    print("   • Consider knowledge base size and token limits")
    print("   • Evaluate based on your specific query patterns")


def save_comparison_results(results, filename="rag_vs_context_comparison.json"):
    """Save detailed results to JSON file."""
    try:
        # Add timestamp and metadata
        output_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "test_type": "RAG vs Context Injection Comparison",
            "total_questions": len(results),
            "results": results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"💾 Detailed results saved to {filename}")
    except Exception as e:
        print(f"⚠️  Could not save results: {str(e)}")


def main():
    """Main function to run the RAG vs Context Injection comparison."""
    print("🚀 RAG vs Context Injection Comparison Test")
    print("="*80)
    print("This test compares Hybrid RAG vs Context Injection approaches")
    print("Make sure Ollama is running with nomic-embed-text and mistral models")
    
    # Check if knowledge base exists
    if not Path("data/knowledge_base.txt").exists():
        print("❌ knowledge_base.txt not found!")
        return
    
    print("\n⏸️  Press Enter to start the comparison test...")
    input()
    
    try:
        # Run the comparison test
        results = run_comparison_test()
        
        if results:
            # Analyze and summarize results
            analyze_comparison_results(results)
            
            # Save detailed results
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"rag_vs_context_results_{timestamp}.json"
            save_comparison_results(results, filename)
            
            print_section("🎉 Comparison Test Complete!")
            print("📋 Summary:")
            print("   ✅ Tested both Hybrid RAG and Context Injection approaches")
            print("   ✅ Evaluated answer quality, response time, and appropriateness")
            print("   ✅ Analyzed performance by category and difficulty")
            print("   ✅ Generated strategic recommendations")
            print(f"\n📁 Detailed results saved to {filename}")
            print("🚀 Use these insights to choose the best approach for your use case!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user.")
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
