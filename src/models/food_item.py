"""
Food Item Model

Represents a food item with its spoilage characteristics and inventory information.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional


class FoodCategory(Enum):
    """Categories of food items based on spoilage characteristics."""
    PERISHABLE = "perishable"  # e.g., fresh produce, dairy
    SEMI_PERISHABLE = "semi_perishable"  # e.g., bread, some fruits
    NON_PERISHABLE = "non_perishable"  # e.g., canned goods, dry goods
    FROZEN = "frozen"  # e.g., ice cream, frozen vegetables


@dataclass
class FoodItem:
    """
    Represents a food item in the kitchen inventory.
    
    Attributes:
        id: Unique identifier for the food item
        name: Human-readable name of the food item
        category: Category based on spoilage characteristics
        spoilage_rate_hours: Time in hours before the item spoils
        current_quantity: Current available quantity
        min_quantity: Minimum quantity to maintain
        max_quantity: Maximum quantity to store
        unit: Unit of measurement (e.g., kg, pieces, liters)
        cost_per_unit: Cost per unit
        preparation_time_minutes: Time needed to prepare this item
        storage_requirements: Special storage requirements
        created_at: When this item was added to inventory
        last_updated: Last time inventory was updated
    """
    id: str
    name: str
    category: FoodCategory
    spoilage_rate_hours: int
    current_quantity: float
    min_quantity: float
    max_quantity: float
    unit: str
    cost_per_unit: float
    preparation_time_minutes: int
    storage_requirements: Optional[str] = None
    created_at: datetime = None
    last_updated: datetime = None
    
    def __post_init__(self):
        """Initialize timestamps if not provided."""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_updated is None:
            self.last_updated = datetime.now()
    
    @property
    def time_until_spoilage(self) -> timedelta:
        """Calculate time remaining until spoilage."""
        return timedelta(hours=self.spoilage_rate_hours)
    
    @property
    def spoilage_risk_score(self) -> float:
        """
        Calculate spoilage risk score (0-1, where 1 is highest risk).
        Higher score means higher risk of spoilage.
        """
        if self.spoilage_rate_hours <= 0:
            return 1.0
        
        time_since_creation = datetime.now() - self.created_at
        risk = time_since_creation.total_seconds() / (self.spoilage_rate_hours * 3600)
        return min(max(risk, 0.0), 1.0)
    
    @property
    def is_spoiled(self) -> bool:
        """Check if the food item has spoiled."""
        return self.spoilage_risk_score >= 1.0
    
    @property
    def is_low_stock(self) -> bool:
        """Check if the item is below minimum quantity."""
        return self.current_quantity <= self.min_quantity
    
    @property
    def is_overstocked(self) -> bool:
        """Check if the item exceeds maximum quantity."""
        return self.current_quantity >= self.max_quantity
    
    def update_quantity(self, new_quantity: float) -> None:
        """
        Update the current quantity and timestamp.
        
        Args:
            new_quantity: New quantity value
        """
        if new_quantity < 0:
            raise ValueError("Quantity cannot be negative")
        
        self.current_quantity = new_quantity
        self.last_updated = datetime.now()
    
    def consume_quantity(self, amount: float) -> None:
        """
        Consume a specified amount of the item.
        
        Args:
            amount: Amount to consume
        """
        if amount < 0:
            raise ValueError("Consumption amount cannot be negative")
        if amount > self.current_quantity:
            raise ValueError("Cannot consume more than available quantity")
        
        self.update_quantity(self.current_quantity - amount)
    
    def add_quantity(self, amount: float) -> None:
        """
        Add a specified amount to the item.
        
        Args:
            amount: Amount to add
        """
        if amount < 0:
            raise ValueError("Addition amount cannot be negative")
        
        new_quantity = self.current_quantity + amount
        if new_quantity > self.max_quantity:
            raise ValueError(f"Adding {amount} would exceed maximum quantity {self.max_quantity}")
        
        self.update_quantity(new_quantity)
    
    def get_priority_score(self) -> float:
        """
        Calculate priority score for workflow optimization.
        Higher score means higher priority for processing.
        
        Returns:
            Priority score (0-1, where 1 is highest priority)
        """
        # Base priority from spoilage risk
        spoilage_priority = self.spoilage_risk_score
        
        # Stock level priority (low stock gets higher priority)
        stock_priority = 1.0 - (self.current_quantity / self.max_quantity)
        
        # Cost priority (higher cost items get higher priority)
        cost_priority = min(self.cost_per_unit / 100.0, 1.0)  # Normalize to 0-1
        
        # Weighted combination of factors
        priority = (0.5 * spoilage_priority + 
                   0.3 * stock_priority + 
                   0.2 * cost_priority)
        
        return min(max(priority, 0.0), 1.0)
    
    def __str__(self) -> str:
        """String representation of the food item."""
        return (f"{self.name} ({self.category.value}) - "
                f"Qty: {self.current_quantity}{self.unit}, "
                f"Risk: {self.spoilage_risk_score:.2f}")
    
    def __repr__(self) -> str:
        """Detailed string representation for debugging."""
        return (f"FoodItem(id='{self.id}', name='{self.name}', "
                f"category={self.category}, spoilage_rate_hours={self.spoilage_rate_hours}, "
                f"current_quantity={self.current_quantity}, unit='{self.unit}')")