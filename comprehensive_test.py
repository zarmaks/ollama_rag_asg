"""
Comprehensive test script για το FAQ-RAG System (CloudSphere Knowledge Base).

Τρέξε το με: python comprehensive_test.py
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
            "expected_keywords": [
                "cloud-native", "Kubernetes", "PostgreSQL", "software vendors"
            ]
        },
        {
            "question": "How much does the Professional tier cost?",
            "category": "Pricing - Direct Match",
            "expected_keywords": [
                "$149", "month", "Professional", "8 vCPU", "16 GB RAM"
            ]
        },
        {
            "question": "Do you offer a free trial?",
            "category": "Trial Information",
            "expected_keywords": [
                "14-day", "Professional tier", "$100", "credit card"
            ]
        },
        {
            "question": "I forgot my password, how can I reset it?",
            "category": "Authentication Support",
            "expected_keywords": [
                "Forgot password", "reset link", "60 minutes",
                "notifications@cloudsphere.com"
            ]
        },
        {
            "question": "What industry compliance certifications do you have?",
            "category": "Compliance & Security",
            "expected_keywords": [
                "SOC 2", "ISO 27001", "GDPR", "HIPAA",
                "compliance@cloudsphere.com"
            ]
        },
        {
            "question": "What are the API rate limits?",
            "category": "API Technical Details",
            "expected_keywords": [
                "10 requests per second", "100,000", "429 Too Many Requests",
                "Retry-After"
            ]
        }
    ]
    
    successful_tests = 0
    total_tests = len(test_questions)
    
    for i, test_case in enumerate(test_questions):
        print(f"\n🔍 Test {i+1}/{total_tests}: {test_case['category']}")
        print(f"❓ Question: '{test_case['question']}'")
        print("-" * 50)
        
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{BASE_URL}/ask",
                json={"question": test_case['question']},
                timeout=60  # Give LLM time to respond
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                answer = response.json()["answer"]
                
                print(f"✅ Status: SUCCESS ({response.status_code})")
                print(f"⏱️  Response time: {response_time:.2f} seconds")
                answer_preview = answer[:200]
                if len(answer) > 200:
                    answer_preview += "..."
                print(f"📝 Answer: {answer_preview}")
                
                # Check for expected keywords (basic relevance test)
                keywords_found = sum(
                    1 for keyword in test_case['expected_keywords']
                    if keyword.lower() in answer.lower()
                )
                
                if keywords_found > 0:
                    expected_count = len(test_case['expected_keywords'])
                    print(f"🎯 Relevance: {keywords_found}/{expected_count} "
                          f"expected keywords found")
                    successful_tests += 1
                else:
                    print("⚠️  Warning: No expected keywords found in answer")
                    expected_keywords = test_case['expected_keywords']
                    print(f"   Expected: {expected_keywords}")
                    
            else:
                print(f"❌ Error: HTTP {response.status_code}")
                try:
                    error_detail = response.json().get('detail',
                                                       'Unknown error')
                    print(f"   Details: {error_detail}")
                except Exception:
                    print(f"   Raw response: {response.text}")
                    
        except requests.exceptions.Timeout:
            print("⏰ Timeout: Request took longer than 60 seconds")
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    result_msg = f"Basic Functionality Results: {successful_tests}/" \
                 f"{total_tests} successful"
    print_subsection(result_msg)
    return successful_tests / total_tests


def test_edge_cases():
    """Τεστάρει edge cases και error handling."""
    print_section("Testing Edge Cases & Error Handling")
    
    edge_cases = [
        {
            "name": "Empty question",
            "payload": {"question": ""},
            "expected_status": [422, 400]  # Validation error expected
        },
        {
            "name": "Very short question",
            "payload": {"question": "?"},
            "expected_status": [200, 422]  # May handle or reject
        },
        {
            "name": "Very long question",
            "payload": {"question": "What " + "is " * 500 + "CloudSphere?"},
            # May handle, reject, or payload too large
            "expected_status": [200, 422, 413]
        },
        {
            "name": "Non-English question",
            "payload": {"question": "Τι είναι το CloudSphere Platform;"},
            "expected_status": [200]  # Should handle gracefully
        },
        {
            "name": "Special characters",
            "payload": {
                "question": "What is CloudSphere's <script>alert('test')"
                           "</script> platform?"
            },
            "expected_status": [200]  # Should sanitize and handle
        },
        {
            "name": "Out of scope question",
            "payload": {"question": "What's the weather like today?"},
            # Should respond that it's not in knowledge base
            "expected_status": [200]
        },
        {
            "name": "Missing field",
            "payload": {"wrong_field": "test"},
            "expected_status": [422]  # Validation error
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
            
            print(f"{status_indicator} Status: {response.status_code} "
                  f"{expected_text}")
            
            if response.status_code == 200:
                answer = response.json().get("answer", "No answer field")
                answer_preview = answer[:100]
                if len(answer) > 100:
                    answer_preview += "..."
                print(f"📝 Response: {answer_preview}")
            elif response.status_code in [400, 422]:
                try:
                    error_detail = response.json().get('detail',
                                                       'No detail provided')
                    print(f"🛠️  Error detail: {error_detail}")
                except Exception:
                    print(f"🛠️  Raw error: {response.text[:100]}")
            
            if status_ok:
                passed_tests += 1
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    edge_result = f"Edge Cases Results: {passed_tests}/{len(edge_cases)} " \
                  f"handled as expected"
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
            history_msg = f"✅ History endpoint working - " \
                         f"{len(history)} interactions found"
            print(history_msg)
            
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
                limited_msg = f"✅ Limited history working - " \
                             f"{len(limited_history)} interactions returned"
                print(limited_msg)
                
                if len(limited_history) <= 3:
                    print("✅ Limit parameter respected")
                else:
                    print("⚠️  Limit parameter not working correctly")
                    
                return True
            else:
                error_msg = f"❌ Limited history failed: " \
                           f"{limited_response.status_code}"
                print(error_msg)
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
    
    # Performance test questions (variety of complexity)
    perf_questions = [
        "What is CloudSphere Platform?",  # Simple, direct match
        "How much does Professional cost?",  # Simple pricing query
        "What compliance certifications do you have?",  # Medium complexity
        "How do I troubleshoot a failed deployment?",  # Complex, longer answer
        "What are API rate limits and authentication?",  # Multi-part question
    ]
    
    print("⏱️  Running performance tests...")
    print("Note: First request may be slower due to model loading\n")
    
    all_times = []
    
    for i, question in enumerate(perf_questions):
        print(f"🔄 Test {i+1}/5: {question[:40]}...")
        
        times_for_question = []
        
        # Run each question 3 times
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
                    
                # Small delay to avoid overwhelming the service
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
        
        print()  # Empty line for readability
    
    # Overall performance analysis
    if all_times:
        print_subsection("Performance Summary")
        print(f"📊 Total requests tested: {len(all_times)}")
        print(f"⚡ Average response time: {sum(all_times) / len(all_times):.2f}s")
        print(f"🏃 Fastest response: {min(all_times):.2f}s")
        print(f"🐌 Slowest response: {max(all_times):.2f}s")
        
        # Performance categories
        fast_count = sum(1 for t in all_times if t < 5)
        medium_count = sum(1 for t in all_times if 5 <= t < 15)
        slow_count = sum(1 for t in all_times if t >= 15)
        
        print(f"\n📈 Performance distribution:")
        print(f"   🟢 Fast (<5s): {fast_count} requests ({fast_count/len(all_times)*100:.1f}%)")
        print(f"   🟡 Medium (5-15s): {medium_count} requests ({medium_count/len(all_times)*100:.1f}%)")
        print(f"   🔴 Slow (>15s): {slow_count} requests ({slow_count/len(all_times)*100:.1f}%)")
        
        return sum(all_times) / len(all_times)
    else:
        print("❌ No successful performance data collected")
        return None


def test_knowledge_coverage():
    """Τεστάρει την κάλυψη της knowledge base."""
    print_section("Knowledge Base Coverage Test")
    
    # Test questions for different areas of the knowledge base
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
                    
                    # Basic relevance check - answer should not be too short or contain "I don't know" patterns
                    if (len(answer) > 50 and 
                        not any(phrase in answer.lower() for phrase in 
                               ["i don't know", "not sure", "no information", "cannot answer"])):
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
    
    # Overall coverage summary
    print_subsection("Knowledge Coverage Summary")
    overall_coverage = sum(coverage_results.values()) / len(coverage_results)
    
    for area, percentage in coverage_results.items():
        status = "🟢" if percentage >= 80 else "🟡" if percentage >= 60 else "🔴"
        print(f"{status} {area}: {percentage:.1f}%")
    
    print(f"\n📈 Overall Knowledge Coverage: {overall_coverage:.1f}%")
    return overall_coverage


def check_api_availability():
    """Ελέγχει αν το API είναι διαθέσιμο."""
    print("🔍 Checking API availability...")
    
    try:
        # Try to connect to the base URL
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
    
    # Check API availability first
    if not check_api_availability():
        print("\n⚠️  Tests cannot proceed without API connectivity.")
        print("\nTo start the API run:")
        print("   uvicorn src.main:app --host 127.0.0.1 --port 8000")
        return
    
    print("\n🎯 Starting comprehensive testing...")
    
    test_results = {}
    
    # Run all test suites
    try:
        print("\n⏸️  Press Enter to start basic functionality tests...")
        input()
        test_results['basic'] = test_basic_functionality()
        
        print("\n⏸️  Press Enter to continue to edge cases testing...")
        input()
        test_results['edge_cases'] = test_edge_cases()
        
        print("\n⏸️  Press Enter to continue to history testing...")
        input()
        test_results['history'] = test_history_endpoint()
        
        print("\n⏸️  Press Enter to continue to performance testing...")
        input()
        test_results['performance'] = test_performance()
        
        print("\n⏸️  Press Enter to continue to knowledge coverage testing...")
        input()
        test_results['coverage'] = test_knowledge_coverage()
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Testing interrupted by user.")
        return
    
    # Final summary
    print_section("🎉 Testing Complete - Final Summary")
    
    print("📊 Test Results:")
    
    if 'basic' in test_results:
        print(f"   🔧 Basic Functionality: {test_results['basic']*100:.1f}% success rate")
    
    if 'edge_cases' in test_results:
        print(f"   🧪 Edge Cases: {test_results['edge_cases']*100:.1f}% handled correctly")
    
    if 'history' in test_results:
        history_status = "✅ Working" if test_results['history'] else "❌ Failed"
        print(f"   📋 History Endpoint: {history_status}")
    
    if 'performance' in test_results and test_results['performance']:
        print(f"   ⚡ Average Response Time: {test_results['performance']:.2f}s")
    
    if 'coverage' in test_results:
        print(f"   📚 Knowledge Coverage: {test_results['coverage']:.1f}%")
    
    # Overall system health assessment
    health_score = 0
    total_metrics = 0
    
    if 'basic' in test_results:
        health_score += test_results['basic'] * 30  # 30% weight
        total_metrics += 30
    
    if 'edge_cases' in test_results:
        health_score += test_results['edge_cases'] * 20  # 20% weight  
        total_metrics += 20
    
    if 'history' in test_results:
        health_score += (1 if test_results['history'] else 0) * 10  # 10% weight
        total_metrics += 10
    
    if 'coverage' in test_results:
        health_score += (test_results['coverage'] / 100) * 40  # 40% weight
        total_metrics += 40
    
    if total_metrics > 0:
        overall_health = health_score / total_metrics * 100
        health_emoji = "🟢" if overall_health >= 80 else "🟡" if overall_health >= 60 else "🔴"
        print(f"\n{health_emoji} Overall System Health: {overall_health:.1f}%")
    
    # Recommendations
    print("\n💡 Recommendations:")
    
    if test_results.get('basic', 0) < 0.8:
        print("   - Review knowledge base relevance and LLM prompt tuning")
    
    if test_results.get('performance', 0) and test_results['performance'] > 10:
        print("   - Consider optimizing LLM response time or adding caching")
    
    if test_results.get('coverage', 0) < 70:
        print("   - Expand knowledge base coverage for underperforming areas")
    
    print("   - Monitor logs for any errors during testing")
    print("   - Consider adding more specific test cases for your use case")
    
    print(f"\n🏁 Testing completed! Your CloudSphere FAQ-RAG system is {'ready for production' if overall_health >= 80 else 'needs optimization'}.")


if __name__ == "__main__":
    main()
