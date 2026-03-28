#!/usr/bin/env python3
"""
Quick test script for AI Marketplace Assistant API

Tests all implemented endpoints from Stages 1 and 2.
"""

import httpx
import asyncio
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"
COLORS = {
    'green': '\033[92m',
    'red': '\033[91m',
    'blue': '\033[94m',
    'yellow': '\033[93m',
    'end': '\033[0m'
}


def print_success(message):
    print(f"{COLORS['green']}✓ {message}{COLORS['end']}")


def print_error(message):
    print(f"{COLORS['red']}✗ {message}{COLORS['end']}")


def print_info(message):
    print(f"{COLORS['blue']}ℹ {message}{COLORS['end']}")


def print_section(message):
    print(f"\n{COLORS['yellow']}{'='*60}")
    print(f"  {message}")
    print(f"{'='*60}{COLORS['end']}\n")


async def test_endpoint(client, method, url, description, **kwargs):
    """Test a single endpoint"""
    try:
        response = await client.request(method, url, **kwargs)
        if response.status_code < 400:
            print_success(f"{description} - Status: {response.status_code}")
            return True, response.json()
        else:
            print_error(f"{description} - Status: {response.status_code}")
            return False, None
    except Exception as e:
        print_error(f"{description} - Error: {str(e)}")
        return False, None


async def main():
    print_section("🧪 AI Marketplace Assistant - API Testing")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        success_count = 0
        total_count = 0
        
        # Test 1: Health Check
        print_section("Test 1: Health Check")
        total_count += 1
        success, data = await test_endpoint(
            client, "GET", f"{BASE_URL}/health",
            "Health check endpoint"
        )
        if success:
            success_count += 1
            print_info(f"Database: {data.get('database')}")
            print_info(f"Redis: {data.get('redis')}")
            print_info(f"Status: {data.get('status')}")
        
        # Test 2: API Root
        print_section("Test 2: API Root")
        total_count += 1
        success, data = await test_endpoint(
            client, "GET", f"{BASE_URL}/",
            "API root endpoint"
        )
        if success:
            success_count += 1
            print_info(f"App: {data.get('name')}")
            print_info(f"Version: {data.get('version')}")
        
        # Test 3: Products List
        print_section("Test 3: Products")
        total_count += 1
        success, data = await test_endpoint(
            client, "GET", f"{BASE_URL}/products/",
            "Get products list",
            params={"limit": 5}
        )
        if success:
            success_count += 1
            products = data.get('cards', [])
            print_info(f"Products retrieved: {len(products)}")
            if products:
                print_info(f"First product: {products[0]['title']}")
        
        # Test 4: Product by ID
        print_section("Test 4: Product by ID")
        total_count += 1
        success, data = await test_endpoint(
            client, "GET", f"{BASE_URL}/products/10001",
            "Get product by ID"
        )
        if success:
            success_count += 1
            print_info(f"Product: {data.get('title')}")
            print_info(f"Brand: {data.get('brand')}")
        
        # Test 5: Categories
        print_section("Test 5: Categories")
        total_count += 1
        success, data = await test_endpoint(
            client, "GET", f"{BASE_URL}/products/reference/categories",
            "Get categories"
        )
        if success:
            success_count += 1
            print_info(f"Categories: {len(data)}")
        
        # Test 6: Brands
        print_section("Test 6: Brands")
        total_count += 1
        success, data = await test_endpoint(
            client, "GET", f"{BASE_URL}/products/reference/brands",
            "Get brands"
        )
        if success:
            success_count += 1
            print_info(f"Brands: {len(data)}")
            if data:
                print_info(f"First brand: {data[0]['name']}")
        
        # Test 7: Feedbacks List
        print_section("Test 7: Feedbacks")
        total_count += 1
        success, data = await test_endpoint(
            client, "GET", f"{BASE_URL}/feedbacks/",
            "Get feedbacks list",
            params={"take": 10}
        )
        if success:
            success_count += 1
            feedbacks = data.get('feedbacks', [])
            print_info(f"Feedbacks: {len(feedbacks)}")
            print_info(f"Unanswered: {data.get('countUnanswered')}")
        
        # Test 8: Unanswered Feedbacks
        print_section("Test 8: Unanswered Feedbacks")
        total_count += 1
        success, data = await test_endpoint(
            client, "GET", f"{BASE_URL}/feedbacks/",
            "Get unanswered feedbacks",
            params={"is_answered": False, "take": 5}
        )
        if success:
            success_count += 1
            feedbacks = data.get('feedbacks', [])
            print_info(f"Unanswered feedbacks: {len(feedbacks)}")
        
        # Test 9: Feedback Stats
        print_section("Test 9: Feedback Stats")
        total_count += 1
        success, data = await test_endpoint(
            client, "GET", f"{BASE_URL}/feedbacks/stats/unanswered",
            "Get unanswered feedback count"
        )
        if success:
            success_count += 1
            print_info(f"Count: {data.get('countUnanswered')}")
        
        # Test 10: Questions
        print_section("Test 10: Questions")
        total_count += 1
        success, data = await test_endpoint(
            client, "GET", f"{BASE_URL}/feedbacks/questions",
            "Get questions list",
            params={"take": 5}
        )
        if success:
            success_count += 1
            questions = data.get('questions', [])
            print_info(f"Questions: {len(questions)}")
            print_info(f"Unanswered: {data.get('countUnanswered')}")
        
        # Test 11: Sales
        print_section("Test 11: Sales")
        total_count += 1
        success, data = await test_endpoint(
            client, "GET", f"{BASE_URL}/sales/",
            "Get sales report",
            params={"limit": 20}
        )
        if success:
            success_count += 1
            sales = data.get('sales', [])
            print_info(f"Sales: {len(sales)}")
            print_info(f"Total: {data.get('total')}")
            if sales:
                total_amount = sum(s.get('forPay', 0) for s in sales)
                print_info(f"Total amount: {total_amount:.2f} руб")
        
        # Test 12: Orders
        print_section("Test 12: Orders")
        total_count += 1
        success, data = await test_endpoint(
            client, "GET", f"{BASE_URL}/sales/orders",
            "Get orders report",
            params={"limit": 10}
        )
        if success:
            success_count += 1
            orders = data.get('orders', [])
            print_info(f"Orders: {len(orders)}")
            print_info(f"Total: {data.get('total')}")
        
        # Test 13: Stocks
        print_section("Test 13: Stocks")
        total_count += 1
        success, data = await test_endpoint(
            client, "GET", f"{BASE_URL}/sales/stocks",
            "Get stocks report"
        )
        if success:
            success_count += 1
            stocks = data.get('stocks', [])
            print_info(f"Stock items: {len(stocks)}")
            print_info(f"Total: {data.get('total')}")
            if stocks:
                total_quantity = sum(s.get('quantity', 0) for s in stocks)
                print_info(f"Total quantity: {total_quantity}")
        
        # Final Results
        print_section("📊 Test Results")
        print_info(f"Tests passed: {success_count}/{total_count}")
        
        if success_count == total_count:
            print_success("All tests passed! ✨")
            print_info("\n🎉 System is working correctly!")
            print_info("You can now:")
            print_info("  1. Open Swagger UI: http://localhost:8000/docs")
            print_info("  2. Test interactively in browser")
            print_info("  3. Proceed to Stage 3")
        else:
            print_error(f"\n{total_count - success_count} tests failed")
            print_info("Check the logs above for details")
        
        return success_count == total_count


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        exit(0 if result else 1)
    except KeyboardInterrupt:
        print_error("\n\nTests interrupted by user")
        exit(1)
    except Exception as e:
        print_error(f"\n\nUnexpected error: {e}")
        exit(1)
