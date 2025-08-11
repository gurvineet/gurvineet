"""
Order Model

Represents a customer order with food items and delivery requirements.
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from .food_item import FoodItem


class OrderStatus(Enum):
    """Status of an order in the workflow."""
    PENDING = "pending"
    IN_PREPARATION = "in_preparation"
    READY = "ready"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderPriority(Enum):
    """Priority level for order processing."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class OrderItem:
    """
    Represents a food item within an order.
    
    Attributes:
        food_item: Reference to the food item
        quantity: Quantity requested
        special_instructions: Any special preparation instructions
    """
    food_item: FoodItem
    quantity: float
    special_instructions: Optional[str] = None
    
    @property
    def total_cost(self) -> float:
        """Calculate total cost for this order item."""
        return self.food_item.cost_per_unit * self.quantity
    
    @property
    def preparation_time_minutes(self) -> float:
        """Calculate total preparation time for this order item."""
        return self.food_item.preparation_time_minutes * self.quantity


@dataclass
class Order:
    """
    Represents a customer order.
    
    Attributes:
        id: Unique order identifier
        customer_id: Customer identifier
        items: List of food items in the order
        status: Current status of the order
        priority: Priority level for processing
        created_at: When the order was created
        estimated_preparation_time: Estimated time to prepare the order
        actual_preparation_time: Actual time taken to prepare
        delivery_address: Customer delivery address
        delivery_instructions: Special delivery instructions
        notes: Additional order notes
    """
    id: str
    customer_id: str
    items: List[OrderItem] = field(default_factory=list)
    status: OrderStatus = OrderStatus.PENDING
    priority: OrderPriority = OrderPriority.NORMAL
    created_at: datetime = field(default_factory=datetime.now)
    estimated_preparation_time: Optional[int] = None
    actual_preparation_time: Optional[int] = None
    delivery_address: Optional[str] = None
    delivery_instructions: Optional[str] = None
    notes: Optional[str] = None
    
    def __post_init__(self):
        """Calculate estimated preparation time if not provided."""
        if self.estimated_preparation_time is None:
            self.estimated_preparation_time = self._calculate_preparation_time()
    
    def _calculate_preparation_time(self) -> int:
        """Calculate estimated preparation time in minutes."""
        if not self.items:
            return 0
        
        # Base preparation time for all items
        total_time = sum(item.preparation_time_minutes for item in self.items)
        
        # Add buffer time for order complexity
        complexity_factor = min(len(self.items) * 0.1, 0.5)  # Max 50% buffer
        buffer_time = total_time * complexity_factor
        
        return int(total_time + buffer_time)
    
    def add_item(self, food_item: FoodItem, quantity: float, 
                 special_instructions: Optional[str] = None) -> None:
        """
        Add a food item to the order.
        
        Args:
            food_item: Food item to add
            quantity: Quantity requested
            special_instructions: Special preparation instructions
        """
        order_item = OrderItem(food_item, quantity, special_instructions)
        self.items.append(order_item)
        
        # Recalculate preparation time
        self.estimated_preparation_time = self._calculate_preparation_time()
    
    def remove_item(self, food_item_id: str) -> bool:
        """
        Remove a food item from the order.
        
        Args:
            food_item_id: ID of the food item to remove
            
        Returns:
            True if item was removed, False if not found
        """
        for i, item in enumerate(self.items):
            if item.food_item.id == food_item_id:
                self.items.pop(i)
                self.estimated_preparation_time = self._calculate_preparation_time()
                return True
        return False
    
    def update_status(self, new_status: OrderStatus) -> None:
        """
        Update the order status.
        
        Args:
            new_status: New status to set
        """
        self.status = new_status
        
        # Update timestamps based on status changes
        if new_status == OrderStatus.IN_PREPARATION:
            # Could add start time tracking here
            pass
        elif new_status == OrderStatus.READY:
            # Could add completion time tracking here
            pass
    
    def get_total_cost(self) -> float:
        """Calculate total cost of the order."""
        return sum(item.total_cost for item in self.items)
    
    def get_total_quantity(self) -> float:
        """Calculate total quantity of all items."""
        return sum(item.quantity for item in self.items)
    
    def get_spoilage_risk_score(self) -> float:
        """
        Calculate overall spoilage risk for the order.
        Higher score means higher risk of spoilage.
        """
        if not self.items:
            return 0.0
        
        # Weighted average of item spoilage risks
        total_weight = sum(item.quantity for item in self.items)
        weighted_risk = sum(item.quantity * item.food_item.spoilage_risk_score 
                           for item in self.items)
        
        return weighted_risk / total_weight if total_weight > 0 else 0.0
    
    def get_priority_score(self) -> float:
        """
        Calculate priority score for workflow optimization.
        Higher score means higher priority for processing.
        """
        # Base priority from order priority enum
        priority_map = {
            OrderPriority.LOW: 0.25,
            OrderPriority.NORMAL: 0.5,
            OrderPriority.HIGH: 0.75,
            OrderPriority.URGENT: 1.0
        }
        base_priority = priority_map.get(self.priority, 0.5)
        
        # Spoilage risk priority
        spoilage_priority = self.get_spoilage_risk_score()
        
        # Time priority (older orders get higher priority)
        time_since_creation = (datetime.now() - self.created_at).total_seconds()
        time_priority = min(time_since_creation / 3600, 1.0)  # Normalize to 1 hour
        
        # Weighted combination
        priority = (0.4 * base_priority + 
                   0.4 * spoilage_priority + 
                   0.2 * time_priority)
        
        return min(max(priority, 0.0), 1.0)
    
    def can_be_prepared(self) -> bool:
        """
        Check if the order can be prepared with current inventory.
        
        Returns:
            True if all items are available in sufficient quantity
        """
        for item in self.items:
            if item.food_item.current_quantity < item.quantity:
                return False
        return True
    
    def get_missing_items(self) -> List[OrderItem]:
        """
        Get list of items that cannot be fulfilled due to insufficient inventory.
        
        Returns:
            List of order items with insufficient inventory
        """
        missing_items = []
        for item in self.items:
            if item.food_item.current_quantity < item.quantity:
                missing_items.append(item)
        return missing_items
    
    def __str__(self) -> str:
        """String representation of the order."""
        return (f"Order {self.id} - {self.status.value} - "
                f"{len(self.items)} items - ${self.get_total_cost():.2f}")
    
    def __repr__(self) -> str:
        """Detailed string representation for debugging."""
        return (f"Order(id='{self.id}', customer_id='{self.customer_id}', "
                f"status={self.status}, priority={self.priority}, "
                f"items_count={len(self.items)})")