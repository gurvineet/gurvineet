#!/usr/bin/env python3
"""
CloudKitchens Kitchen Workflow Optimization - Main Application

This is the main entry point for the kitchen workflow optimization system.
It demonstrates the core functionality with sample data and optimization scenarios.
"""

import sys
import time
from datetime import datetime, timedelta
from typing import List

from models.food_item import FoodItem, FoodCategory
from models.order import Order, OrderStatus, OrderPriority
from services.kitchen_service import KitchenService
from algorithms.workflow_optimizer import WorkflowOptimizer


def create_sample_inventory() -> List[FoodItem]:
    """Create sample food items for demonstration."""
    items = [
        # Perishable items (high spoilage risk)
        FoodItem(
            id="KALE_001",
            name="Fresh Kale",
            category=FoodCategory.PERISHABLE,
            spoilage_rate_hours=48,  # 2 days
            current_quantity=5.0,
            min_quantity=2.0,
            max_quantity=10.0,
            unit="kg",
            cost_per_unit=8.50,
            preparation_time_minutes=15,
            storage_requirements="Refrigerated"
        ),
        FoodItem(
            id="MILK_001",
            name="Organic Milk",
            category=FoodCategory.PERISHABLE,
            spoilage_rate_hours=72,  # 3 days
            current_quantity=8.0,
            min_quantity=3.0,
            max_quantity=15.0,
            unit="liters",
            cost_per_unit=4.20,
            preparation_time_minutes=5,
            storage_requirements="Refrigerated"
        ),
        FoodItem(
            id="BANANA_001",
            name="Fresh Bananas",
            category=FoodCategory.PERISHABLE,
            spoilage_rate_hours=120,  # 5 days
            current_quantity=12.0,
            min_quantity=5.0,
            max_quantity=20.0,
            unit="pieces",
            cost_per_unit=0.30,
            preparation_time_minutes=3,
            storage_requirements="Room temperature"
        ),
        
        # Semi-perishable items
        FoodItem(
            id="BREAD_001",
            name="Artisan Bread",
            category=FoodCategory.SEMI_PERISHABLE,
            spoilage_rate_hours=168,  # 7 days
            current_quantity=20.0,
            min_quantity=8.0,
            max_quantity=30.0,
            unit="pieces",
            cost_per_unit=3.50,
            preparation_time_minutes=8,
            storage_requirements="Room temperature"
        ),
        FoodItem(
            id="CHEESE_001",
            name="Aged Cheddar",
            category=FoodCategory.SEMI_PERISHABLE,
            spoilage_rate_hours=240,  # 10 days
            current_quantity=6.0,
            min_quantity=2.0,
            max_quantity=12.0,
            unit="kg",
            cost_per_unit=12.00,
            preparation_time_minutes=10,
            storage_requirements="Refrigerated"
        ),
        
        # Non-perishable items
        FoodItem(
            id="RICE_001",
            name="Basmati Rice",
            category=FoodCategory.NON_PERISHABLE,
            spoilage_rate_hours=8760,  # 1 year
            current_quantity=25.0,
            min_quantity=10.0,
            max_quantity=50.0,
            unit="kg",
            cost_per_unit=2.80,
            preparation_time_minutes=25,
            storage_requirements="Dry storage"
        ),
        FoodItem(
            id="OIL_001",
            name="Olive Oil",
            category=FoodCategory.NON_PERISHABLE,
            spoilage_rate_hours=8760,  # 1 year
            current_quantity=15.0,
            min_quantity=5.0,
            max_quantity=25.0,
            unit="liters",
            cost_per_unit=8.00,
            preparation_time_minutes=2,
            storage_requirements="Dry storage"
        ),
        
        # Frozen items
        FoodItem(
            id="ICE_001",
            name="Ice Cubes",
            category=FoodCategory.FROZEN,
            spoilage_rate_hours=720,  # 30 days
            current_quantity=100.0,
            min_quantity=20.0,
            max_quantity=200.0,
            unit="kg",
            cost_per_unit=0.50,
            preparation_time_minutes=1,
            storage_requirements="Frozen"
        ),
        FoodItem(
            id="FROZEN_VEG_001",
            name="Frozen Mixed Vegetables",
            category=FoodCategory.FROZEN,
            spoilage_rate_hours=8760,  # 1 year
            current_quantity=18.0,
            min_quantity=5.0,
            max_quantity=30.0,
            unit="kg",
            cost_per_unit=3.20,
            preparation_time_minutes=12,
            storage_requirements="Frozen"
        )
    ]
    
    return items


def create_sample_orders(kitchen_service: KitchenService) -> List[Order]:
    """Create sample orders for demonstration."""
    orders = []
    
    # Order 1: High priority, perishable items
    order1 = kitchen_service.create_order(
        customer_id="CUST_001",
        items=[
            ("KALE_001", 1.5, "Wash thoroughly"),
            ("MILK_001", 2.0, "Cold delivery"),
            ("BANANA_001", 6.0, "Ripe but not overripe")
        ],
        priority=OrderPriority.HIGH,
        delivery_address="123 Main St, Downtown",
        notes="Customer has dairy allergy - use almond milk if available"
    )
    if order1:
        orders.append(order1)
    
    # Order 2: Normal priority, mixed items
    order2 = kitchen_service.create_order(
        customer_id="CUST_002",
        items=[
            ("BREAD_001", 3.0, "Fresh baked"),
            ("CHEESE_001", 0.5, "Extra sharp"),
            ("RICE_001", 2.0, "Long grain preferred")
        ],
        priority=OrderPriority.NORMAL,
        delivery_address="456 Oak Ave, Midtown"
    )
    if order2:
        orders.append(order2)
    
    # Order 3: Low priority, non-perishable items
    order3 = kitchen_service.create_order(
        customer_id="CUST_003",
        items=[
            ("OIL_001", 1.0, "Extra virgin"),
            ("FROZEN_VEG_001", 2.0, "Mixed variety")
        ],
        priority=OrderPriority.LOW,
        delivery_address="789 Pine Rd, Uptown"
    )
    if order3:
        orders.append(order3)
    
    # Order 4: Urgent priority, high spoilage risk
    order4 = kitchen_service.create_order(
        customer_id="CUST_004",
        items=[
            ("KALE_001", 2.0, "Organic only"),
            ("MILK_001", 1.0, "Lactose-free"),
            ("ICE_001", 5.0, "For immediate use")
        ],
        priority=OrderPriority.URGENT,
        delivery_address="321 Elm St, Downtown",
        delivery_instructions="Ring doorbell twice"
    )
    if order4:
        orders.append(order4)
    
    # Order 5: Normal priority, bulk order
    order5 = kitchen_service.create_order(
        customer_id="CUST_005",
        items=[
            ("RICE_001", 5.0, "Basmati preferred"),
            ("OIL_001", 3.0, "Any premium brand"),
            ("BREAD_001", 8.0, "Various types")
        ],
        priority=OrderPriority.NORMAL,
        delivery_address="654 Maple Dr, Suburbs",
        notes="Business order for office catering"
    )
    if order5:
        orders.append(order5)
    
    return orders


def demonstrate_workflow_optimization(kitchen_service: KitchenService):
    """Demonstrate the workflow optimization functionality."""
    print("\n" + "="*60)
    print("WORKFLOW OPTIMIZATION DEMONSTRATION")
    print("="*60)
    
    # Get current workflow metrics
    print("\n1. Current Workflow Metrics:")
    metrics = kitchen_service.get_workflow_metrics()
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"   {key.replace('_', ' ').title()}: {value:.3f}")
        else:
            print(f"   {key.replace('_', ' ').title()}: {value}")
    
    # Optimize workflow
    print("\n2. Running Workflow Optimization...")
    start_time = time.time()
    optimization_result = kitchen_service.optimize_workflow()
    optimization_time = time.time() - start_time
    
    print(f"   Optimization completed in {optimization_time:.3f} seconds")
    
    # Display optimization results
    print("\n3. Optimization Results:")
    print(f"   Total Processing Time: {optimization_result.total_processing_time} minutes")
    print(f"   Spoilage Risk Reduction: {optimization_result.spoilage_risk_reduction:.3f}")
    print(f"   Efficiency Score: {optimization_result.efficiency_score:.3f}")
    
    print("\n4. Optimized Order Sequence:")
    for i, order in enumerate(optimization_result.optimized_order_sequence, 1):
        priority_score = order.get_priority_score()
        spoilage_risk = order.get_spoilage_risk_score()
        print(f"   {i:2d}. {order.id} - {order.customer_id}")
        print(f"       Priority: {order.priority.value.upper()}")
        print(f"       Priority Score: {priority_score:.3f}")
        print(f"       Spoilage Risk: {spoilage_risk:.3f}")
        print(f"       Items: {len(order.items)}")
        print(f"       Est. Time: {order.estimated_preparation_time} min")
        print(f"       Total Cost: ${order.get_total_cost():.2f}")
        print()
    
    print("5. Recommendations:")
    for i, recommendation in enumerate(optimization_result.recommendations, 1):
        print(f"   {i}. {recommendation}")


def demonstrate_inventory_management(kitchen_service: KitchenService):
    """Demonstrate inventory management functionality."""
    print("\n" + "="*60)
    print("INVENTORY MANAGEMENT DEMONSTRATION")
    print("="*60)
    
    # Display inventory summary
    print("\n1. Inventory Summary:")
    summary = kitchen_service.get_inventory_summary()
    print(f"   Total Items: {summary['total_items']}")
    print(f"   Total Value: ${summary['total_value']:.2f}")
    print(f"   Low Stock Items: {summary['low_stock_items']}")
    print(f"   High Risk Items: {summary['high_risk_items']}")
    
    print("\n2. Inventory by Category:")
    for category, stats in summary['categories'].items():
        print(f"   {category.title()}:")
        print(f"     Count: {stats['count']}")
        print(f"     Total Quantity: {stats['total_quantity']}")
        print(f"     Total Value: ${stats['total_value']:.2f}")
    
    # Show high-risk items
    print("\n3. High-Risk Items (Spoilage Risk > 0.7):")
    high_risk_items = [item for item in kitchen_service.inventory.values() 
                       if item.spoilage_risk_score > 0.7]
    
    if high_risk_items:
        for item in high_risk_items:
            print(f"   {item.name}: Risk {item.spoilage_risk_score:.3f}")
    else:
        print("   No high-risk items found")
    
    # Show low-stock items
    print("\n4. Low-Stock Items:")
    low_stock_items = [item for item in kitchen_service.inventory.values() 
                       if item.is_low_stock]
    
    if low_stock_items:
        for item in low_stock_items:
            print(f"   {item.name}: {item.current_quantity}{item.unit} "
                  f"(min: {item.min_quantity}{item.unit})")
    else:
        print("   No low-stock items found")


def demonstrate_order_management(kitchen_service: KitchenService):
    """Demonstrate order management functionality."""
    print("\n" + "="*60)
    print("ORDER MANAGEMENT DEMONSTRATION")
    print("="*60)
    
    # Show orders by status
    print("\n1. Orders by Status:")
    for status in OrderStatus:
        orders = kitchen_service.get_orders_by_status(status)
        print(f"   {status.value.title()}: {len(orders)} orders")
    
    # Show orders by priority
    print("\n2. Orders by Priority:")
    for priority in OrderPriority:
        orders = [order for order in kitchen_service.orders.values() 
                  if order.priority == priority]
        print(f"   {priority.value.title()}: {len(orders)} orders")
    
    # Show customer orders
    print("\n3. Orders by Customer:")
    customer_orders = {}
    for order in kitchen_service.orders.values():
        customer_id = order.customer_id
        if customer_id not in customer_orders:
            customer_orders[customer_id] = []
        customer_orders[customer_id].append(order)
    
    for customer_id, orders in customer_orders.items():
        total_value = sum(order.get_total_cost() for order in orders)
        print(f"   {customer_id}: {len(orders)} orders, "
              f"Total Value: ${total_value:.2f}")


def export_reports(kitchen_service: KitchenService):
    """Export inventory and orders reports."""
    print("\n" + "="*60)
    print("REPORT EXPORT")
    print("="*60)
    
    try:
        # Export inventory report
        inventory_file = kitchen_service.export_inventory_report()
        print(f"\n1. Inventory Report exported to: {inventory_file}")
        
        # Export orders report
        orders_file = kitchen_service.export_orders_report()
        print(f"2. Orders Report exported to: {orders_file}")
        
        print("\nReports have been exported successfully!")
        
    except Exception as e:
        print(f"Error exporting reports: {e}")


def main():
    """Main application entry point."""
    print("CloudKitchens Kitchen Workflow Optimization System")
    print("=" * 60)
    print("Initializing system...")
    
    try:
        # Initialize kitchen service
        kitchen_service = KitchenService()
        
        # Create sample inventory
        print("\nCreating sample inventory...")
        sample_items = create_sample_inventory()
        for item in sample_items:
            if kitchen_service.add_food_item(item):
                print(f"   Added: {item.name}")
            else:
                print(f"   Failed to add: {item.name}")
        
        # Create sample orders
        print("\nCreating sample orders...")
        sample_orders = create_sample_orders(kitchen_service)
        print(f"   Created {len(sample_orders)} orders")
        
        # Demonstrate functionality
        demonstrate_inventory_management(kitchen_service)
        demonstrate_order_management(kitchen_service)
        demonstrate_workflow_optimization(kitchen_service)
        export_reports(kitchen_service)
        
        print("\n" + "="*60)
        print("DEMONSTRATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        
        # Performance metrics
        print("\nFinal Performance Metrics:")
        metrics = kitchen_service.workflow_optimizer.get_performance_metrics()
        if metrics:
            for key, value in metrics.items():
                if isinstance(value, float):
                    print(f"   {key.replace('_', ' ').title()}: {value:.3f}")
                else:
                    print(f"   {key.replace('_', ' ').title()}: {value}")
        
        print("\nSystem is ready for production use!")
        
    except Exception as e:
        print(f"\nError during system initialization: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()