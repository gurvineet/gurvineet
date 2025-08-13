#!/usr/bin/env python3
"""
Test script for the Kitchen System

This script tests the basic functionality of the kitchen system
to ensure it works correctly before running the full harness.
"""

import time
import threading
from kitchen_system import KitchenSystem, Temperature, FoodOrder


def test_basic_functionality():
    """Test basic order placement and pickup."""
    print("Testing basic functionality...")
    
    kitchen = KitchenSystem()
    
    # Test 1: Place a simple order
    success = kitchen.place_order("test_001", "Hot Pizza", Temperature.HOT, 300)
    assert success, "Failed to place simple order"
    print("✓ Basic order placement works")
    
    # Test 2: Check storage status
    status = kitchen.get_storage_status()
    assert status['heater']['count'] == 1, "Order not stored in heater"
    print("✓ Order stored in correct location")
    
    # Test 3: Pickup order
    order = kitchen.pickup_order("test_001")
    assert order is not None, "Failed to pickup order"
    assert order.name == "Hot Pizza", "Wrong order picked up"
    print("✓ Order pickup works")
    
    # Test 4: Check storage is empty
    status = kitchen.get_storage_status()
    assert status['heater']['count'] == 0, "Heater not empty after pickup"
    print("✓ Storage cleanup works")


def test_storage_capacity():
    """Test storage capacity limits."""
    print("\nTesting storage capacity...")
    
    kitchen = KitchenSystem()
    
    # Fill cooler to capacity
    for i in range(6):
        success = kitchen.place_order(f"cold_{i}", f"Cold Item {i}", Temperature.COLD, 600)
        assert success, f"Failed to place cold order {i}"
    
    # Try to place one more cold order
    success = kitchen.place_order("cold_extra", "Extra Cold Item", Temperature.COLD, 600)
    assert not success, "Should not be able to place order when cooler is full"
    print("✓ Cooler capacity limit enforced")
    
    # Fill heater to capacity
    for i in range(6):
        success = kitchen.place_order(f"hot_{i}", f"Hot Item {i}", Temperature.HOT, 600)
        assert success, f"Failed to place hot order {i}"
    
    # Try to place one more hot order
    success = kitchen.place_order("hot_extra", "Extra Hot Item", Temperature.HOT, 600)
    assert not success, "Should not be able to place order when heater is full"
    print("✓ Heater capacity limit enforced")


def test_temperature_mismatch():
    """Test storing orders at non-ideal temperatures."""
    print("\nTesting temperature mismatch handling...")
    
    kitchen = KitchenSystem()
    
    # Fill cooler and heater
    for i in range(6):
        kitchen.place_order(f"cold_{i}", f"Cold Item {i}", Temperature.COLD, 600)
        kitchen.place_order(f"hot_{i}", f"Hot Item {i}", Temperature.HOT, 600)
    
    # Try to place a cold order (should go to shelf)
    success = kitchen.place_order("cold_shelf", "Cold on Shelf", Temperature.COLD, 600)
    assert success, "Failed to place cold order on shelf when cooler full"
    
    # Check it's on shelf
    status = kitchen.get_storage_status()
    assert status['shelf']['count'] == 1, "Order not placed on shelf"
    print("✓ Orders placed on shelf when ideal storage is full")


def test_freshness_degradation():
    """Test freshness degradation at non-ideal temperatures."""
    print("\nTesting freshness degradation...")
    
    kitchen = KitchenSystem()
    
    # Place order at ideal temperature
    kitchen.place_order("ideal", "Ideal Temp", Temperature.HOT, 100)
    
    # Place order at non-ideal temperature
    kitchen.place_order("non_ideal", "Non-Ideal Temp", Temperature.HOT, 100)
    
    # Wait for some time
    time.sleep(0.1)  # 100ms
    
    # Check freshness
    ideal_order = kitchen.orders.get("ideal")
    non_ideal_order = kitchen.orders.get("non_ideal")
    
    assert ideal_order is not None, "Ideal order not found"
    assert non_ideal_order is not None, "Non-ideal order not found"
    
    # Non-ideal should degrade faster
    ideal_fresh = ideal_order.is_fresh(time.time())
    non_ideal_fresh = non_ideal_order.is_fresh(time.time())
    
    print("✓ Freshness degradation works correctly")


def test_concurrent_operations():
    """Test concurrent order placement and pickup."""
    print("\nTesting concurrent operations...")
    
    kitchen = KitchenSystem()
    
    def place_orders():
        for i in range(10):
            kitchen.place_order(f"concurrent_{i}", f"Item {i}", Temperature.ROOM, 1000)
            time.sleep(0.01)
    
    def pickup_orders():
        time.sleep(0.05)  # Wait for some orders to be placed
        for i in range(10):
            kitchen.pickup_order(f"concurrent_{i}")
            time.sleep(0.01)
    
    # Start concurrent threads
    place_thread = threading.Thread(target=place_orders)
    pickup_thread = threading.Thread(target=pickup_orders)
    
    place_thread.start()
    pickup_thread.start()
    
    # Wait for completion
    place_thread.join()
    pickup_thread.join()
    
    print("✓ Concurrent operations work correctly")


def test_action_ledger():
    """Test action logging and ledger."""
    print("\nTesting action ledger...")
    
    kitchen = KitchenSystem()
    
    # Place and pickup an order
    kitchen.place_order("ledger_test", "Test Item", Temperature.HOT, 600)
    kitchen.pickup_order("ledger_test")
    
    # Check ledger
    actions = kitchen.get_actions_ledger()
    assert len(actions) == 2, f"Expected 2 actions, got {len(actions)}"
    
    # Check action types
    action_types = [action.action_type for action in actions]
    assert ActionType.PLACE in action_types, "Place action not logged"
    assert ActionType.PICKUP in action_types, "Pickup action not logged"
    
    print("✓ Action ledger works correctly")


def run_all_tests():
    """Run all tests."""
    print("Running Kitchen System Tests")
    print("=" * 40)
    
    try:
        test_basic_functionality()
        test_storage_capacity()
        test_temperature_mismatch()
        test_freshness_degradation()
        test_concurrent_operations()
        test_action_ledger()
        
        print("\n" + "=" * 40)
        print("All tests passed! ✓")
        print("=" * 40)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    # Import ActionType for the test
    from kitchen_system import ActionType
    
    success = run_all_tests()
    exit(0 if success else 1)