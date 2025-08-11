#!/usr/bin/env python3
"""
Tests for FoodItem model.

Uses only Python standard library for testing.
"""
import unittest
from datetime import datetime, timedelta
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.food_item import FoodItem, FoodCategory


class TestFoodItem(unittest.TestCase):
    """Test cases for FoodItem class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.food_item = FoodItem(
            id="TEST_001",
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
    
    def test_food_item_creation(self):
        """Test FoodItem creation with all required fields."""
        self.assertEqual(self.food_item.id, "TEST_001")
        self.assertEqual(self.food_item.name, "Test Food")
        self.assertEqual(self.food_item.category, FoodCategory.PERISHABLE)
        self.assertEqual(self.food_item.spoilage_rate_hours, 24)
        self.assertEqual(self.food_item.current_quantity, 10.0)
        self.assertEqual(self.food_item.unit, "kg")
        self.assertEqual(self.food_item.cost_per_unit, 5.0)
        self.assertEqual(self.food_item.preparation_time_minutes, 15)
    
    def test_timestamps_initialization(self):
        """Test that timestamps are automatically initialized."""
        now = datetime.now()
        self.assertIsNotNone(self.food_item.created_at)
        self.assertIsNotNone(self.food_item.last_updated)
        
        # Timestamps should be within 1 second of now
        self.assertLess(abs((self.food_item.created_at - now).total_seconds()), 1)
        self.assertLess(abs((self.food_item.last_updated - now).total_seconds()), 1)
    
    def test_time_until_spoilage(self):
        """Test time_until_spoilage property."""
        expected_time = timedelta(hours=24)
        self.assertEqual(self.food_item.time_until_spoilage, expected_time)
    
    def test_spoilage_risk_score_fresh_item(self):
        """Test spoilage risk score for a fresh item."""
        # Fresh item should have very low risk
        risk_score = self.food_item.spoilage_risk_score
        self.assertGreaterEqual(risk_score, 0.0)
        self.assertLess(risk_score, 0.1)  # Should be very low for fresh item
    
    def test_spoilage_risk_score_aging_item(self):
        """Test spoilage risk score for an aging item."""
        # Create an item that's been aging
        aging_item = FoodItem(
            id="AGING_001",
            name="Aging Food",
            category=FoodCategory.PERISHABLE,
            spoilage_rate_hours=24,
            current_quantity=5.0,
            min_quantity=1.0,
            max_quantity=10.0,
            unit="kg",
            cost_per_unit=3.0,
            preparation_time_minutes=10,
            created_at=datetime.now() - timedelta(hours=12)  # 12 hours old
        )
        
        # Item at half its spoilage time should have risk around 0.5
        risk_score = aging_item.spoilage_risk_score
        self.assertGreaterEqual(risk_score, 0.4)
        self.assertLessEqual(risk_score, 0.6)
    
    def test_is_spoiled(self):
        """Test is_spoiled property."""
        # Fresh item should not be spoiled
        self.assertFalse(self.food_item.is_spoiled)
        
        # Create a spoiled item
        spoiled_item = FoodItem(
            id="SPOILED_001",
            name="Spoiled Food",
            category=FoodCategory.PERISHABLE,
            spoilage_rate_hours=24,
            current_quantity=1.0,
            min_quantity=0.5,
            max_quantity=5.0,
            unit="kg",
            cost_per_unit=2.0,
            preparation_time_minutes=5,
            created_at=datetime.now() - timedelta(hours=30)  # 30 hours old (beyond 24h limit)
        )
        
        self.assertTrue(spoiled_item.is_spoiled)
    
    def test_stock_levels(self):
        """Test stock level properties."""
        # Test low stock
        self.food_item.current_quantity = 1.0  # Below min_quantity (2.0)
        self.assertTrue(self.food_item.is_low_stock)
        
        # Test normal stock
        self.food_item.current_quantity = 5.0  # Between min and max
        self.assertFalse(self.food_item.is_low_stock)
        self.assertFalse(self.food_item.is_overstocked)
        
        # Test overstocked
        self.food_item.current_quantity = 25.0  # Above max_quantity (20.0)
        self.assertTrue(self.food_item.is_overstocked)
    
    def test_update_quantity(self):
        """Test quantity update functionality."""
        original_updated = self.food_item.last_updated
        
        # Wait a bit to ensure timestamp difference
        import time
        time.sleep(0.001)
        
        # Update quantity
        self.food_item.update_quantity(15.0)
        
        self.assertEqual(self.food_item.current_quantity, 15.0)
        self.assertGreater(self.food_item.last_updated, original_updated)
    
    def test_update_quantity_negative(self):
        """Test that negative quantities are rejected."""
        with self.assertRaises(ValueError):
            self.food_item.update_quantity(-5.0)
    
    def test_consume_quantity(self):
        """Test quantity consumption."""
        original_quantity = self.food_item.current_quantity
        
        # Consume some quantity
        self.food_item.consume_quantity(3.0)
        
        self.assertEqual(self.food_item.current_quantity, original_quantity - 3.0)
    
    def test_consume_quantity_negative(self):
        """Test that negative consumption amounts are rejected."""
        with self.assertRaises(ValueError):
            self.food_item.consume_quantity(-2.0)
    
    def test_consume_quantity_insufficient(self):
        """Test that consuming more than available quantity is rejected."""
        with self.assertRaises(ValueError):
            self.food_item.consume_quantity(15.0)  # Only have 10.0
    
    def test_add_quantity(self):
        """Test quantity addition."""
        original_quantity = self.food_item.current_quantity
        
        # Add some quantity
        self.food_item.add_quantity(5.0)
        
        self.assertEqual(self.food_item.current_quantity, original_quantity + 5.0)
    
    def test_add_quantity_negative(self):
        """Test that negative addition amounts are rejected."""
        with self.assertRaises(ValueError):
            self.food_item.add_quantity(-3.0)
    
    def test_add_quantity_exceeds_max(self):
        """Test that adding quantity beyond max is rejected."""
        with self.assertRaises(ValueError):
            self.food_item.add_quantity(15.0)  # Would exceed max_quantity (20.0)
    
    def test_priority_score_calculation(self):
        """Test priority score calculation."""
        priority_score = self.food_item.get_priority_score()
        
        # Priority score should be between 0 and 1
        self.assertGreaterEqual(priority_score, 0.0)
        self.assertLessEqual(priority_score, 1.0)
    
    def test_priority_score_with_spoilage_risk(self):
        """Test priority score increases with spoilage risk."""
        # Create a fresh item
        fresh_item = FoodItem(
            id="FRESH_001",
            name="Fresh Food",
            category=FoodCategory.PERISHABLE,
            spoilage_rate_hours=48,
            current_quantity=10.0,
            min_quantity=2.0,
            max_quantity=20.0,
            unit="kg",
            cost_per_unit=5.0,
            preparation_time_minutes=15
        )
        
        # Create an aging item
        aging_item = FoodItem(
            id="AGING_001",
            name="Aging Food",
            category=FoodCategory.PERISHABLE,
            spoilage_rate_hours=48,
            current_quantity=10.0,
            min_quantity=2.0,
            max_quantity=20.0,
            unit="kg",
            cost_per_unit=5.0,
            preparation_time_minutes=15,
            created_at=datetime.now() - timedelta(hours=36)  # 36 hours old
        )
        
        fresh_priority = fresh_item.get_priority_score()
        aging_priority = aging_item.get_priority_score()
        
        # Aging item should have higher priority (higher spoilage risk)
        self.assertGreater(aging_priority, fresh_priority)
    
    def test_string_representation(self):
        """Test string representation of FoodItem."""
        string_repr = str(self.food_item)
        
        self.assertIn(self.food_item.name, string_repr)
        self.assertIn(self.food_item.category.value, string_repr)
        self.assertIn(str(self.food_item.current_quantity), string_repr)
        self.assertIn(self.food_item.unit, string_repr)
    
    def test_repr_representation(self):
        """Test detailed string representation for debugging."""
        repr_str = repr(self.food_item)
        
        self.assertIn(self.food_item.id, repr_str)
        self.assertIn(self.food_item.name, repr_str)
        self.assertIn(self.food_item.category.value, repr_str)
        self.assertIn(str(self.food_item.current_quantity), repr_str)


class TestFoodCategory(unittest.TestCase):
    """Test cases for FoodCategory enum."""
    
    def test_food_categories(self):
        """Test all food categories are defined."""
        categories = list(FoodCategory)
        
        self.assertIn(FoodCategory.PERISHABLE, categories)
        self.assertIn(FoodCategory.SEMI_PERISHABLE, categories)
        self.assertIn(FoodCategory.NON_PERISHABLE, categories)
        self.assertIn(FoodCategory.FROZEN, categories)
    
    def test_category_values(self):
        """Test category string values."""
        self.assertEqual(FoodCategory.PERISHABLE.value, "perishable")
        self.assertEqual(FoodCategory.SEMI_PERISHABLE.value, "semi_perishable")
        self.assertEqual(FoodCategory.NON_PERISHABLE.value, "non_perishable")
        self.assertEqual(FoodCategory.FROZEN.value, "frozen")


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)