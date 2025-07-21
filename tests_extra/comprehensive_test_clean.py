"""
Comprehensive test script για το FAQ-RAG System (CloudSphere Knowledge Base).

Τρέξε το με: python tests_extra/comprehensive_test_clean.py
Βεβαιώσου ότι το API τρέχει με:
uvicorn src.main:app --host 127.0.0.1 --port 8000
"""

import requests
import time

BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Helper για όμορφο formatting."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def print_subsection(title: str):
    """Helper για υποτμήματα."""
    print(f"\n{'-'*50}")
    print(f"  {title}")
    print(f"{'-'*50}")


def test_basic_functionality():
    """Τεστάρει τη βασική λειτουργικότητα του FAQ system."""
    print_section("Testing Basic FAQ Functionality")
    
    # CloudSphere-specific test questions based on knowledge base
    test_questions = [
        {
            "question": "What is CloudSphere Platform and who is it for?",
            "category": "Product Overview",
            "expected_keywords": ["cloud-native", "Kubernetes", "PostgreSQL"]
        },
        {
            "question": "How much does the Professional tier cost?",
            "category": "Pricing - Direct Match", 
            "expected_keywords": ["$149", "month", "Professional"]
        },
        {
            "question": "Do you offer a free trial?",
            "category": "Trial Information",
            "expected_keywords": ["14-day", "Professional tier", "$100"]
        },
        {
            "question": "I forgot my password, how can I reset it?",
            "category": "Authentication Support",
            "expected_keywords": ["Forgot password", "reset link", "60 minutes"]
        },
        {
            "question": "What industry compliance certifications do you have?",
            "category": "Compliance & Security",
            "expected_keywords": ["SOC 2", "ISO 27001", "GDPR", "HIPAA"]
        },
        {
            "question": "What are the API rate limits?",
            "category": "API Technical Details",
            "expected_keywords": ["10 requests per second", "100,000", "429"]
        }
    ]
    
    results = []
    successful_tests = 0
    total_tests = len(test_questions)
    for i, test_case in enumerate(test_questions):
        print(f"\n🔍 Test {i+1}/{total_tests}: {test_case['category']}")
        print(f"❓ Question: '{test_case['question']}'")
        print("-" * 50)
        result = {
            "category": test_case['category'],
            "question": test_case['question'],
            "expected_keywords": test_case['expected_keywords'],
            "status_code": None,
            "response_time": None,
            "answer": None,
            "keywords_found": 0,
            "error": None
        }
        try:
            start_time = time.time()
            response = requests.post(
                f"{BASE_URL}/ask",
                json={"question": test_case['question']},
                timeout=60
            )
            end_time = time.time()
            response_time = end_time - start_time
            result["status_code"] = response.status_code
            result["response_time"] = response_time
            if response.status_code == 200:
                answer = response.json()["answer"]
                result["answer"] = answer
                print(f"✅ Status: SUCCESS ({response.status_code})")
                print(f"⏱️  Response time: {response_time:.2f} seconds")
                answer_preview = answer[:200]
                if len(answer) > 200:
                    answer_preview += "..."
                print(f"📝 Answer: {answer_preview}")
                keywords_found = 0
                for keyword in test_case['expected_keywords']:
                    if keyword.lower() in answer.lower():
                        keywords_found += 1
                result["keywords_found"] = keywords_found
                if keywords_found > 0:
                    expected_count = len(test_case['expected_keywords'])
                    print(f"🎯 Relevance: {keywords_found}/{expected_count} keywords found")
                    successful_tests += 1
                else:
                    print("⚠️  Warning: No expected keywords found in answer")
                    print(f"   Expected: {test_case['expected_keywords']}")
            else:
                print(f"❌ Error: HTTP {response.status_code}")
                try:
                    error_detail = response.json().get('detail', 'Unknown error')
                    print(f"   Details: {error_detail}")
                    result["error"] = error_detail
                except Exception:
                    print(f"   Raw response: {response.text}")
                    result["error"] = response.text
        except requests.exceptions.Timeout:
            print("⏰ Timeout: Request took longer than 60 seconds")
            result["error"] = "Timeout"
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            result["error"] = str(e)
        results.append(result)
    result_msg = f"Basic Functionality Results: {successful_tests}/{total_tests} successful"
    print_subsection(result_msg)
    return successful_tests / total_tests, results


def test_edge_cases():
    """Τεστάρει edge cases και error handling."""
    print_section("Testing Edge Cases & Error Handling")
    
    edge_cases = [
        {
            "name": "Empty question",
            "payload": {"question": ""},
            "expected_status": [422, 400]
        },
        {
            "name": "Very short question", 
            "payload": {"question": "?"},
            "expected_status": [200, 422]
        },
        {
            "name": "Very long question",
            "payload": {"question": "What " + "is " * 500 + "CloudSphere?"},
            "expected_status": [200, 422, 413]
        },
        {
            "name": "Non-English question",
            "payload": {"question": "Τι είναι το CloudSphere Platform;"},
            "expected_status": [200]
        },
        {
            "name": "Special characters",
            "payload": {"question": "What is CloudSphere's platform?"},
            "expected_status": [200]
        },
        {
            "name": "Out of scope question",
            "payload": {"question": "What's the weather like today?"},
            "expected_status": [200]
        },
        {
            "name": "Missing field",
            "payload": {},
            "expected_status": [422]
        }
    ]
    
    passed_tests = 0
    
    for i, case in enumerate(edge_cases):
        print(f"\n🧪 Edge Case {i+1}: {case['name']}")
        print(f"📤 Payload: {case['payload']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/ask",
                json=case['payload'],
                timeout=30
            )
            
            status_ok = response.status_code in case['expected_status']
            status_indicator = "✅" if status_ok else "⚠️"
            expected_text = "(Expected)" if status_ok else "(Unexpected)"
            
            print(f"{status_indicator} Status: {response.status_code} {expected_text}")
            
            if response.status_code == 200:
                answer = response.json().get("answer", "No answer field")
                answer_preview = answer[:100]
                if len(answer) > 100:
                    answer_preview += "..."
                print(f"📝 Response: {answer_preview}")
            elif response.status_code in [400, 422]:
                try:
                    error_detail = response.json().get('detail', 'No detail provided')
                    print(f"🛠️  Error detail: {error_detail}")
                except Exception:
                    print(f"🛠️  Raw error: {response.text[:100]}")
            
            if status_ok:
                passed_tests += 1
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    edge_result = f"Edge Cases Results: {passed_tests}/{len(edge_cases)} handled as expected"
    print_subsection(edge_result)
    return passed_tests / len(edge_cases)


def test_history_endpoint():
    """Τεστάρει το history endpoint."""
    print_section("Testing History Endpoint")
    
    print("📋 Testing basic history retrieval...")
    try:
        response = requests.get(f"{BASE_URL}/history")
        
        if response.status_code == 200:
            history = response.json()
            print(f"✅ History endpoint working - {len(history)} interactions found")
            
            if history:
                print("📊 Sample interaction:")
                sample = history[0]
                question_preview = sample.get('question', 'N/A')[:50]
                answer_preview = sample.get('answer', 'N/A')[:50]
                print(f"   Q: {question_preview}...")
                print(f"   A: {answer_preview}...")
                print(f"   Timestamp: {sample.get('ts', 'N/A')}")
            
            # Test with limit parameter
            print("\n📋 Testing history with limit=3...")
            limited_response = requests.get(f"{BASE_URL}/history?limit=3")
            
            if limited_response.status_code == 200:
                limited_history = limited_response.json()
                print(f"✅ Limited history working - {len(limited_history)} interactions returned")
                
                if len(limited_history) <= 3:
                    print("✅ Limit parameter respected")
                else:
                    print("⚠️  Limit parameter not working correctly")
                    
                return True
            else:
                print(f"❌ Limited history failed: {limited_response.status_code}")
                return False
                
        else:
            print(f"❌ History endpoint failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ History test exception: {str(e)}")
        return False


def test_performance():
    """Μετράει την απόδοση του συστήματος."""
    print_section("Performance Analysis")
    
    perf_questions = [
        "What is CloudSphere Platform?",
        "How much does Professional cost?", 
        "What compliance certifications do you have?",
        "How do I troubleshoot a failed deployment?",
        "What are API rate limits and authentication?",
    ]
    
    print("⏱️  Running performance tests...")
    print("Note: First request may be slower due to model loading\n")
    
    all_times = []
    
    for i, question in enumerate(perf_questions):
        print(f"🔄 Test {i+1}/5: {question[:40]}...")
        
        times_for_question = []
        
        for run in range(3):
            try:
                start_time = time.time()
                
                response = requests.post(
                    f"{BASE_URL}/ask",
                    json={"question": question},
                    timeout=120
                )
                
                end_time = time.time()
                response_time = end_time - start_time
                
                if response.status_code == 200:
                    times_for_question.append(response_time)
                    print(f"    Run {run+1}: {response_time:.2f}s")
                else:
                    print(f"    Run {run+1}: Failed ({response.status_code})")
                    
                if run < 2:
                    time.sleep(1)
                    
            except requests.exceptions.Timeout:
                print(f"    Run {run+1}: Timeout (>120s)")
            except Exception as e:
                print(f"    Run {run+1}: Error - {str(e)}")
        
        if times_for_question:
            avg_time = sum(times_for_question) / len(times_for_question)
            all_times.extend(times_for_question)
            print(f"    Average: {avg_time:.2f}s")
        
        print()
    
    if all_times:
        print_subsection("Performance Summary")
        print(f"📊 Total requests tested: {len(all_times)}")
        avg_response_time = sum(all_times) / len(all_times)
        print(f"⚡ Average response time: {avg_response_time:.2f}s")
        print(f"🏃 Fastest response: {min(all_times):.2f}s")
        print(f"🐌 Slowest response: {max(all_times):.2f}s")
        
        # Performance categories
        fast_count = sum(1 for t in all_times if t < 5)
        medium_count = sum(1 for t in all_times if 5 <= t < 15)
        slow_count = sum(1 for t in all_times if t >= 15)
        
        print("\n📈 Performance distribution:")
        fast_pct = fast_count/len(all_times)*100
        medium_pct = medium_count/len(all_times)*100
        slow_pct = slow_count/len(all_times)*100
        
        print(f"   🟢 Fast (<5s): {fast_count} requests ({fast_pct:.1f}%)")
        print(f"   🟡 Medium (5-15s): {medium_count} requests ({medium_pct:.1f}%)")
        print(f"   🔴 Slow (>15s): {slow_count} requests ({slow_pct:.1f}%)")
        
        return avg_response_time
    else:
        print("❌ No successful performance data collected")
        return None


def test_knowledge_coverage():
    """Τεστάρει την κάλυψη της knowledge base."""
    print_section("Knowledge Base Coverage Test")
    
    coverage_areas = [
        {
            "area": "Pricing & Billing",
            "questions": [
                "What pricing tiers do you offer?",
                "Do you have hidden fees?", 
                "What payment methods do you accept?"
            ]
        },
        {
            "area": "Security & Compliance",
            "questions": [
                "How is my data protected?",
                "What compliance certifications do you have?",
                "Do you support multi-factor authentication?"
            ]
        },
        {
            "area": "Technical Support", 
            "questions": [
                "What support channels are available?",
                "How do I troubleshoot deployments?",
                "What are your business hours?"
            ]
        },
        {
            "area": "API & Integration",
            "questions": [
                "What are the API rate limits?",
                "Do you provide SDKs?",
                "How do I integrate with CI/CD?"
            ]
        },
        {
            "area": "Account Management",
            "questions": [
                "How do I reset my password?",
                "How do I upgrade my plan?",
                "How do I close my account?"
            ]
        }
    ]
    
    coverage_results = {}
    
    for area_info in coverage_areas:
        area = area_info["area"]
        questions = area_info["questions"]
        
        print(f"\n📚 Testing {area} coverage...")
        
        successful_answers = 0
        
        for question in questions:
            try:
                response = requests.post(
                    f"{BASE_URL}/ask",
                    json={"question": question},
                    timeout=45
                )
                
                if response.status_code == 200:
                    answer = response.json()["answer"]
                    
                    # Basic relevance check
                    uncertain_phrases = [
                        "i don't know", "not sure", "no information", 
                        "cannot answer"
                    ]
                    
                    if (len(answer) > 50 and 
                        not any(phrase in answer.lower() for phrase in uncertain_phrases)):
                        successful_answers += 1
                        print(f"   ✅ {question[:40]}...")
                    else:
                        print(f"   ⚠️  {question[:40]}... (uncertain answer)")
                else:
                    print(f"   ❌ {question[:40]}... (HTTP {response.status_code})")
                    
            except Exception as e:
                print(f"   ❌ {question[:40]}... (Exception: {str(e)[:30]})")
        
        coverage_percentage = (successful_answers / len(questions)) * 100
        coverage_results[area] = coverage_percentage
        print(f"   📊 {area}: {successful_answers}/{len(questions)} ({coverage_percentage:.1f}%)")
    
    print_subsection("Knowledge Coverage Summary")
    overall_coverage = sum(coverage_results.values()) / len(coverage_results)
    
    for area, percentage in coverage_results.items():
        if percentage >= 80:
            status = "🟢"
        elif percentage >= 60:
            status = "🟡"
        else:
            status = "🔴"
        print(f"{status} {area}: {percentage:.1f}%")
    
    print(f"\n📈 Overall Knowledge Coverage: {overall_coverage:.1f}%")
    return overall_coverage


def check_api_availability():
    """Ελέγχει αν το API είναι διαθέσιμο."""
    print("🔍 Checking API availability...")
    
    try:
        response = requests.get(f"{BASE_URL}/", timeout=10)
        print(f"✅ API is responding (Status: {response.status_code})")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure it's running with:")
        print("   uvicorn src.main:app --host 127.0.0.1 --port 8000")
        return False
        
    except requests.exceptions.Timeout:
        print("⏰ API connection timeout. Service may be overloaded.")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False


def main():
    """Κύρια συνάρτηση που τρέχει όλα τα tests."""
    print("🚀 CloudSphere FAQ-RAG System - Comprehensive Test Suite")
    print("="*70)
    print("This will test your FastAPI-based FAQ service with CloudSphere knowledge base")
    
    if not check_api_availability():
        print("\n⚠️  Tests cannot proceed without API connectivity.")
        print("\nTo start the API run:")
        print("   uvicorn src.main:app --host 127.0.0.1 --port 8000")
        return
    
    print("\n🎯 Starting comprehensive testing...")
    
    # Run tests for both context injection (default) and RAG
    import json
    from datetime import datetime
    modes = [
        {"name": "context_injection", "param": True},
        {"name": "rag", "param": False}
    ]
    all_mode_results = {}
    for mode in modes:
        print_section(f"Running tests in mode: {mode['name']}")
        orig_post = requests.post
        def post_with_mode(url, *args, **kwargs):
            if "/ask" in url and "json" in kwargs:
                # Σωστός τρόπος: query parameter, όχι JSON body
                if "params" not in kwargs:
                    kwargs["params"] = {}
                kwargs["params"]["use_context_injection"] = mode["param"]
            return orig_post(url, *args, **kwargs)
        requests.post = post_with_mode
        test_results = {}
        try:
            print("\n🚀 Starting basic functionality tests...")
            test_results['basic'], basic_details = test_basic_functionality()
            print("\n🚀 Continuing to edge cases testing...")
            test_results['edge_cases'] = test_edge_cases()
            print("\n🚀 Continuing to history testing...")
            test_results['history'] = test_history_endpoint()
            print("\n🚀 Continuing to performance testing...")
            test_results['performance'] = test_performance()
            print("\n🚀 Continuing to knowledge coverage testing...")
            test_results['coverage'] = test_knowledge_coverage()
        except KeyboardInterrupt:
            print("\n\n⏹️  Testing interrupted by user.")
            return
        finally:
            requests.post = orig_post
        all_mode_results[mode['name']] = {"summary": test_results, "basic_details": basic_details}
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"comprehensive_test_results_{mode['name']}_{timestamp}.json"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({"summary": test_results, "basic_details": basic_details}, f, indent=2, ensure_ascii=False)
            print(f"💾 Results saved to: {filename}")
        except Exception as e:
            print(f"⚠️  Could not save results: {str(e)}")
    # Final summary comparison
    print_section("🎉 Testing Complete - Final Summary (Comparison)")
    for mode in modes:
        name = mode['name']
        print(f"\n=== {name.upper()} MODE ===")
        summary = all_mode_results[name]["summary"]
        print("📊 Test Results:")
        if 'basic' in summary:
            print(f"   🔧 Basic Functionality: {summary['basic']*100:.1f}% success rate")
        if 'edge_cases' in summary:
            print(f"   🧪 Edge Cases: {summary['edge_cases']*100:.1f}% handled correctly")
        if 'history' in summary:
            history_status = "✅ Working" if summary['history'] else "❌ Failed"
            print(f"   📋 History Endpoint: {history_status}")
        if 'performance' in summary and summary['performance']:
            print(f"   ⚡ Average Response Time: {summary['performance']:.2f}s")
        if 'coverage' in summary:
            print(f"   📚 Knowledge Coverage: {summary['coverage']:.1f}%")
    print("\n💡 Use the saved JSON files for detailed comparison and analysis.")


if __name__ == "__main__":
    main()
