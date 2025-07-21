"""
Simple and effective test script for FAQ-RAG System.

Usage: python tests_extra/simple_test.py
Make sure API is running: uvicorn src.main:app --host 127.0.0.1 --port 8000
"""

import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"


def check_api():
    """Check if API is available"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def test_basic_questions():
    """Test core functionality with key questions"""
    print("🧪 Testing Core Functionality")
    print("-" * 40)
    
    questions = [
        # Valid questions that should have answers
        ("What is CloudSphere Platform?", "📚 Valid"),
        ("How much does Professional cost?", "📚 Valid"),
        
        # Questions that DON'T exist in knowledge base
        ("How do I bake a chocolate cake?", "🍰 Out-of-scope"),
        
        # Ambiguous/controversial questions
        ("Which cloud provider is the best?", "🤔 Controversial"),
        ("Is CloudSphere better than AWS?", "🤔 Controversial")
    ]
    
    results = []
    
    for i, (question, category) in enumerate(questions, 1):
        print(f"{i}. {category} {question[:30]}...", end=" ")
        
        try:
            start_time = time.time()
            print("⏳ ", end="", flush=True)  # Progress indicator
            response = requests.post(
                f"{BASE_URL}/ask",
                json={"question": question},
                timeout=125  # Increased timeout for slow LLM
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                answer = response.json()["answer"]
                # Quick relevance check
                has_content = (len(answer) > 50 and
                               "don't know" not in answer.lower())
                status = "✅" if has_content else "⚠️"
                print(f"{status} ({response_time:.1f}s)")
                
                # Show answer preview for analysis
                preview = answer[:150] + ('...' if len(answer) > 150 else '')
                print(f"   📝 Answer: {preview}")
                
                results.append({"success": has_content, "time": response_time})
            else:
                print(f"❌ HTTP {response.status_code}")
                results.append({"success": False, "time": response_time})
                
        except requests.exceptions.Timeout:
            print("⏰ Timeout")
            results.append({"success": False, "time": 125})
        except Exception as e:
            print(f"❌ Error: {str(e)[:20]}...")
            results.append({"success": False, "time": 0})
    
    return results


def test_error_handling():
    """Test edge cases quickly"""
    print("\n🛠️  Testing Error Handling")
    print("-" * 40)
    
    test_cases = [
        {"name": "Empty question", "payload": {"question": ""},
         "expect": [400, 422]},
        {"name": "Missing field", "payload": {}, "expect": [422]},
        {"name": "Very long input",
         "payload": {"question": "What " * 200 + "?"},
         "expect": [200, 413, 422]}
    ]
    
    passed = 0
    
    for case in test_cases:
        print(f"• {case['name']}...", end=" ")
        
        try:
            response = requests.post(
                f"{BASE_URL}/ask",
                json=case["payload"],
                timeout=10
            )
            
            if response.status_code in case["expect"]:
                print("✅")
                passed += 1
            else:
                print(f"⚠️ Got {response.status_code}")
                
        except Exception as e:
            print(f"❌ {str(e)[:20]}...")
    
    return passed, len(test_cases)


def test_history():
    """Test history endpoint"""
    print("\n📋 Testing History")
    print("-" * 40)
    
    try:
        response = requests.get(f"{BASE_URL}/history", timeout=10)
        if response.status_code == 200:
            history = response.json()
            print(f"✅ History working - {len(history)} entries")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def compare_modes():
    """Compare context injection vs RAG mode"""
    print("\n⚖️  Comparing Modes")
    print("-" * 40)
    
    test_question = "What is CloudSphere Platform?"
    modes = [
        {"name": "Context Injection", "param": True},
        {"name": "RAG", "param": False}
    ]
    
    results = {}
    
    for mode in modes:
        print(f"Testing {mode['name']}...", end=" ")
        
        try:
            start_time = time.time()
            print("⏳ ", end="", flush=True)  # Progress indicator
            response = requests.post(
                f"{BASE_URL}/ask",
                json={
                    "question": test_question,
                    "use_context_injection": mode["param"]  # Moved to JSON body
                },
                timeout=60  # Increased timeout
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                answer = response.json()["answer"]
                print(f"✅ ({response_time:.1f}s)")
                
                # Show answer preview for comparison
                preview = answer[:100] + ('...' if len(answer) > 100 else '')
                print(f"      📝 {preview}")
                
                results[mode['name']] = {
                    "success": True,
                    "time": response_time,
                    "answer_length": len(answer)
                }
            else:
                print(f"❌ {response.status_code}")
                results[mode['name']] = {
                    "success": False, "time": response_time}
                
        except Exception as e:
            print(f"❌ {str(e)[:20]}...")
            results[mode['name']] = {"success": False, "time": 0}
    
    return results


def main():
    """Run all tests"""
    print("🚀 CloudSphere FAQ System - Quick Test Suite")
    print("=" * 50)
    
    # Check API availability
    if not check_api():
        print("❌ API not available. Start with:")
        print("   uvicorn src.main:app --host 127.0.0.1 --port 8000")
        return
    
    print("✅ API is running")
    
    # Run tests
    start_time = time.time()
    
    basic_results = test_basic_questions()
    error_passed, error_total = test_error_handling()
    history_ok = test_history()
    mode_comparison = compare_modes()
    
    total_time = time.time() - start_time
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    # Basic functionality
    successful = sum(1 for r in basic_results if r["success"])
    total_time = sum(r["time"] for r in basic_results if r["success"])
    avg_time = total_time / max(successful, 1)
    print(f"🔧 Basic Tests: {successful}/{len(basic_results)} passed")
    print(f"⏱️  Average Response: {avg_time:.1f}s")
    
    # Error handling
    print(f"🛠️  Error Handling: {error_passed}/{error_total} correct")
    
    # History
    print(f"📋 History Endpoint: {'✅ Working' if history_ok else '❌ Failed'}")
    
    # Performance assessment
    if avg_time < 10:
        perf_status = "🟢 Good"
    elif avg_time < 20:
        perf_status = "🟡 Acceptable"
    else:
        perf_status = "🔴 Slow"
    print(f"🚀 Performance: {perf_status}")
    
    # Mode comparison
    if mode_comparison:
        print("\n⚖️  Mode Comparison:")
        for mode, data in mode_comparison.items():
            if data.get("success"):
                print(f"   {mode}: {data['time']:.1f}s")
            else:
                print(f"   {mode}: Failed")
    
    print(f"\n⏱️  Total test time: {total_time:.1f}s")
    
    # Save compact results
    results = {
        "timestamp": datetime.now().isoformat(),
        "basic_success_rate": successful / len(basic_results),
        "avg_response_time": avg_time,
        "error_handling_rate": error_passed / error_total,
        "history_working": history_ok,
        "mode_comparison": mode_comparison,
        "total_test_time": total_time
    }
    
    filename = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"💾 Results saved: {filename}")
    except Exception as e:
        print(f"⚠️  Could not save results: {e}")


if __name__ == "__main__":
    main()
