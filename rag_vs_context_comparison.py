#!/usr/bin/env python3
"""
Simple comparison between RAG and Context Injection methods
"""
import requests
import time
import json

def test_method(question, use_context_injection=False):
    """Test a single question with specified method"""
    url = f"http://localhost:8000/ask"
    params = {"use_context_injection": use_context_injection} if use_context_injection else {}
    
    start_time = time.time()
    try:
        response = requests.post(
            url, 
            json={"question": question},
            params=params,
            timeout=120  # 2 minutes timeout
        )
        end_time = time.time()
        
        if response.status_code == 200:
            return {
                "success": True,
                "answer": response.json()["answer"],
                "time": end_time - start_time,
                "method": "Context Injection" if use_context_injection else "RAG"
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}",
                "time": end_time - start_time,
                "method": "Context Injection" if use_context_injection else "RAG"
            }
    except Exception as e:
        end_time = time.time()
        return {
            "success": False,
            "error": str(e),
            "time": end_time - start_time,
            "method": "Context Injection" if use_context_injection else "RAG"
        }

def main():
    questions = [
        "What is CloudSphere Platform?",  # Easy - exact match
        "How much does the cheapest plan cost and what does it include?",  # Medium - needs synthesis  
        "What programming languages does CloudSphere support for development?"  # Hard - not in knowledge base
    ]
    
    results = []
    
    for i, question in enumerate(questions, 1):
        print(f"\n=== Question {i}: {question} ===")
        
        # Test RAG method
        print("Testing RAG method...")
        rag_result = test_method(question, use_context_injection=False)
        results.append({**rag_result, "question": question})
        
        if rag_result["success"]:
            print(f"✅ RAG: {rag_result['time']:.2f}s")
            print(f"Answer: {rag_result['answer'][:100]}...")
        else:
            print(f"❌ RAG: {rag_result['error']}")
        
        # Test Context Injection method
        print("Testing Context Injection method...")
        context_result = test_method(question, use_context_injection=True)
        results.append({**context_result, "question": question})
        
        if context_result["success"]:
            print(f"✅ Context Injection: {context_result['time']:.2f}s")
            print(f"Answer: {context_result['answer'][:100]}...")
        else:
            print(f"❌ Context Injection: {context_result['error']}")
        
        print(f"{'='*60}")
    
    # Save results
    with open("comparison_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📊 Results saved to comparison_results.json")
    
    # Summary
    rag_times = [r["time"] for r in results if r["method"] == "RAG" and r["success"]]
    context_times = [r["time"] for r in results if r["method"] == "Context Injection" and r["success"]]
    
    if rag_times and context_times:
        print(f"\n📈 Performance Summary:")
        print(f"RAG Average: {sum(rag_times)/len(rag_times):.2f}s")
        print(f"Context Injection Average: {sum(context_times)/len(context_times):.2f}s")

if __name__ == "__main__":
    main()
