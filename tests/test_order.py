#!/usr/bin/env python3
"""
Tests for Order model.

Uses only Python standard library for testing.
"""
import unittest
from datetime import datetime, timedelta
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.order import Order, OrderItem, OrderStatus, OrderPriority
from models.food_item import FoodItem, FoodCategory


class TestOrderItem(unittest.TestCase):
    """Test cases for OrderItem class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.food_item = FoodItem(
            id="TEST_FOOD_001",
            name="Test Food",
            category=FoodCategory.PERISHABLE,
            spoilage_rate_hours=24,
            current_quantity=10.0,
            min_quantity=2.0,
            max_quantity=20.0,
            unit="kg",
            cost_per_unit=5.0,
            preparation_time_minutes=15
        )
        
        self.order_item = OrderItem(
            food_item=self.food_item,
            quantity=2.0,
            special_instructions="Test instructions"
        )
    
    def test_order_item_creation(self):
        """Test OrderItem creation."""
        self.assertEqual(self.order_item.food_item, self.food_item)
        self.assertEqual(self.order_item.quantity, 2.0)
        self.assertEqual(self.order_item.special_instructions, "Test instructions")
    
    def test_total_cost_calculation(self):
        """Test total cost calculation."""
        expected_cost = 2.0 * 5.0  # quantity * cost_per_unit
        self.assertEqual(self.order_item.total_cost, expected_cost)
    
    def test_preparation_time(self):
        """Test preparation time property."""
        self.assertEqual(self.order_item.preparation_time_minutes, 15)


class TestOrder(unittest.TestCase):
    """Test cases for Order class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.food_item1 = FoodItem(
            id="FOOD_001",
            name="Food Item 1",
            category=FoodCategory.PERISHABLE,
            spoilage_rate_hours=24,
            current_quantity=10.0,
            min_quantity=2.0,
            max_quantity=20.0,
            unit="kg",
            cost_per_unit=5.0,
            preparation_time_minutes=15
        )
        
        self.food_item2 = FoodItem(
            id="FOOD_002",
            name="Food Item 2",
            category=FoodCategory.SEMI_PERISHABLE,
            spoilage_rate_hours=168,
            current_quantity=20.0,
            min_quantity=5.0,
            max_quantity=30.0,
            unit="pieces",
            cost_per_unit=3.0,
            preparation_time_minutes=10
        )
        
        self.order = Order(
            id="ORDER_001",
            customer_id="CUST_001",
            priority=OrderPriority.HIGH,
            delivery_address="123 Test St",
            delivery_instructions="Ring doorbell"
        )
    
    def test_order_creation(self):
        """Test Order creation with required fields."""
        self.assertEqual(self.order.id, "ORDER_001")
        self.assertEqual(self.order.customer_id, "CUST_001")
        self.assertEqual(self.order.priority, OrderPriority.HIGH)
        self.assertEqual(self.order.status, OrderStatus.PENDING)
        self.assertEqual(self.order.delivery_address, "123 Test St")
        self.assertEqual(self.order.delivery_instructions, "Ring doorbell")
        self.assertEqual(len(self.order.items), 0)
    
    def test_timestamps_initialization(self):
        """Test that timestamps are automatically initialized."""
        now = datetime.now()
        self.assertIsNotNone(self.order.created_at)
        
        # Created timestamp should be within 1 second of now
        self.assertLess(abs((self.order.created_at - now).total_seconds()), 1)
    
    def test_add_item(self):
        """Test adding items to order."""
        self.order.add_item(self.food_item1, 2.0, "Fresh please")
        
        self.assertEqual(len(self.order.items), 1)
        self.assertEqual(self.order.items[0].food_item, self.food_item1)
        self.assertEqual(self.order.items[0].quantity, 2.0)
        self.assertEqual(self.order.items[0].special_instructions, "Fresh please")
    
    def test_add_multiple_items(self):
        """Test adding multiple items to order."""
        self.order.add_item(self.food_item1, 1.5, "Organic")
        self.order.add_item(self.food_item2, 3.0, "Fresh baked")
        
        self.assertEqual(len(self.order.items), 2)
        self.assertEqual(self.order.items[0].food_item, self.food_item1)
        self.assertEqual(self.order.items[1].food_item, self.food_item2)
    
    def test_remove_item(self):
        """Test removing items from order."""
        self.order.add_item(self.food_item1, 2.0)
        self.order.add_item(self.food_item2, 3.0)
        
        # Remove first item
        self.order.remove_item(self.food_item1.id)
        
        self.assertEqual(len(self.order.items), 1)
        self.assertEqual(self.order.items[0].food_item, self.food_item2)
    
    def test_remove_nonexistent_item(self):
        """Test removing non-existent item."""
        self.order.add_item(self.food_item1, 2.0)
        
        # Try to remove non-existent item
        result = self.order.remove_item("NONEXISTENT_ID")
        
        self.assertFalse(result)
        self.assertEqual(len(self.order.items), 1)  # Item count unchanged
    
    def test_update_status(self):
        """Test order status updates."""
        self.assertEqual(self.order.status, OrderStatus.PENDING)
        
        # Update status
        self.order.update_status(OrderStatus.IN_PREPARATION)
        self.assertEqual(self.order.status, OrderStatus.IN_PREPARATION)
        
        # Update with timestamp
        timestamp = datetime.now()
        self.order.update_status(OrderStatus.READY, timestamp)
        self.assertEqual(self.order.status, OrderStatus.READY)
        self.assertEqual(self.order.actual_preparation_time, timestamp)
    
    def test_total_cost_calculation(self):
        """Test total cost calculation for order."""
        self.order.add_item(self.food_item1, 2.0)  # 2.0 * 5.0 = 10.0
        self.order.add_item(self.food_item2, 3.0)  # 3.0 * 3.0 = 9.0
        
        expected_total = 10.0 + 9.0
        self.assertEqual(self.order.get_total_cost(), expected_total)
    
    def test_total_quantity_calculation(self):
        """Test total quantity calculation for order."""
        self.order.add_item(self.food_item1, 2.0)
        self.order.add_item(self.food_item2, 3.0)
        
        expected_total = 2.0 + 3.0
        self.assertEqual(self.order.get_total_quantity(), expected_total)
    
    def test_spoilage_risk_score(self):
        """Test spoilage risk score calculation."""
        # Add items with different spoilage characteristics
        self.order.add_item(self.food_item1, 2.0)  # High spoilage risk
        self.order.add_item(self.food_item2, 3.0)  # Lower spoilage risk
        
        risk_score = self.order.get_spoilage_risk_score()
        
        # Risk score should be between 0 and 1
        self.assertGreaterEqual(risk_score, 0.0)
        self.assertLessEqual(risk_score, 1.0)
        
        # Should be weighted average of item risks
        self.assertGreater(risk_score, 0.0)  # Should have some risk
    
    def test_priority_score_calculation(self):
        """Test priority score calculation."""
        # Add some items
        self.order.add_item(self.food_item1, 2.0)
        self.order.add_item(self.food_item2, 3.0)
        
        priority_score = self.order.get_priority_score()
        
        # Priority score should be between 0 and 1
        self.assertGreaterEqual(priority_score, 0.0)
        self.assertLessEqual(priority_score, 1.0)
    
    def test_priority_score_with_order_priority(self):
        """Test that order priority affects priority score."""
        # Create orders with different priorities
        high_priority_order = Order(
            id="HIGH_001",
            customer_id="CUST_002",
            priority=OrderPriority.HIGH
        )
        high_priority_order.add_item(self.food_item1, 1.0)
        
        low_priority_order = Order(
            id="LOW_001",
            customer_id="CUST_003",
            priority=OrderPriority.LOW
        )
        low_priority_order.add_item(self.food_item1, 1.0)
        
        high_score = high_priority_order.get_priority_score()
        low_score = low_priority_order.get_priority_score()
        
        # High priority order should have higher score
        self.assertGreater(high_score, low_score)
    
    def test_can_be_prepared(self):
        """Test order preparation feasibility."""
        # Order with no items cannot be prepared
        self.assertFalse(self.order.can_be_prepared())
        
        # Add items
        self.order.add_item(self.food_item1, 2.0)
        self.order.add_item(self.food_item2, 3.0)
        
        # Order with items can be prepared
        self.assertTrue(self.order.can_be_prepared())
    
    def test_get_missing_items(self):
        """Test missing items detection."""
        # Add items
        self.order.add_item(self.food_item1, 2.0)
        self.order.add_item(self.food_item2, 3.0)
        
        # All items should be available
        missing_items = self.order.get_missing_items()
        self.assertEqual(len(missing_items), 0)
        
        # Create order with insufficient inventory
        insufficient_order = Order(
            id="INSUFFICIENT_001",
            customer_id="CUST_004"
        )
        insufficient_order.add_item(self.food_item1, 15.0)  # More than available (10.0)
        
        missing_items = insufficient_order.get_missing_items()
        self.assertEqual(len(missing_items), 1)
        self.assertEqual(missing_items[0].food_item, self.food_item1)
    
    def test_string_representation(self):
        """Test string representation of Order."""
        self.order.add_item(self.food_item1, 2.0)
        
        string_repr = str(self.order)
        
        self.assertIn(self.order.id, string_repr)
        self.assertIn(self.order.customer_id, string_repr)
        self.assertIn(self.order.status.value, string_repr)
        self.assertIn(self.order.priority.value, string_repr)
    
    def test_repr_representation(self):
        """Test detailed string representation for debugging."""
        self.order.add_item(self.food_item1, 2.0)
        
        repr_str = repr(self.order)
        
        self.assertIn(self.order.id, repr_str)
        self.assertIn(self.order.customer_id, repr_str)
        self.assertIn(str(len(self.order.items)), repr_str)


class TestOrderStatus(unittest.TestCase):
    """Test cases for OrderStatus enum."""
    
    def test_order_statuses(self):
        """Test all order statuses are defined."""
        statuses = list(OrderStatus)
        
        self.assertIn(OrderStatus.PENDING, statuses)
        self.assertIn(OrderStatus.IN_PREPARATION, statuses)
        self.assertIn(OrderStatus.READY, statuses)
        self.assertIn(OrderStatus.OUT_FOR_DELIVERY, statuses)
        self.assertIn(OrderStatus.DELIVERED, statuses)
        self.assertIn(OrderStatus.CANCELLED, statuses)
    
    def test_status_values(self):
        """Test status string values."""
        self.assertEqual(OrderStatus.PENDING.value, "pending")
        self.assertEqual(OrderStatus.IN_PREPARATION.value, "in_preparation")
        self.assertEqual(OrderStatus.READY.value, "ready")
        self.assertEqual(OrderStatus.OUT_FOR_DELIVERY.value, "out_for_delivery")
        self.assertEqual(OrderStatus.DELIVERED.value, "delivered")
        self.assertEqual(OrderStatus.CANCELLED.value, "cancelled")


class TestOrderPriority(unittest.TestCase):
    """Test cases for OrderPriority enum."""
    
    def test_order_priorities(self):
        """Test all order priorities are defined."""
        priorities = list(OrderPriority)
        
        self.assertIn(OrderPriority.LOW, priorities)
        self.assertIn(OrderPriority.NORMAL, priorities)
        self.assertIn(OrderPriority.HIGH, priorities)
        self.assertIn(OrderPriority.URGENT, priorities)
    
    def test_priority_values(self):
        """Test priority string values."""
        self.assertEqual(OrderPriority.LOW.value, "low")
        self.assertEqual(OrderPriority.NORMAL.value, "normal")
        self.assertEqual(OrderPriority.HIGH.value, "high")
        self.assertEqual(OrderPriority.URGENT.value, "urgent")


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)