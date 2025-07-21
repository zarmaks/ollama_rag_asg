import requests
import time
import json
from typing import Dict, Any

def test_question(question: str, use_context_injection: bool = False) -> Dict[str, Any]:
    """Test a question and measure response time."""
    url = "http://localhost:8000/ask"
    if use_context_injection:
        url += "?use_context_injection=true"
    
    data = {"question": question}
    
    start_time = time.time()
    try:
        response = requests.post(url, json=data, timeout=30)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "answer": result["answer"],
                "response_time": round(end_time - start_time, 3)
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}",
                "response_time": round(end_time - start_time, 3)
            }
    except Exception as e:
        end_time = time.time()
        return {
            "success": False,
            "error": str(e),
            "response_time": round(end_time - start_time, 3)
        }

def compare_methods():
    """Compare RAG vs Context Injection with 3 different question types."""
    
    # Test questions of varying difficulty
    questions = [
        {
            "type": "Easy - Direct FAQ",
            "question": "What is CloudSphere Platform?",
            "expected": "Should find exact match in knowledge base"
        },
        {
            "type": "Medium - Requires inference",
            "question": "How much does the cheapest plan cost and what does it include?",
            "expected": "Should combine info about Essential tier"
        },
        {
            "type": "Hard - Not in knowledge base",
            "question": "What programming languages does CloudSphere support for development?",
            "expected": "Should admit information not available"
        }
    ]
    
    print("🔍 CONTEXT INJECTION vs RAG COMPARISON")
    print("=" * 60)
    
    results = []
    
    for i, q in enumerate(questions, 1):
        print(f"\n📝 TEST {i}: {q['type']}")
        print(f"Question: {q['question']}")
        print(f"Expected: {q['expected']}")
        print("-" * 40)
        
        # Test with RAG (default)
        print("🤖 RAG Method:")
        rag_result = test_question(q['question'], use_context_injection=False)
        if rag_result['success']:
            print(f"✅ Time: {rag_result['response_time']}s")
            print(f"Answer: {rag_result['answer'][:100]}...")
        else:
            print(f"❌ Error: {rag_result['error']}")
            print(f"Time: {rag_result['response_time']}s")
        
        # Test with Context Injection
        print("\n🎯 Context Injection Method:")
        context_result = test_question(q['question'], use_context_injection=True)
        if context_result['success']:
            print(f"✅ Time: {context_result['response_time']}s")
            print(f"Answer: {context_result['answer'][:100]}...")
        else:
            print(f"❌ Error: {context_result['error']}")
            print(f"Time: {context_result['response_time']}s")
        
        # Compare times
        if rag_result['success'] and context_result['success']:
            time_diff = context_result['response_time'] - rag_result['response_time']
            if time_diff > 0:
                print(f"\n⏱️ RAG was {time_diff:.3f}s faster")
            else:
                print(f"\n⏱️ Context Injection was {abs(time_diff):.3f}s faster")
        
        # Store results
        results.append({
            "question": q,
            "rag": rag_result,
            "context_injection": context_result
        })
        
        print("\n" + "=" * 60)
    
    # Summary
    print("\n📊 SUMMARY")
    print("-" * 30)
    
    rag_times = [r['rag']['response_time'] for r in results if r['rag']['success']]
    context_times = [r['context_injection']['response_time'] for r in results if r['context_injection']['success']]
    
    if rag_times and context_times:
        avg_rag = sum(rag_times) / len(rag_times)
        avg_context = sum(context_times) / len(context_times)
        
        print(f"Average RAG Time: {avg_rag:.3f}s")
        print(f"Average Context Injection Time: {avg_context:.3f}s")
        print(f"Difference: {abs(avg_context - avg_rag):.3f}s")
        
        if avg_rag < avg_context:
            print("🏆 RAG is faster on average")
        else:
            print("🏆 Context Injection is faster on average")
    
    # Save detailed results
    with open('context_injection_comparison_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("\n💾 Detailed results saved to 'context_injection_comparison_results.json'")

if __name__ == "__main__":
    compare_methods()
