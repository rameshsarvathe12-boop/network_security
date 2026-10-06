import requests
import sys
import json
from datetime import datetime
import time

class IoTSecurityMonitorTester:
    def __init__(self, base_url="https://3462f3e1-8798-4c50-b983-51450bcd5a10.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.device_ids = []
        self.threat_ids = []

    def run_test(self, name, method, endpoint, expected_status, data=None, timeout=10):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return True, response.json()
                except:
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timed out after {timeout} seconds")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_endpoint(self):
        """Test health check endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "api/health",
            200
        )
        if success and isinstance(response, dict):
            print(f"   Health Status: {response.get('status', 'unknown')}")
            print(f"   Timestamp: {response.get('timestamp', 'unknown')}")
        return success

    def test_dashboard_endpoint(self):
        """Test dashboard data endpoint"""
        success, response = self.run_test(
            "Dashboard Data",
            "GET",
            "api/dashboard",
            200
        )
        if success and isinstance(response, dict):
            print(f"   Total Devices: {response.get('total_devices', 0)}")
            print(f"   Online Devices: {response.get('online_devices', 0)}")
            print(f"   Security Score: {response.get('avg_security_score', 0)}")
            print(f"   Network Status: {response.get('network_status', 'unknown')}")
            print(f"   Active Threats: {response.get('critical_threats', 0) + response.get('high_threats', 0)}")
        return success

    def test_devices_endpoint(self):
        """Test devices list endpoint"""
        success, response = self.run_test(
            "Devices List",
            "GET",
            "api/devices",
            200
        )
        if success and isinstance(response, dict) and 'devices' in response:
            devices = response['devices']
            print(f"   Found {len(devices)} devices")
            if devices:
                # Store device IDs for later tests
                self.device_ids = [device['device_id'] for device in devices[:3]]  # Store first 3
                sample_device = devices[0]
                print(f"   Sample Device: {sample_device.get('device_name', 'unknown')}")
                print(f"   Device Type: {sample_device.get('device_type', 'unknown')}")
                print(f"   Status: {sample_device.get('status', 'unknown')}")
                print(f"   Security Score: {sample_device.get('security_score', 0)}")
        return success

    def test_device_details_endpoint(self):
        """Test individual device details endpoint"""
        if not self.device_ids:
            print("⚠️  Skipping device details test - no device IDs available")
            return True
        
        device_id = self.device_ids[0]
        success, response = self.run_test(
            f"Device Details ({device_id[:8]}...)",
            "GET",
            f"api/devices/{device_id}",
            200
        )
        if success and isinstance(response, dict):
            device = response.get('device', {})
            recent_logs = response.get('recent_logs', [])
            recent_threats = response.get('recent_threats', [])
            print(f"   Device Name: {device.get('device_name', 'unknown')}")
            print(f"   Recent Logs: {len(recent_logs)}")
            print(f"   Recent Threats: {len(recent_threats)}")
        return success

    def test_threats_endpoint(self):
        """Test threats list endpoint"""
        success, response = self.run_test(
            "Threats List",
            "GET",
            "api/threats",
            200
        )
        if success and isinstance(response, dict) and 'threats' in response:
            threats = response['threats']
            print(f"   Found {len(threats)} threats")
            if threats:
                # Store threat IDs for later tests
                self.threat_ids = [threat['alert_id'] for threat in threats[:3] if not threat.get('resolved', False)]
                sample_threat = threats[0]
                print(f"   Sample Threat: {sample_threat.get('threat_type', 'unknown')}")
                print(f"   Severity: {sample_threat.get('severity', 'unknown')}")
                print(f"   Resolved: {sample_threat.get('resolved', False)}")
                print(f"   Confidence: {sample_threat.get('confidence_score', 0)}")
        return success

    def test_resolve_threat_endpoint(self):
        """Test threat resolution endpoint"""
        if not self.threat_ids:
            print("⚠️  Skipping threat resolution test - no unresolved threat IDs available")
            return True
        
        threat_id = self.threat_ids[0]
        success, response = self.run_test(
            f"Resolve Threat ({threat_id[:8]}...)",
            "POST",
            f"api/threats/{threat_id}/resolve",
            200
        )
        if success and isinstance(response, dict):
            print(f"   Message: {response.get('message', 'unknown')}")
        return success

    def test_invalid_endpoints(self):
        """Test invalid endpoints return proper error codes"""
        print("\n🔍 Testing Invalid Endpoints...")
        
        # Test non-existent device
        success, _ = self.run_test(
            "Non-existent Device",
            "GET",
            "api/devices/invalid-device-id",
            404
        )
        
        # Test non-existent threat resolution
        success2, _ = self.run_test(
            "Non-existent Threat Resolution",
            "POST",
            "api/threats/invalid-threat-id/resolve",
            404
        )
        
        return success and success2

    def wait_for_ai_threats(self):
        """Wait for AI system to generate some threats"""
        print("\n⏳ Waiting for AI threat detection system (10 seconds)...")
        time.sleep(12)  # Wait a bit longer than the 10-second cycle
        
        # Check if new threats were generated
        success, response = self.run_test(
            "AI Generated Threats Check",
            "GET",
            "api/threats",
            200
        )
        
        if success and isinstance(response, dict) and 'threats' in response:
            threats = response['threats']
            recent_threats = [t for t in threats if not t.get('resolved', False)]
            print(f"   Active threats after AI analysis: {len(recent_threats)}")
            
            # Show some threat types if available
            threat_types = set(t.get('threat_type', 'unknown') for t in recent_threats[:5])
            if threat_types:
                print(f"   Threat types detected: {', '.join(threat_types)}")
        
        return success

def main():
    print("🚀 Starting 5G IoT Security Monitor API Tests")
    print("=" * 60)
    
    # Setup
    tester = IoTSecurityMonitorTester()
    
    # Run all tests
    test_results = []
    
    # Basic API tests
    test_results.append(tester.test_health_endpoint())
    test_results.append(tester.test_dashboard_endpoint())
    test_results.append(tester.test_devices_endpoint())
    test_results.append(tester.test_device_details_endpoint())
    test_results.append(tester.test_threats_endpoint())
    test_results.append(tester.test_resolve_threat_endpoint())
    
    # Wait for AI system and test again
    test_results.append(tester.wait_for_ai_threats())
    
    # Error handling tests
    test_results.append(tester.test_invalid_endpoints())

    # Print final results
    print("\n" + "=" * 60)
    print(f"📊 FINAL RESULTS")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed! Backend API is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())