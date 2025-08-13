#!/usr/bin/env python3
"""
Real-time Food Order Fulfillment System

This system manages food orders in a delivery-only kitchen with concurrent
order placement and pickup operations.
"""

import time
import threading
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class Temperature(Enum):
    """Food storage temperature requirements."""
    HOT = "hot"
    COLD = "cold"
    ROOM = "room"


class ActionType(Enum):
    """Types of kitchen actions."""
    PLACE = "place"
    MOVE = "move"
    PICKUP = "pickup"
    DISCARD = "discard"


@dataclass
class FoodOrder:
    """Represents a food order with all required attributes."""
    id: str
    name: str
    temperature: Temperature
    freshness: int  # Duration in seconds
    placed_at: float  # Timestamp when placed
    stored_at: float  # Timestamp when stored
    storage_location: str  # "cooler", "heater", or "shelf"
    
    def is_fresh(self, current_time: float) -> bool:
        """Check if the order is still fresh at current time."""
        elapsed_time = current_time - self.stored_at
        ideal_freshness = self.freshness
        
        # If stored at ideal temperature, use normal freshness
        # If stored at non-ideal temperature, degrade twice as quickly
        if self.storage_location == self.temperature.value:
            return elapsed_time < ideal_freshness
        else:
            return elapsed_time < (ideal_freshness / 2)


@dataclass
class KitchenAction:
    """Represents a kitchen action for the ledger."""
    timestamp: float
    order_id: str
    action_type: ActionType
    target: str  # Storage location or action description
    details: str = ""


class KitchenSystem:
    """Main kitchen system managing order fulfillment and storage."""
    
    def __init__(self):
        # Storage containers with capacity limits
        self.cooler: List[FoodOrder] = []  # Max 6 cold orders
        self.heater: List[FoodOrder] = []  # Max 6 hot orders
        self.shelf: List[FoodOrder] = []   # Max 12 orders
        
        # Order tracking
        self.orders: Dict[str, FoodOrder] = {}
        
        # Action ledger
        self.actions: List[KitchenAction] = []
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Statistics
        self.stats = {
            'orders_placed': 0,
            'orders_picked_up': 0,
            'orders_discarded': 0,
            'orders_moved': 0
        }
    
    def place_order(self, order_id: str, name: str, temperature: Temperature, 
                   freshness: int) -> bool:
        """
        Place a new order in the kitchen system.
        
        Returns True if successfully placed, False otherwise.
        """
        current_time = time.time()
        
        with self.lock:
            # Create the order
            order = FoodOrder(
                id=order_id,
                name=name,
                temperature=temperature,
                freshness=freshness,
                placed_at=current_time,
                stored_at=current_time,
                storage_location=""
            )
            
            # Try to store at ideal temperature first
            if self._try_store_at_ideal_temperature(order):
                self._log_action(current_time, order_id, ActionType.PLACE, 
                               order.storage_location, f"Stored {name} at ideal temperature")
                self.orders[order_id] = order
                self.stats['orders_placed'] += 1
                return True
            
            # If ideal storage is full, try to move existing orders and place on shelf
            if self._try_make_room_and_place(order):
                self._log_action(current_time, order_id, ActionType.PLACE, 
                               order.storage_location, f"Stored {name} after making room")
                self.orders[order_id] = order
                self.stats['orders_placed'] += 1
                return True
            
            # If still can't place, discard an order and place new one
            if self._discard_and_place(order):
                self._log_action(current_time, order_id, ActionType.PLACE, 
                               order.storage_location, f"Stored {name} after discarding old order")
                self.orders[order_id] = order
                self.stats['orders_placed'] += 1
                return True
            
            return False
    
    def _try_store_at_ideal_temperature(self, order: FoodOrder) -> bool:
        """Try to store order at its ideal temperature."""
        if order.temperature == Temperature.COLD and len(self.cooler) < 6:
            self.cooler.append(order)
            order.storage_location = "cooler"
            return True
        elif order.temperature == Temperature.HOT and len(self.heater) < 6:
            self.heater.append(order)
            order.storage_location = "heater"
            return True
        elif order.temperature == Temperature.ROOM and len(self.shelf) < 12:
            self.shelf.append(order)
            order.storage_location = "shelf"
            return True
        return False
    
    def _try_make_room_and_place(self, order: FoodOrder) -> bool:
        """Try to move existing orders to make room for new order."""
        # Try to move cold orders from shelf to cooler
        if order.temperature == Temperature.COLD and len(self.cooler) < 6:
            moved = self._move_from_shelf_to_cooler()
            if moved and len(self.shelf) < 12:
                self.shelf.append(order)
                order.storage_location = "shelf"
                return True
        
        # Try to move hot orders from shelf to heater
        elif order.temperature == Temperature.HOT and len(self.heater) < 6:
            moved = self._move_from_shelf_to_heater()
            if moved and len(self.shelf) < 12:
                self.shelf.append(order)
                order.storage_location = "shelf"
                return True
        
        # Try to place directly on shelf if there's room
        elif len(self.shelf) < 12:
            self.shelf.append(order)
            order.storage_location = "shelf"
            return True
        
        return False
    
    def _move_from_shelf_to_cooler(self) -> bool:
        """Move a cold order from shelf to cooler if possible."""
        for i, order in enumerate(self.shelf):
            if order.temperature == Temperature.COLD and len(self.cooler) < 6:
                moved_order = self.shelf.pop(i)
                self.cooler.append(moved_order)
                moved_order.storage_location = "cooler"
                
                current_time = time.time()
                self._log_action(current_time, moved_order.id, ActionType.MOVE, 
                               "cooler", f"Moved {moved_order.name} from shelf to cooler")
                self.stats['orders_moved'] += 1
                return True
        return False
    
    def _move_from_shelf_to_heater(self) -> bool:
        """Move a hot order from shelf to heater if possible."""
        for i, order in enumerate(self.shelf):
            if order.temperature == Temperature.HOT and len(self.heater) < 6:
                moved_order = self.shelf.pop(i)
                self.heater.append(moved_order)
                moved_order.storage_location = "heater"
                
                current_time = time.time()
                self._log_action(current_time, moved_order.id, ActionType.MOVE, 
                               "heater", f"Moved {moved_order.name} from shelf to heater")
                self.stats['orders_moved'] += 1
                return True
        return False
    
    def _discard_and_place(self, order: FoodOrder) -> bool:
        """Discard an order from shelf to make room for new order."""
        if len(self.shelf) >= 12:
            # Choose order to discard based on freshness and temperature mismatch
            discard_index = self._choose_order_to_discard()
            if discard_index is not None:
                discarded_order = self.shelf.pop(discard_index)
                current_time = time.time()
                
                self._log_action(current_time, discarded_order.id, ActionType.DISCARD, 
                               "shelf", f"Discarded {discarded_order.name} to make room")
                self.stats['orders_discarded'] += 1
                
                # Now place the new order
                self.shelf.append(order)
                order.storage_location = "shelf"
                return True
        
        return False
    
    def _choose_order_to_discard(self) -> Optional[int]:
        """
        Choose which order to discard when shelf is full.
        
        Strategy: Prioritize orders that are:
        1. Already expired/freshness exceeded
        2. Stored at non-ideal temperature (degrading faster)
        3. Closest to expiration
        """
        current_time = time.time()
        best_discard_index = None
        best_discard_score = float('-inf')
        
        for i, order in enumerate(self.shelf):
            # Calculate discard score (higher = better to discard)
            score = 0
            
            # Check if expired
            if not order.is_fresh(current_time):
                score += 1000  # High priority to discard expired orders
            
            # Check temperature mismatch penalty
            if order.storage_location != order.temperature.value:
                score += 500  # Medium priority for temperature mismatches
            
            # Add time-based score (closer to expiration = higher score)
            elapsed_time = current_time - order.stored_at
            ideal_freshness = order.freshness
            if order.storage_location == order.temperature.value:
                time_ratio = elapsed_time / ideal_freshness
            else:
                time_ratio = (elapsed_time * 2) / ideal_freshness
            
            score += int(time_ratio * 100)
            
            if score > best_discard_score:
                best_discard_score = score
                best_discard_index = i
        
        return best_discard_index
    
    def pickup_order(self, order_id: str) -> Optional[FoodOrder]:
        """
        Pick up an order for delivery.
        
        Returns the order if successful, None if not found or expired.
        """
        current_time = time.time()
        
        with self.lock:
            if order_id not in self.orders:
                return None
            
            order = self.orders[order_id]
            
            # Check if order is still fresh
            if not order.is_fresh(current_time):
                # Order expired, discard it
                self._remove_order_from_storage(order)
                self._log_action(current_time, order_id, ActionType.DISCARD, 
                               order.storage_location, f"Discarded expired {order.name}")
                self.stats['orders_discarded'] += 1
                del self.orders[order_id]
                return None
            
            # Remove order from storage
            self._remove_order_from_storage(order)
            self._log_action(current_time, order_id, ActionType.PICKUP, 
                           order.storage_location, f"Picked up {order.name}")
            self.stats['orders_picked_up'] += 1
            
            # Remove from tracking
            del self.orders[order_id]
            
            return order
    
    def _remove_order_from_storage(self, order: FoodOrder):
        """Remove order from its current storage location."""
        if order.storage_location == "cooler":
            self.cooler = [o for o in self.cooler if o.id != order.id]
        elif order.storage_location == "heater":
            self.heater = [o for o in self.heater if o.id != order.id]
        elif order.storage_location == "shelf":
            self.shelf = [o for o in self.shelf if o.id != order.id]
    
    def _log_action(self, timestamp: float, order_id: str, action_type: ActionType, 
                   target: str, details: str = ""):
        """Log a kitchen action to the ledger."""
        action = KitchenAction(
            timestamp=timestamp,
            order_id=order_id,
            action_type=action_type,
            target=target,
            details=details
        )
        self.actions.append(action)
        
        # Output to console in human-readable format
        dt = datetime.fromtimestamp(timestamp)
        time_str = dt.strftime("%H:%M:%S.%f")[:-3]
        print(f"[{time_str}] {action_type.value.upper()}: Order {order_id} -> {target} {details}")
    
    def get_storage_status(self) -> Dict[str, Dict]:
        """Get current storage status."""
        with self.lock:
            return {
                'cooler': {
                    'count': len(self.cooler),
                    'capacity': 6,
                    'orders': [{'id': o.id, 'name': o.name, 'temperature': o.temperature.value} 
                              for o in self.cooler]
                },
                'heater': {
                    'count': len(self.heater),
                    'capacity': 6,
                    'orders': [{'id': o.id, 'name': o.name, 'temperature': o.temperature.value} 
                              for o in self.heater]
                },
                'shelf': {
                    'count': len(self.shelf),
                    'capacity': 12,
                    'orders': [{'id': o.id, 'name': o.name, 'temperature': o.temperature.value} 
                              for o in self.shelf]
                }
            }
    
    def get_actions_ledger(self) -> List[KitchenAction]:
        """Get the complete actions ledger."""
        with self.lock:
            return self.actions.copy()
    
    def get_statistics(self) -> Dict[str, int]:
        """Get system statistics."""
        with self.lock:
            return self.stats.copy()
    
    def cleanup_expired_orders(self):
        """Remove expired orders from storage."""
        current_time = time.time()
        
        with self.lock:
            # Check cooler
            expired_cooler = [o for o in self.cooler if not o.is_fresh(current_time)]
            for order in expired_cooler:
                self.cooler.remove(order)
                self._log_action(current_time, order.id, ActionType.DISCARD, 
                               "cooler", f"Auto-discarded expired {order.name}")
                self.stats['orders_discarded'] += 1
                if order.id in self.orders:
                    del self.orders[order.id]
            
            # Check heater
            expired_heater = [o for o in self.heater if not o.is_fresh(current_time)]
            for order in expired_heater:
                self.heater.remove(order)
                self._log_action(current_time, order.id, ActionType.DISCARD, 
                               "heater", f"Auto-discarded expired {order.name}")
                self.stats['orders_discarded'] += 1
                if order.id in self.orders:
                    del self.orders[order.id]
            
            # Check shelf
            expired_shelf = [o for o in self.shelf if not o.is_fresh(current_time)]
            for order in expired_shelf:
                self.shelf.remove(order)
                self._log_action(current_time, order.id, ActionType.DISCARD, 
                               "shelf", f"Auto-discarded expired {order.name}")
                self.stats['orders_discarded'] += 1
                if order.id in self.orders:
                    del self.orders[order.id]