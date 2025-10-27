#!/usr/bin/env python3
"""
Demo script for the Food Order Fulfillment System

This script demonstrates the basic functionality of the kitchen system
with a simple example scenario.
"""

import time
from kitchen_system import KitchenSystem, Temperature


def run_demo():
    """Run a simple demonstration of the kitchen system."""
    print("🍕 Food Order Fulfillment System Demo")
    print("=" * 50)
    
    # Initialize the kitchen
    kitchen = KitchenSystem()
    
    print("Kitchen initialized with empty storage:")
    print_storage_status(kitchen)
    
    # Scenario 1: Place some orders
    print("\n📦 Placing orders...")
    
    orders = [
        ("pizza_001", "Margherita Pizza", Temperature.HOT, 300),
        ("salad_001", "Caesar Salad", Temperature.COLD, 600),
        ("bread_001", "Fresh Baguette", Temperature.ROOM, 1200),
        ("ice_cream_001", "Vanilla Ice Cream", Temperature.COLD, 900),
        ("soup_001", "Tomato Soup", Temperature.HOT, 600),
    ]
    
    for order_id, name, temp, freshness in orders:
        success = kitchen.place_order(order_id, name, temp, freshness)
        if success:
            print(f"  ✓ {name} placed successfully")
        else:
            print(f"  ❌ Failed to place {name}")
    
    print("\nStorage status after placing orders:")
    print_storage_status(kitchen)
    
    # Scenario 2: Show some pickups
    print("\n🚚 Picking up orders...")
    
    # Pickup pizza
    order = kitchen.pickup_order("pizza_001")
    if order:
        print(f"  ✓ {order.name} picked up successfully")
    else:
        print(f"  ❌ Failed to pickup pizza_001")
    
    # Pickup salad
    order = kitchen.pickup_order("salad_001")
    if order:
        print(f"  ✓ {order.name} picked up successfully")
    else:
        print(f"  ❌ Failed to pickup salad_001")
    
    print("\nStorage status after pickups:")
    print_storage_status(kitchen)
    
    # Scenario 3: Show action ledger
    print("\n📋 Action Ledger:")
    actions = kitchen.get_actions_ledger()
    for action in actions:
        dt = time.strftime("%H:%M:%S", time.localtime(action.timestamp))
        print(f"  [{dt}] {action.action_type.value.upper()}: {action.order_id} -> {action.target}")
    
    # Scenario 4: Show statistics
    print("\n📊 System Statistics:")
    stats = kitchen.get_statistics()
    for key, value in stats.items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
    
    print("\n🎉 Demo completed successfully!")


def print_storage_status(kitchen):
    """Print the current storage status."""
    status = kitchen.get_storage_status()
    
    for location, info in status.items():
        print(f"  {location.title()}: {info['count']}/{info['capacity']} orders")
        for order in info['orders']:
            print(f"    - {order['name']} ({order['temperature']})")


if __name__ == "__main__":
    run_demo()