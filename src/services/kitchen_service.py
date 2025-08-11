"""
Kitchen Service

Core business logic for managing kitchen inventory and orders.
Uses only Python standard library.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import json
import csv
from pathlib import Path

from models.food_item import FoodItem, FoodCategory
from models.order import Order, OrderStatus, OrderPriority, OrderItem
from algorithms.workflow_optimizer import WorkflowOptimizer, OptimizationResult


class KitchenService:
    """
    Main service for managing kitchen operations.
    
    Handles inventory management, order processing, and workflow optimization.
    """
    
    def __init__(self, data_directory: str = "data"):
        """
        Initialize the kitchen service.
        
        Args:
            data_directory: Directory for storing data files
        """
        self.data_directory = Path(data_directory)
        self.data_directory.mkdir(exist_ok=True)
        
        # Initialize components
        self.inventory: Dict[str, FoodItem] = {}
        self.orders: Dict[str, Order] = {}
        self.workflow_optimizer = WorkflowOptimizer()
        
        # Load existing data
        self._load_data()
    
    def add_food_item(self, food_item: FoodItem) -> bool:
        """
        Add a new food item to inventory.
        
        Args:
            food_item: Food item to add
            
        Returns:
            True if successfully added, False otherwise
        """
        if food_item.id in self.inventory:
            return False
        
        self.inventory[food_item.id] = food_item
        self._save_inventory()
        return True
    
    def update_food_item(self, item_id: str, **kwargs) -> bool:
        """
        Update an existing food item.
        
        Args:
            item_id: ID of the food item to update
            **kwargs: Fields to update
            
        Returns:
            True if successfully updated, False otherwise
        """
        if item_id not in self.inventory:
            return False
        
        item = self.inventory[item_id]
        for field, value in kwargs.items():
            if hasattr(item, field):
                setattr(item, field, value)
        
        item.last_updated = datetime.now()
        self._save_inventory()
        return True
    
    def remove_food_item(self, item_id: str) -> bool:
        """
        Remove a food item from inventory.
        
        Args:
            item_id: ID of the food item to remove
            
        Returns:
            True if successfully removed, False otherwise
        """
        if item_id not in self.inventory:
            return False
        
        # Check if item is used in any orders
        for order in self.orders.values():
            for order_item in order.items:
                if order_item.food_item.id == item_id:
                    return False  # Cannot remove item used in orders
        
        del self.inventory[item_id]
        self._save_inventory()
        return True
    
    def get_food_item(self, item_id: str) -> Optional[FoodItem]:
        """
        Get a food item by ID.
        
        Args:
            item_id: ID of the food item
            
        Returns:
            Food item if found, None otherwise
        """
        return self.inventory.get(item_id)
    
    def get_inventory_summary(self) -> Dict[str, any]:
        """
        Get summary of current inventory.
        
        Returns:
            Dictionary with inventory statistics
        """
        if not self.inventory:
            return {
                'total_items': 0,
                'total_value': 0.0,
                'low_stock_items': 0,
                'high_risk_items': 0,
                'categories': {}
            }
        
        total_value = sum(item.current_quantity * item.cost_per_unit 
                         for item in self.inventory.values())
        
        low_stock_items = sum(1 for item in self.inventory.values() 
                             if item.is_low_stock)
        
        high_risk_items = sum(1 for item in self.inventory.values() 
                             if item.spoilage_risk_score > 0.7)
        
        categories = {}
        for item in self.inventory.values():
            category = item.category.value
            if category not in categories:
                categories[category] = {
                    'count': 0,
                    'total_quantity': 0.0,
                    'total_value': 0.0
                }
            categories[category]['count'] += 1
            categories[category]['total_quantity'] += item.current_quantity
            categories[category]['total_value'] += item.current_quantity * item.cost_per_unit
        
        return {
            'total_items': len(self.inventory),
            'total_value': total_value,
            'low_stock_items': low_stock_items,
            'high_risk_items': high_risk_items,
            'categories': categories
        }
    
    def create_order(self, customer_id: str, items: List[Tuple[str, float, Optional[str]]], 
                     priority: OrderPriority = OrderPriority.NORMAL,
                     delivery_address: Optional[str] = None,
                     delivery_instructions: Optional[str] = None,
                     notes: Optional[str] = None) -> Optional[Order]:
        """
        Create a new order.
        
        Args:
            customer_id: Customer identifier
            items: List of tuples (food_item_id, quantity, special_instructions)
            priority: Order priority level
            delivery_address: Customer delivery address
            delivery_instructions: Special delivery instructions
            notes: Additional order notes
            
        Returns:
            Created order if successful, None otherwise
        """
        # Generate unique order ID
        order_id = f"ORD_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.orders) + 1}"
        
        # Create order
        order = Order(
            id=order_id,
            customer_id=customer_id,
            priority=priority,
            delivery_address=delivery_address,
            delivery_instructions=delivery_instructions,
            notes=notes
        )
        
        # Add items to order
        for item_id, quantity, special_instructions in items:
            food_item = self.inventory.get(item_id)
            if not food_item:
                return None  # Food item not found
            
            if food_item.current_quantity < quantity:
                return None  # Insufficient inventory
            
            order.add_item(food_item, quantity, special_instructions)
        
        if not order.items:
            return None  # No items in order
        
        # Store order
        self.orders[order_id] = order
        self._save_orders()
        
        return order
    
    def update_order_status(self, order_id: str, new_status: OrderStatus) -> bool:
        """
        Update the status of an order.
        
        Args:
            order_id: ID of the order to update
            new_status: New status to set
            
        Returns:
            True if successfully updated, False otherwise
        """
        if order_id not in self.orders:
            return False
        
        order = self.orders[order_id]
        old_status = order.status
        
        # Update status
        order.update_status(new_status)
        
        # Handle inventory updates based on status change
        if (old_status == OrderStatus.PENDING and 
            new_status == OrderStatus.IN_PREPARATION):
            # Reserve inventory
            self._reserve_inventory(order)
        elif (old_status == OrderStatus.IN_PREPARATION and 
              new_status == OrderStatus.READY):
            # Consume inventory
            self._consume_inventory(order)
        
        self._save_orders()
        return True
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """
        Get an order by ID.
        
        Args:
            order_id: ID of the order
            
        Returns:
            Order if found, None otherwise
        """
        return self.orders.get(order_id)
    
    def get_orders_by_status(self, status: OrderStatus) -> List[Order]:
        """
        Get all orders with a specific status.
        
        Args:
            status: Status to filter by
            
        Returns:
            List of orders with the specified status
        """
        return [order for order in self.orders.values() if order.status == status]
    
    def get_orders_by_customer(self, customer_id: str) -> List[Order]:
        """
        Get all orders for a specific customer.
        
        Args:
            customer_id: Customer identifier
            
        Returns:
            List of orders for the customer
        """
        return [order for order in self.orders.values() if order.customer_id == customer_id]
    
    def optimize_workflow(self) -> OptimizationResult:
        """
        Optimize the current workflow.
        
        Returns:
            Optimization result with recommended order sequence
        """
        active_orders = [order for order in self.orders.values() 
                        if order.status in [OrderStatus.PENDING, OrderStatus.IN_PREPARATION]]
        
        return self.workflow_optimizer.optimize_workflow(active_orders)
    
    def get_workflow_metrics(self) -> Dict[str, any]:
        """
        Get current workflow metrics.
        
        Returns:
            Dictionary with workflow statistics
        """
        active_orders = [order for order in self.orders.values() 
                        if order.status in [OrderStatus.PENDING, OrderStatus.IN_PREPARATION]]
        
        if not active_orders:
            return {
                'active_orders': 0,
                'avg_priority_score': 0.0,
                'avg_spoilage_risk': 0.0,
                'total_processing_time': 0
            }
        
        avg_priority_score = sum(order.get_priority_score() for order in active_orders) / len(active_orders)
        avg_spoilage_risk = sum(order.get_spoilage_risk_score() for order in active_orders) / len(active_orders)
        total_processing_time = sum(order.estimated_preparation_time for order in active_orders)
        
        return {
            'active_orders': len(active_orders),
            'avg_priority_score': avg_priority_score,
            'avg_spoilage_risk': avg_spoilage_risk,
            'total_processing_time': total_processing_time
        }
    
    def export_inventory_report(self, filename: str = None) -> str:
        """
        Export inventory report to CSV.
        
        Args:
            filename: Output filename (optional)
            
        Returns:
            Path to the exported file
        """
        if filename is None:
            filename = f"inventory_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = self.data_directory / filename
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'ID', 'Name', 'Category', 'Spoilage_Rate_Hours', 'Current_Quantity',
                'Min_Quantity', 'Max_Quantity', 'Unit', 'Cost_Per_Unit',
                'Preparation_Time_Minutes', 'Spoilage_Risk_Score', 'Status'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for item in self.inventory.values():
                status = "LOW_STOCK" if item.is_low_stock else "OK"
                if item.is_spoiled:
                    status = "SPOILED"
                elif item.is_overstocked:
                    status = "OVERSTOCKED"
                
                writer.writerow({
                    'ID': item.id,
                    'Name': item.name,
                    'Category': item.category.value,
                    'Spoilage_Rate_Hours': item.spoilage_rate_hours,
                    'Current_Quantity': item.current_quantity,
                    'Min_Quantity': item.min_quantity,
                    'Max_Quantity': item.max_quantity,
                    'Unit': item.unit,
                    'Cost_Per_Unit': item.cost_per_unit,
                    'Preparation_Time_Minutes': item.preparation_time_minutes,
                    'Spoilage_Risk_Score': f"{item.spoilage_risk_score:.3f}",
                    'Status': status
                })
        
        return str(filepath)
    
    def export_orders_report(self, filename: str = None) -> str:
        """
        Export orders report to CSV.
        
        Args:
            filename: Output filename (optional)
            
        Returns:
            Path to the exported file
        """
        if filename is None:
            filename = f"orders_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = self.data_directory / filename
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'Order_ID', 'Customer_ID', 'Status', 'Priority', 'Created_At',
                'Items_Count', 'Total_Cost', 'Estimated_Preparation_Time',
                'Spoilage_Risk_Score', 'Priority_Score'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for order in self.orders.values():
                writer.writerow({
                    'Order_ID': order.id,
                    'Customer_ID': order.customer_id,
                    'Status': order.status.value,
                    'Priority': order.priority.value,
                    'Created_At': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'Items_Count': len(order.items),
                    'Total_Cost': f"{order.get_total_cost():.2f}",
                    'Estimated_Preparation_Time': order.estimated_preparation_time,
                    'Spoilage_Risk_Score': f"{order.get_spoilage_risk_score():.3f}",
                    'Priority_Score': f"{order.get_priority_score():.3f}"
                })
        
        return str(filepath)
    
    def _reserve_inventory(self, order: Order) -> None:
        """Reserve inventory for an order being prepared."""
        for order_item in order.items:
            food_item = order_item.food_item
            # In a real system, you might want to track reserved vs available inventory
            pass
    
    def _consume_inventory(self, order: Order) -> None:
        """Consume inventory when an order is completed."""
        for order_item in order.items:
            food_item = order_item.food_item
            food_item.consume_quantity(order_item.quantity)
    
    def _load_data(self) -> None:
        """Load existing data from files."""
        self._load_inventory()
        self._load_orders()
    
    def _save_inventory(self) -> None:
        """Save inventory data to file."""
        filepath = self.data_directory / "inventory.json"
        
        # Convert inventory to serializable format
        inventory_data = {}
        for item_id, item in self.inventory.items():
            inventory_data[item_id] = {
                'id': item.id,
                'name': item.name,
                'category': item.category.value,
                'spoilage_rate_hours': item.spoilage_rate_hours,
                'current_quantity': item.current_quantity,
                'min_quantity': item.min_quantity,
                'max_quantity': item.max_quantity,
                'unit': item.unit,
                'cost_per_unit': item.cost_per_unit,
                'preparation_time_minutes': item.preparation_time_minutes,
                'storage_requirements': item.storage_requirements,
                'created_at': item.created_at.isoformat(),
                'last_updated': item.last_updated.isoformat()
            }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(inventory_data, f, indent=2, ensure_ascii=False)
    
    def _load_inventory(self) -> None:
        """Load inventory data from file."""
        filepath = self.data_directory / "inventory.json"
        
        if not filepath.exists():
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                inventory_data = json.load(f)
            
            for item_id, item_data in inventory_data.items():
                # Reconstruct FoodItem from data
                food_item = FoodItem(
                    id=item_data['id'],
                    name=item_data['name'],
                    category=FoodCategory(item_data['category']),
                    spoilage_rate_hours=item_data['spoilage_rate_hours'],
                    current_quantity=item_data['current_quantity'],
                    min_quantity=item_data['min_quantity'],
                    max_quantity=item_data['max_quantity'],
                    unit=item_data['unit'],
                    cost_per_unit=item_data['cost_per_unit'],
                    preparation_time_minutes=item_data['preparation_time_minutes'],
                    storage_requirements=item_data.get('storage_requirements'),
                    created_at=datetime.fromisoformat(item_data['created_at']),
                    last_updated=datetime.fromisoformat(item_data['last_updated'])
                )
                
                self.inventory[item_id] = food_item
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error loading inventory: {e}")
    
    def _save_orders(self) -> None:
        """Save orders data to file."""
        filepath = self.data_directory / "orders.json"
        
        # Convert orders to serializable format
        orders_data = {}
        for order_id, order in self.orders.items():
            orders_data[order_id] = {
                'id': order.id,
                'customer_id': order.customer_id,
                'status': order.status.value,
                'priority': order.priority.value,
                'created_at': order.created_at.isoformat(),
                'estimated_preparation_time': order.estimated_preparation_time,
                'actual_preparation_time': order.actual_preparation_time,
                'delivery_address': order.delivery_address,
                'delivery_instructions': order.delivery_instructions,
                'notes': order.notes,
                'items': [
                    {
                        'food_item_id': item.food_item.id,
                        'quantity': item.quantity,
                        'special_instructions': item.special_instructions
                    }
                    for item in order.items
                ]
            }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(orders_data, f, indent=2, ensure_ascii=False)
    
    def _load_orders(self) -> None:
        """Load orders data from file."""
        filepath = self.data_directory / "orders.json"
        
        if not filepath.exists():
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                orders_data = json.load(f)
            
            for order_id, order_data in orders_data.items():
                # Reconstruct Order from data
                order = Order(
                    id=order_data['id'],
                    customer_id=order_data['customer_id'],
                    status=OrderStatus(order_data['status']),
                    priority=OrderPriority(order_data['priority']),
                    created_at=datetime.fromisoformat(order_data['created_at']),
                    estimated_preparation_time=order_data['estimated_preparation_time'],
                    actual_preparation_time=order_data.get('actual_preparation_time'),
                    delivery_address=order_data.get('delivery_address'),
                    delivery_instructions=order_data.get('delivery_instructions'),
                    notes=order_data.get('notes')
                )
                
                # Add items to order
                for item_data in order_data['items']:
                    food_item = self.inventory.get(item_data['food_item_id'])
                    if food_item:
                        order.add_item(
                            food_item,
                            item_data['quantity'],
                            item_data.get('special_instructions')
                        )
                
                self.orders[order_id] = order
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error loading orders: {e}")