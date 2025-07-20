import requests
import time

def simple_test():
    """Simple comparison test with one question."""
    
    question = "What is CloudSphere Platform?"
    
    print("🔍 SIMPLE COMPARISON TEST")
    print("=" * 40)
    print(f"Question: {question}")
    print()
    
    # Test RAG method
    print("🤖 Testing RAG Method...")
    start_time = time.time()
    try:
        response = requests.post(
            "http://localhost:8000/ask", 
            json={"question": question},
            timeout=60  # Increased timeout
        )
        rag_time = time.time() - start_time
        
        if response.status_code == 200:
            rag_answer = response.json()["answer"]
            print(f"✅ RAG Success - Time: {rag_time:.3f}s")
            print(f"Answer: {rag_answer[:150]}...")
        else:
            print(f"❌ RAG Error: {response.status_code}")
            rag_answer = None
    except Exception as e:
        rag_time = time.time() - start_time
        print(f"❌ RAG Exception: {str(e)[:100]}")
        rag_answer = None
    
    print()
    
    # Test Context Injection method
    print("🎯 Testing Context Injection Method...")
    start_time = time.time()
    try:
        response = requests.post(
            "http://localhost:8000/ask?use_context_injection=true", 
            json={"question": question},
            timeout=60  # Increased timeout
        )
        context_time = time.time() - start_time
        
        if response.status_code == 200:
            context_answer = response.json()["answer"]
            print(f"✅ Context Injection Success - Time: {context_time:.3f}s")
            print(f"Answer: {context_answer[:150]}...")
        else:
            print(f"❌ Context Injection Error: {response.status_code}")
            context_answer = None
    except Exception as e:
        context_time = time.time() - start_time
        print(f"❌ Context Injection Exception: {str(e)[:100]}")
        context_answer = None
    
    # Compare if both succeeded
    if rag_answer and context_answer:
        print("\n📊 COMPARISON:")
        print(f"RAG Time: {rag_time:.3f}s")
        print(f"Context Injection Time: {context_time:.3f}s")
        
        if rag_time < context_time:
            diff = context_time - rag_time
            print(f"🏆 RAG is {diff:.3f}s faster")
        else:
            diff = rag_time - context_time
            print(f"🏆 Context Injection is {diff:.3f}s faster")
    
    print("\n" + "=" * 40)

if __name__ == "__main__":
    simple_test()
