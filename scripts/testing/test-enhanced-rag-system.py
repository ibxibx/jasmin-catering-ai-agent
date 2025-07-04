#!/usr/bin/env python3
"""
Test the enhanced RAG system with 5 comprehensive test cases
Respects Azure OpenAI rate limits (10 requests per 10 seconds)
"""

import time
import json
from datetime import datetime
from core.ai_assistant_openai_agent import JasminAIAssistantOpenAI
from core.slack_notifier import SlackNotifier

class EnhancedRAGTester:
    """Test the enhanced RAG system"""
    
    def __init__(self):
        self.assistant = JasminAIAssistantOpenAI()
        self.slack = SlackNotifier()
        self.test_results = []
        
    def wait_for_rate_limit(self, seconds=12):
        """Wait to respect rate limits"""
        print(f"⏳ Waiting {seconds}s for rate limit...")
        time.sleep(seconds)
    
    def run_test_case(self, test_number, subject, body, expected_features):
        """Run a single test case"""
        print(f"\n{'='*60}")
        print(f"🧪 Test Case {test_number}: {subject}")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        try:
            # Generate response with enhanced RAG
            response, documents, info = self.assistant.generate_response(subject, body)
            
            if response:
                processing_time = time.time() - start_time
                
                # Analyze response
                analysis = self.analyze_response(response, documents, info, expected_features)
                
                # Store results
                test_result = {
                    "test_number": test_number,
                    "subject": subject,
                    "success": True,
                    "processing_time": f"{processing_time:.2f}s",
                    "ai_processing_time": info.get('processing_time', 'N/A'),
                    "documents_used": len(documents),
                    "tokens": info.get('tokens', {}),
                    "pricing_extracted": info.get('pricing', {}),
                    "assistant_id": info.get('assistant_id'),
                    "analysis": analysis,
                    "response_length": len(response),
                    "vector_store_used": 'vs_' in str(info.get('assistant_id', ''))
                }
                
                self.test_results.append(test_result)
                
                # Display results
                print(f"✅ SUCCESS")
                print(f"📊 Processing Time: {processing_time:.2f}s")
                print(f"🤖 AI Time: {info.get('processing_time', 'N/A')}")
                print(f"📚 Documents Used: {len(documents)}")
                print(f"🎯 Features Found: {analysis['features_found']}/{analysis['total_features']}")
                print(f"💰 Pricing Extracted: {len(info.get('pricing', {}))}")
                
                if info.get('tokens'):
                    tokens = info['tokens']
                    print(f"🔢 Tokens: {tokens.get('total_tokens', 'N/A')} total")
                
                # Send to Slack
                self.slack.log(f"✅ Test {test_number} Success", "success", {
                    "subject": subject,
                    "processing_time": f"{processing_time:.2f}s",
                    "documents": len(documents),
                    "features": f"{analysis['features_found']}/{analysis['total_features']}"
                })
                
                return True
                
            else:
                print(f"❌ FAILED - No response generated")
                self.test_results.append({
                    "test_number": test_number,
                    "subject": subject,
                    "success": False,
                    "error": "No response generated"
                })
                
                self.slack.log(f"❌ Test {test_number} Failed", "error", {
                    "subject": subject,
                    "error": "No response generated"
                })
                
                return False
                
        except Exception as e:
            print(f"❌ FAILED - Exception: {str(e)}")
            self.test_results.append({
                "test_number": test_number,
                "subject": subject,
                "success": False,
                "error": str(e)
            })
            
            self.slack.log(f"❌ Test {test_number} Error", "error", {
                "subject": subject,
                "error": str(e)
            })
            
            return False
    
    def analyze_response(self, response, documents, info, expected_features):
        """Analyze the response for expected features"""
        response_lower = response.lower()
        
        features_found = 0
        feature_details = {}
        
        for feature in expected_features:
            found = feature.lower() in response_lower
            features_found += 1 if found else 0
            feature_details[feature] = found
        
        return {
            "features_found": features_found,
            "total_features": len(expected_features),
            "feature_details": feature_details,
            "has_pricing": len(info.get('pricing', {})) > 0,
            "professional_tone": "sehr geehrte" in response_lower or "freundliche grüße" in response_lower,
            "three_options": response_lower.count("basis") > 0 and response_lower.count("standard") > 0 and response_lower.count("premium") > 0
        }
    
    def run_all_tests(self):
        """Run all 5 test cases"""
        print("🚀 Enhanced RAG System - 5 Test Cases")
        print("=" * 60)
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🤖 Assistant: {self.assistant.assistant_id}")
        print("=" * 60)
        
        # Send test start notification
        self.slack.log("🧪 Enhanced RAG Testing Started", "info", {
            "test_cases": 5,
            "assistant_id": self.assistant.assistant_id,
            "vector_store": "vs_xDbEaqnBNUtJ70P7GoNgY1qD"
        })
        
        # Test Case 1: Corporate Event
        self.run_test_case(
            1,
            "Firmenfeier für 75 Mitarbeiter - Donnerstag",
            "Guten Tag, wir planen unsere Jahresfeier für 75 Mitarbeiter am Donnerstag, 15. August. Können Sie uns ein Angebot für ein Buffet machen? Wir hätten gerne eine Mischung aus warmen und kalten Speisen.",
            ["basis", "standard", "premium", "75", "donnerstag", "buffet", "warme", "kalte"]
        )
        
        self.wait_for_rate_limit()
        
        # Test Case 2: Vegetarian Wedding
        self.run_test_case(
            2,
            "Vegetarische Hochzeit - 120 Gäste im Juni",
            "Hallo! Wir heiraten im Juni und möchten vegetarisches Catering für 120 Gäste. Die Feier ist an einem Samstag. Können Sie uns drei verschiedene Menü-Optionen anbieten?",
            ["vegetarisch", "hochzeit", "120", "juni", "samstag", "drei", "menü", "basis", "standard", "premium"]
        )
        
        self.wait_for_rate_limit()
        
        # Test Case 3: Urgent Small Event
        self.run_test_case(
            3,
            "Dringend: Catering morgen für 25 Personen",
            "Sehr geehrte Damen und Herren, wir benötigen kurzfristig Catering für morgen für 25 Personen. Es ist eine Geschäftsbesprechung. Ist das möglich und was würde es kosten?",
            ["dringend", "25", "morgen", "geschäftsbesprechung", "eilauftrag", "zuschlag"]
        )
        
        self.wait_for_rate_limit()
        
        # Test Case 4: Premium Summer Wedding
        self.run_test_case(
            4,
            "Hochzeit im Sommer - 200 Gäste Premium Service",
            "Wir planen eine große Hochzeit im Juli mit 200 Gästen und möchten den besten Service. Geld spielt keine Rolle, wir wollen das Premium-Paket mit allem was dazu gehört.",
            ["hochzeit", "200", "juli", "premium", "service", "sommer", "zuschlag"]
        )
        
        self.wait_for_rate_limit()
        
        # Test Case 5: Weekly Office Catering
        self.run_test_case(
            5,
            "Wöchentliches Büro-Catering - Mittwochs für 30 Personen",
            "Guten Tag, wir sind ein Startup und möchten regelmäßig jeden Mittwoch Catering für unser Team von 30 Personen. Gibt es Mengenrabatte für regelmäßige Bestellungen?",
            ["wöchentlich", "mittwoch", "30", "startup", "regelmäßig", "rabatt", "stammkunden"]
        )
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        successful_tests = sum(1 for result in self.test_results if result.get('success', False))
        total_tests = len(self.test_results)
        
        print(f"\n{'='*60}")
        print(f"📊 ENHANCED RAG TESTING SUMMARY")
        print(f"{'='*60}")
        print(f"✅ Successful Tests: {successful_tests}/{total_tests}")
        print(f"📈 Success Rate: {(successful_tests/total_tests*100):.1f}%")
        
        if successful_tests > 0:
            avg_processing_time = sum(float(r.get('processing_time', '0').replace('s', '')) 
                                    for r in self.test_results if r.get('success')) / successful_tests
            total_documents = sum(r.get('documents_used', 0) for r in self.test_results if r.get('success'))
            total_tokens = sum(r.get('tokens', {}).get('total_tokens', 0) 
                             for r in self.test_results if r.get('success') and r.get('tokens'))
            
            print(f"⚡ Avg Processing Time: {avg_processing_time:.2f}s")
            print(f"📚 Total Documents Used: {total_documents}")
            if total_tokens > 0:
                print(f"🔢 Total Tokens Used: {total_tokens}")
        
        # Detailed results
        print(f"\n📋 Detailed Results:")
        for result in self.test_results:
            status = "✅" if result.get('success') else "❌"
            print(f"   {status} Test {result['test_number']}: {result['subject'][:50]}...")
            if result.get('success'):
                analysis = result.get('analysis', {})
                print(f"      Features: {analysis.get('features_found', 0)}/{analysis.get('total_features', 0)}")
                print(f"      Pricing: {'Yes' if analysis.get('has_pricing') else 'No'}")
                print(f"      Professional: {'Yes' if analysis.get('professional_tone') else 'No'}")
        
        # Save results
        results_file = f"test-results-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump({
                "summary": {
                    "successful_tests": successful_tests,
                    "total_tests": total_tests,
                    "success_rate": f"{(successful_tests/total_tests*100):.1f}%",
                    "test_date": datetime.now().isoformat()
                },
                "results": self.test_results
            }, f, indent=2)
        
        print(f"\n💾 Results saved to: {results_file}")
        
        # Send final summary to Slack
        self.slack.log("📊 Enhanced RAG Testing Complete", "success" if successful_tests == total_tests else "warning", {
            "success_rate": f"{(successful_tests/total_tests*100):.1f}%",
            "successful": successful_tests,
            "total": total_tests,
            "vector_store": "AssistantVectorStore_Jasmin",
            "assistant_type": "Azure OpenAI Assistant with RAG"
        })
        
        return successful_tests == total_tests

def main():
    """Main execution"""
    tester = EnhancedRAGTester()
    success = tester.run_all_tests()
    
    if success:
        print(f"\n🎉 ALL TESTS PASSED! Enhanced RAG system is working perfectly.")
        return True
    else:
        print(f"\n⚠️  Some tests failed. Check the results above.")
        return False

if __name__ == "__main__":
    main()