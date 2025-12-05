"""
API Testing Script

Test all backend endpoints to verify functionality.
"""

import requests
import json
from typing import Dict, Any


class BackendTester:
    """Test backend API endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.token = None
        self.test_user_id = 1  # Use existing user from dataset
        
    def print_result(self, test_name: str, success: bool, message: str = ""):
        """Print test result"""
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status} - {test_name}")
        if message:
            print(f"      {message}")
    
    def test_health(self) -> bool:
        """Test health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health")
            success = response.status_code == 200
            self.print_result("Health Check", success, f"Status: {response.status_code}")
            return success
        except Exception as e:
            self.print_result("Health Check", False, str(e))
            return False
    
    def test_login(self) -> bool:
        """Test login endpoint"""
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                json={"user_id": self.test_user_id}
            )
            success = response.status_code == 200
            
            if success:
                data = response.json()
                self.token = data.get('token')
                self.print_result("Login", True, f"Token received")
            else:
                self.print_result("Login", False, f"Status: {response.status_code}")
            
            return success
        except Exception as e:
            self.print_result("Login", False, str(e))
            return False
    
    def test_get_animes(self) -> bool:
        """Test get animes list"""
        try:
            response = requests.get(
                f"{self.base_url}/api/anime",
                params={"page": 1, "limit": 10}
            )
            success = response.status_code == 200
            
            if success:
                data = response.json()
                count = len(data.get('animes', []))
                self.print_result("Get Animes", True, f"Retrieved {count} animes")
            else:
                self.print_result("Get Animes", False, f"Status: {response.status_code}")
            
            return success
        except Exception as e:
            self.print_result("Get Animes", False, str(e))
            return False
    
    def test_get_anime_detail(self) -> bool:
        """Test get single anime"""
        try:
            response = requests.get(f"{self.base_url}/api/anime/1")
            success = response.status_code == 200
            
            if success:
                data = response.json()
                anime = data.get('anime', {})
                self.print_result("Get Anime Detail", True, f"Anime: {anime.get('name', 'N/A')}")
            else:
                self.print_result("Get Anime Detail", False, f"Status: {response.status_code}")
            
            return success
        except Exception as e:
            self.print_result("Get Anime Detail", False, str(e))
            return False
    
    def test_search_anime(self) -> bool:
        """Test anime search"""
        try:
            response = requests.get(
                f"{self.base_url}/api/anime/search",
                params={"q": "Naruto"}
            )
            success = response.status_code == 200
            
            if success:
                data = response.json()
                count = len(data.get('animes', []))
                self.print_result("Search Anime", True, f"Found {count} results")
            else:
                self.print_result("Search Anime", False, f"Status: {response.status_code}")
            
            return success
        except Exception as e:
            self.print_result("Search Anime", False, str(e))
            return False
    
    def test_get_recommendations(self) -> bool:
        """Test ML-powered recommendations"""
        if not self.token:
            self.print_result("Get Recommendations", False, "No auth token")
            return False
        
        try:
            response = requests.get(
                f"{self.base_url}/api/recommendation",
                params={"limit": 10},
                headers={"Authorization": f"Bearer {self.token}"}
            )
            success = response.status_code == 200
            
            if success:
                data = response.json()
                count = len(data.get('recommendations', []))
                model = data.get('model_used', 'unknown')
                self.print_result("Get Recommendations", True, f"{count} recommendations from {model}")
            else:
                self.print_result("Get Recommendations", False, f"Status: {response.status_code}")
            
            return success
        except Exception as e:
            self.print_result("Get Recommendations", False, str(e))
            return False
    
    def test_get_similar_animes(self) -> bool:
        """Test similar animes (content-based)"""
        try:
            response = requests.get(
                f"{self.base_url}/api/recommendation/similar/1",
                params={"limit": 10, "use_content": "true"}
            )
            success = response.status_code == 200
            
            if success:
                data = response.json()
                count = len(data.get('similar_animes', []))
                method = data.get('method', 'unknown')
                self.print_result("Get Similar Animes", True, f"{count} similar animes ({method})")
            else:
                self.print_result("Get Similar Animes", False, f"Status: {response.status_code}")
            
            return success
        except Exception as e:
            self.print_result("Get Similar Animes", False, str(e))
            return False
    
    def test_admin_stats(self) -> bool:
        """Test admin stats endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/admin/stats")
            success = response.status_code == 200
            
            if success:
                data = response.json()
                stats = data.get('stats', {})
                self.print_result("Admin Stats", True, 
                    f"Users: {stats.get('total_users')}, Animes: {stats.get('total_animes')}")
            else:
                self.print_result("Admin Stats", False, f"Status: {response.status_code}")
            
            return success
        except Exception as e:
            self.print_result("Admin Stats", False, str(e))
            return False
    
    def test_admin_models(self) -> bool:
        """Test admin models endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/admin/models")
            success = response.status_code == 200
            
            if success:
                data = response.json()
                models = data.get('models', [])
                self.print_result("Admin Models", True, f"{len(models)} models available")
            else:
                self.print_result("Admin Models", False, f"Status: {response.status_code}")
            
            return success
        except Exception as e:
            self.print_result("Admin Models", False, str(e))
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("=" * 60)
        print("BACKEND API TESTING")
        print("=" * 60)
        print(f"Base URL: {self.base_url}\n")
        
        results = []
        
        # Basic tests
        print("Basic Endpoints:")
        results.append(("Health Check", self.test_health()))
        results.append(("Login", self.test_login()))
        
        print("\nAnime Endpoints:")
        results.append(("Get Animes", self.test_get_animes()))
        results.append(("Get Anime Detail", self.test_get_anime_detail()))
        results.append(("Search Anime", self.test_search_anime()))
        
        print("\nRecommendation Endpoints (ML):")
        results.append(("Get Recommendations", self.test_get_recommendations()))
        results.append(("Get Similar Animes", self.test_get_similar_animes()))
        
        print("\nAdmin Endpoints:")
        results.append(("Admin Stats", self.test_admin_stats()))
        results.append(("Admin Models", self.test_admin_models()))
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, success in results if success)
        total = len(results)
        
        print(f"Passed: {passed}/{total}")
        print(f"Failed: {total - passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("\n✓ All tests passed!")
        else:
            print("\n✗ Some tests failed. Check server logs.")
        
        return passed == total


if __name__ == '__main__':
    tester = BackendTester()
    tester.run_all_tests()
