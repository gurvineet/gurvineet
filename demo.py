#!/usr/bin/env python3
"""
Simple Demo for CloudKitchens Kitchen Workflow Optimization System

This script demonstrates the core functionality without the full demo.
"""
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.food_item import FoodItem, FoodCategory
from models.order import Order, OrderStatus, OrderPriority
from services.kitchen_service import KitchenService


def simple_demo():
    """Run a simple demonstration of the system."""
    print("CloudKitchens Kitchen Workflow Optimization - Simple Demo")
    print("=" * 50)
    
    # Initialize service
    service = KitchenService()
    
    # Create a simple food item
    kale = FoodItem(
        id="KALE_001",
        name="Fresh Kale",
        category=FoodCategory.PERISHABLE,
        spoilage_rate_hours=48,
        current_quantity=5.0,
        min_quantity=2.0,
        max_quantity=10.0,
        unit="kg",
        cost_per_unit=8.50,
        preparation_time_minutes=15
    )
    
    # Add to inventory
    service.add_food_item(kale)
    print(f"✓ Added {kale.name} to inventory")
    
    # Create an order
    order = service.create_order(
        customer_id="CUST_001",
        items=[("KALE_001", 1.5, "Organic please")],
        priority=OrderPriority.HIGH
    )
    
    if order:
        print(f"✓ Created order {order.id}")
        print(f"  Customer: {order.customer_id}")
        print(f"  Priority: {order.priority.value}")
        print(f"  Status: {order.status.value}")
        print(f"  Items: {len(order.items)}")
        print(f"  Total Cost: ${order.get_total_cost():.2f}")
        
        # Show inventory summary
        summary = service.get_inventory_summary()
        print(f"\nInventory Summary:")
        print(f"  Total Items: {summary['total_items']}")
        print(f"  Total Value: ${summary['total_value']:.2f}")
        
        # Optimize workflow
        print(f"\nOptimizing workflow...")
        result = service.optimize_workflow()
        print(f"✓ Optimization complete!")
        print(f"  Efficiency Score: {result.efficiency_score:.3f}")
        print(f"  Orders in sequence: {len(result.optimized_order_sequence)}")
        
    else:
        print("✗ Failed to create order")
    
    print("\nDemo completed successfully!")


if __name__ == '__main__':
    simple_demo()