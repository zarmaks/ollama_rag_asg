"""
Simple Retrieval Comparison Test για το FAQ-RAG System.

Αυτό το script δοκιμάζει το ίδιο API endpoint με διαφορετικές ερωτήσεις 
που είναι σχεδιασμένες να δείξουν τις διαφορές μεταξύ:
1. Semantic similarity queries
2. Exact keyword matching queries  
3. Mixed/hybrid approach queries

Τρέξε το με: python simple_retrieval_test.py
"""

import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Helper για όμορφο formatting."""
    print(f"\n{'='*75}")
    print(f"  {title}")
    print(f"{'='*75}\n")


def print_subsection(title: str):
    """Helper για υποτμήματα."""
    print(f"\n{'-'*55}")
    print(f"  {title}")
    print(f"{'-'*55}")


def load_comparison_questions():
    """
    Ερωτήσεις που δοκιμάζουν διαφορετικές δυνατότητες retrieval.
    
    Κάθε ομάδα έχει:
    - Original question (όπως εμφανίζεται στο KB)
    - Semantic variants (παρόμοια έννοια, διαφορετικά λόγια)  
    - Keyword variants (ίδια keywords αλλά διαφορετικά)
    """
    return [
        {
            "topic": "Refund Policy",
            "original_kb": "What is your refund policy?",
            "tests": [
                {
                    "question": "What is your refund policy?",
                    "type": "exact_match",
                    "description": "Exact match - should find perfect answer"
                },
                {
                    "question": "refund policy details",
                    "type": "keyword_focused", 
                    "description": "Key terms present - BM25 should excel"
                },
                {
                    "question": "I want to get my money back",
                    "type": "semantic_focused",
                    "description": "Same concept, different words - semantic should excel"
                },
                {
                    "question": "Can I return my purchase and get refunded?",
                    "type": "mixed",
                    "description": "Mixed approach - both keywords and concepts"
                }
            ]
        },
        
        {
            "topic": "Authentication/Password Reset", 
            "original_kb": "I forgot my console password. How can I reset it?",
            "tests": [
                {
                    "question": "I forgot my console password. How can I reset it?",
                    "type": "exact_match",
                    "description": "Perfect match from KB"
                },
                {
                    "question": "forgot password reset console",
                    "type": "keyword_focused",
                    "description": "All key terms - keyword matching should work"
                },
                {
                    "question": "I can't remember my login credentials",
                    "type": "semantic_focused", 
                    "description": "Same problem, different phrasing - needs semantic understanding"
                },
                {
                    "question": "How do I recover access to my account?",
                    "type": "semantic_focused",
                    "description": "Conceptually similar - password recovery"
                }
            ]
        },
        
        {
            "topic": "Pricing Information",
            "original_kb": "Which products and add-ons are included in each pricing tier?",
            "tests": [
                {
                    "question": "Which products and add-ons are included in each pricing tier?",
                    "type": "exact_match", 
                    "description": "Direct KB question"
                },
                {
                    "question": "Professional pricing tier cost $149",
                    "type": "keyword_focused",
                    "description": "Specific pricing keywords"
                },
                {
                    "question": "How much does the middle plan cost?",
                    "type": "semantic_focused",
                    "description": "Conceptual reference to 'Professional' as middle tier"
                },
                {
                    "question": "What do I get with Professional subscription?",
                    "type": "mixed",
                    "description": "Specific tier + benefit inquiry"
                }
            ]
        },
        
        {
            "topic": "Security/Compliance",
            "original_kb": "What industry compliance certifications do you have?",
            "tests": [
                {
                    "question": "What industry compliance certifications do you have?",
                    "type": "exact_match",
                    "description": "Perfect KB match"
                },
                {
                    "question": "SOC 2 ISO 27001 GDPR HIPAA compliance",
                    "type": "keyword_focused", 
                    "description": "Technical acronyms - BM25 should excel"
                },
                {
                    "question": "How secure and compliant is your platform?",
                    "type": "semantic_focused",
                    "description": "Security concepts - needs understanding of relationship"
                },
                {
                    "question": "What certifications prove your data protection?",
                    "type": "mixed",
                    "description": "Combines 'certifications' keyword with security concept"
                }
            ]
        },
        
        {
            "topic": "API/Technical",
            "original_kb": "What are the API rate limits?", 
            "tests": [
                {
                    "question": "What are the API rate limits?",
                    "type": "exact_match",
                    "description": "Direct technical question"
                },
                {
                    "question": "API rate limiting 10 requests per second",
                    "type": "keyword_focused",
                    "description": "Technical terms and numbers"
                },
                {
                    "question": "How many API calls can I make?",
                    "type": "semantic_focused", 
                    "description": "Same concept, everyday language"
                },
                {
                    "question": "API throttling and request limits",
                    "type": "mixed",
                    "description": "Technical synonyms and related terms"
                }
            ]
        }
    ]


def test_question(question_data):
    """Test single question and measure response."""
    question = question_data["question"]
    question_type = question_data["type"]
    description = question_data["description"]
    
    print(f"🔍 {question_type.upper().replace('_', ' ')} Test")
    print(f"❓ Question: \"{question}\"")
    print(f"💡 Expected: {description}")
    
    try:
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/ask",
            json={"question": question},
            timeout=60
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        if response.status_code == 200:
            answer = response.json()["answer"]
            
            # Basic quality metrics
            answer_length = len(answer)
            has_specific_info = any(term in answer.lower() for term in [
                'professional', '$149', '$49', '$499', 'essential', 'enterprise',
                'soc 2', 'gdpr', 'hipaa', 'iso', 'forgot password', '14-day',
                'rate limit', '10 requests', 'refund', 'monthly', 'non-refundable'
            ])
            
            seems_confident = not any(phrase in answer.lower() for phrase in [
                "i don't know", "not sure", "cannot find", "no information",
                "i'm not certain", "unclear"
            ])
            
            print(f"✅ Response Time: {response_time:.2f}s")
            print(f"📝 Answer Length: {answer_length} characters")
            print(f"🎯 Contains Specific Info: {'Yes' if has_specific_info else 'No'}")
            print(f"🤖 Confidence Level: {'High' if seems_confident else 'Low'}")
            print(f"📄 Answer: {answer[:150]}...")
            
            return {
                "question": question,
                "type": question_type,
                "response_time": response_time,
                "answer": answer,
                "answer_length": answer_length,
                "has_specific_info": has_specific_info,
                "seems_confident": seems_confident,
                "success": True
            }
            
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            try:
                error_detail = response.json().get('detail', 'Unknown error')
                print(f"   Details: {error_detail}")
            except:
                print(f"   Raw response: {response.text[:100]}")
            
            return {
                "question": question,
                "type": question_type,
                "success": False,
                "error": f"HTTP {response.status_code}"
            }
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout: Request took longer than 60 seconds")
        return {"question": question, "type": question_type, "success": False, "error": "Timeout"}
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return {"question": question, "type": question_type, "success": False, "error": str(e)}


def run_retrieval_comparison_test():
    """Main test function."""
    print_section("Retrieval Approach Comparison Test")
    print("This test shows how different question styles perform with your current RAG setup")
    print("Results will help you understand if you need semantic, keyword, or hybrid retrieval")
    
    comparison_questions = load_comparison_questions()
    all_results = []
    
    for topic_group in comparison_questions:
        topic = topic_group["topic"]
        original_kb = topic_group["original_kb"]
        tests = topic_group["tests"]
        
        print_subsection(f"Topic: {topic}")
        print(f"📚 Original KB Question: \"{original_kb}\"")
        
        topic_results = {"topic": topic, "original_kb": original_kb, "tests": []}
        
        for i, test_case in enumerate(tests):
            print(f"\n--- Test {i+1}/4 ---")
            result = test_question(test_case)
            topic_results["tests"].append(result)
            
            # Small delay between questions
            time.sleep(1)
        
        all_results.append(topic_results)
        
        print("\n" + "="*40 + " TOPIC SUMMARY " + "="*40)
        analyze_topic_results(topic_results)
        
        input(f"\n⏸️  Press Enter to continue to next topic...")
    
    return all_results


def analyze_topic_results(topic_results):
    """Analyze results for a single topic."""
    successful_tests = [t for t in topic_results["tests"] if t.get("success", False)]
    
    if not successful_tests:
        print("❌ No successful tests for this topic")
        return
    
    print(f"📊 Analysis for {topic_results['topic']}:")
    
    # Performance by type
    type_performance = {}
    for test in successful_tests:
        test_type = test["type"]
        if test_type not in type_performance:
            type_performance[test_type] = []
        
        # Simple scoring system
        score = 0
        score += 2 if test.get("has_specific_info", False) else 0
        score += 2 if test.get("seems_confident", False) else 0
        score += 1 if test.get("response_time", 10) < 5 else 0  # Bonus for speed
        
        type_performance[test_type].append({
            "score": score,
            "response_time": test.get("response_time", 0),
            "answer_length": test.get("answer_length", 0)
        })
    
    print("\n🏆 Performance by Question Type:")
    for question_type, performances in type_performance.items():
        avg_score = sum(p["score"] for p in performances) / len(performances)
        avg_time = sum(p["response_time"] for p in performances) / len(performances)
        avg_length = sum(p["answer_length"] for p in performances) / len(performances)
        
        print(f"   {question_type.replace('_', ' ').title()}:")
        print(f"     Quality Score: {avg_score:.1f}/5")
        print(f"     Avg Time: {avg_time:.2f}s") 
        print(f"     Avg Answer Length: {avg_length:.0f} chars")


def generate_final_analysis(all_results):
    """Generate comprehensive analysis across all topics."""
    print_section("🎯 Final Analysis & Recommendations")
    
    # Collect all successful tests
    all_successful = []
    for topic in all_results:
        for test in topic["tests"]:
            if test.get("success", False):
                all_successful.append(test)
    
    if not all_successful:
        print("❌ No successful tests to analyze")
        return
    
    # Group by question type
    type_stats = {}
    for test in all_successful:
        test_type = test["type"]
        if test_type not in type_stats:
            type_stats[test_type] = {
                "count": 0,
                "total_score": 0,
                "total_time": 0,
                "total_length": 0,
                "high_confidence": 0
            }
        
        stats = type_stats[test_type]
        stats["count"] += 1
        stats["total_time"] += test.get("response_time", 0)
        stats["total_length"] += test.get("answer_length", 0)
        
        # Calculate quality score
        score = 0
        score += 2 if test.get("has_specific_info", False) else 0
        score += 2 if test.get("seems_confident", False) else 0
        score += 1 if test.get("response_time", 10) < 5 else 0
        
        stats["total_score"] += score
        if test.get("seems_confident", False):
            stats["high_confidence"] += 1
    
    print("📊 Overall Performance by Question Type:\n")
    
    best_type = None
    best_score = 0
    
    for question_type, stats in type_stats.items():
        avg_score = stats["total_score"] / stats["count"]
        avg_time = stats["total_time"] / stats["count"] 
        avg_length = stats["total_length"] / stats["count"]
        confidence_rate = (stats["high_confidence"] / stats["count"]) * 100
        
        print(f"🎯 {question_type.replace('_', ' ').upper()}:")
        print(f"   Tests: {stats['count']}")
        print(f"   Avg Quality Score: {avg_score:.1f}/5")
        print(f"   Avg Response Time: {avg_time:.2f}s")
        print(f"   Avg Answer Length: {avg_length:.0f} chars")
        print(f"   High Confidence Rate: {confidence_rate:.1f}%")
        print()
        
        if avg_score > best_score:
            best_score = avg_score
            best_type = question_type
    
    print_subsection("🎉 Key Insights")
    
    print(f"🏆 Best Performing Question Type: {best_type.replace('_', ' ').title()}")
    print(f"📈 Average Quality Score: {best_score:.1f}/5")
    
    print(f"\n💡 What this tells us about your current RAG setup:")
    
    if best_type == "exact_match":
        print("   ✅ Your system works best with exact keyword matches")
        print("   💡 Consider: You might benefit from better BM25/keyword indexing")
        
    elif best_type == "keyword_focused": 
        print("   ✅ Your system excels at keyword-based retrieval")
        print("   💡 Consider: Current setup is likely BM25-heavy, which is working well")
        
    elif best_type == "semantic_focused":
        print("   ✅ Your system handles conceptual queries very well") 
        print("   💡 Consider: Strong semantic understanding - embeddings are effective")
        
    elif best_type == "mixed":
        print("   ✅ Your system balances keywords and concepts effectively")
        print("   💡 Consider: You have a good hybrid approach working")
    
    print(f"\n🔧 Recommendations:")
    
    # Performance-based recommendations
    semantic_avg = type_stats.get("semantic_focused", {}).get("total_score", 0) / max(1, type_stats.get("semantic_focused", {}).get("count", 1))
    keyword_avg = type_stats.get("keyword_focused", {}).get("total_score", 0) / max(1, type_stats.get("keyword_focused", {}).get("count", 1)) 
    
    if semantic_avg > keyword_avg + 0.5:
        print("   🎯 Semantic search is performing well - consider emphasizing vector embeddings")
    elif keyword_avg > semantic_avg + 0.5:
        print("   🎯 Keyword search is performing well - BM25 approach is effective")
    else:
        print("   🎯 Balanced performance - hybrid approach would be ideal")
    
    print("   📚 Monitor query patterns to optimize retrieval strategy")
    print("   ⚡ Consider caching for frequently asked questions")
    print("   🔄 Test with more domain-specific queries for better insights")


def save_results(results, filename=None):
    """Save test results to JSON file."""
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"retrieval_test_results_{timestamp}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"💾 Results saved to: {filename}")
        return filename
    except Exception as e:
        print(f"⚠️  Could not save results: {str(e)}")
        return None


def check_api_availability():
    """Check if the FAQ API is available."""
    print("🔍 Checking API availability...")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        print(f"✅ API is responding (Status: {response.status_code})")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure it's running:")
        print("   uvicorn src.main:app --host 127.0.0.1 --port 8000")
        return False
        
    except Exception as e:
        print(f"❌ API check failed: {str(e)}")
        return False


def main():
    """Main execution function."""
    print("🚀 Simple Retrieval Comparison Test")
    print("="*75)
    print("This test compares how different question styles perform with your RAG system")
    print("It will help identify if your setup favors semantic, keyword, or hybrid retrieval")
    
    # Check API availability
    if not check_api_availability():
        return
    
    print(f"\n🎯 Test Structure:")
    print("   - 5 topics with 4 question variants each")
    print("   - Tests exact matches, keyword focus, semantic focus, and mixed approaches")  
    print("   - Measures response quality, speed, and confidence")
    
    print(f"\n⏸️  Press Enter to start the retrieval comparison test...")
    input()
    
    try:
        # Run the comparison test
        results = run_retrieval_comparison_test()
        
        # Generate final analysis
        generate_final_analysis(results)
        
        # Save results
        saved_file = save_results(results)
        
        print_section("🎉 Test Complete!")
        if saved_file:
            print(f"📄 Detailed results saved to: {saved_file}")
        print("Use these insights to optimize your RAG retrieval strategy!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user.")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")


if __name__ == "__main__":
    main()
