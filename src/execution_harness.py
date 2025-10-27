#!/usr/bin/env python3
"""
Execution Harness for Food Order Fulfillment System

This harness exercises the real-time kitchen system with configurable
order placement and pickup rates.
"""

import time
import random
import threading
import argparse
from typing import List, Dict, Any
from kitchen_system import KitchenSystem, Temperature, FoodOrder


class MockChallengeServer:
    """Mock challenge server for testing purposes."""
    
    def __init__(self):
        # Sample food items with realistic properties
        self.food_items = [
            {"name": "Cheese Pizza", "temperature": "hot", "freshness": 300},  # 5 min
            {"name": "Caesar Salad", "temperature": "cold", "freshness": 600},  # 10 min
            {"name": "Chicken Wings", "temperature": "hot", "freshness": 450},  # 7.5 min
            {"name": "Ice Cream", "temperature": "cold", "freshness": 900},    # 15 min
            {"name": "Sandwich", "temperature": "room", "freshness": 1200},   # 20 min
            {"name": "Soup", "temperature": "hot", "freshness": 600},         # 10 min
            {"name": "Sushi", "temperature": "cold", "freshness": 300},       # 5 min
            {"name": "Bread", "temperature": "room", "freshness": 1800},      # 30 min
            {"name": "Steak", "temperature": "hot", "freshness": 480},        # 8 min
            {"name": "Milk", "temperature": "cold", "freshness": 720},        # 12 min
        ]
    
    def get_orders(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get a list of orders for testing."""
        orders = []
        for i in range(count):
            food_item = random.choice(self.food_items)
            order = {
                "id": f"order_{i:03d}_{random.randint(1000, 9999)}",
                "name": food_item["name"],
                "temperature": food_item["temperature"],
                "freshness": food_item["freshness"]
            }
            orders.append(order)
        return orders
    
    def submit_actions(self, actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Submit actions to the challenge server."""
        # In a real implementation, this would send data to the actual server
        print(f"\n=== SUBMITTING ACTIONS TO CHALLENGE SERVER ===")
        print(f"Total actions: {len(actions)}")
        
        # Simulate server response
        result = {
            "status": "success",
            "message": "Actions submitted successfully",
            "action_count": len(actions),
            "timestamp": time.time()
        }
        
        print(f"Server response: {result}")
        return result


class ExecutionHarness:
    """Main execution harness for the kitchen system."""
    
    def __init__(self, rate: float = 2.0, pickup_min: int = 4, pickup_max: int = 8):
        self.rate = rate  # orders per second
        self.pickup_min = pickup_min  # minimum pickup delay in seconds
        self.pickup_max = pickup_max  # maximum pickup delay in seconds
        
        self.kitchen = KitchenSystem()
        self.server = MockChallengeServer()
        
        # Order tracking
        self.pending_pickups: Dict[str, float] = {}  # order_id -> pickup_time
        self.pickup_threads: List[threading.Thread] = []
        
        # Control flags
        self.running = False
        self.cleanup_thread = None
        
        print(f"Kitchen System Initialized")
        print(f"Order Rate: {self.rate} orders/second")
        print(f"Pickup Window: {self.pickup_min}-{self.pickup_max} seconds")
        print("=" * 50)
    
    def start(self):
        """Start the execution harness."""
        self.running = True
        
        # Start cleanup thread for expired orders
        self.cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True)
        self.cleanup_thread.start()
        
        # Get orders from server
        orders = self.server.get_orders(count=20)  # Get 20 orders for testing
        
        print(f"Received {len(orders)} orders from server")
        print("Starting order placement...")
        
        # Place orders at specified rate
        for i, order_data in enumerate(orders):
            if not self.running:
                break
            
            # Place the order
            success = self.kitchen.place_order(
                order_id=order_data["id"],
                name=order_data["name"],
                temperature=Temperature(order_data["temperature"]),
                freshness=order_data["freshness"]
            )
            
            if success:
                # Schedule pickup
                pickup_delay = random.uniform(self.pickup_min, self.pickup_max)
                pickup_time = time.time() + pickup_delay
                self.pending_pickups[order_data["id"]] = pickup_time
                
                # Start pickup thread
                pickup_thread = threading.Thread(
                    target=self._pickup_worker,
                    args=(order_data["id"], pickup_delay),
                    daemon=True
                )
                pickup_thread.start()
                self.pickup_threads.append(pickup_thread)
                
                print(f"Order {order_data['id']} placed successfully, pickup scheduled in {pickup_delay:.1f}s")
            else:
                print(f"Failed to place order {order_data['id']}")
            
            # Wait for next order based on rate
            if i < len(orders) - 1:  # Don't wait after last order
                time.sleep(1.0 / self.rate)
        
        print(f"All orders placed. Waiting for pickups to complete...")
        
        # Wait for all pickups to complete
        for thread in self.pickup_threads:
            thread.join()
        
        # Final cleanup
        self._final_cleanup()
        
        # Submit actions to server
        self._submit_results()
        
        print("Execution completed successfully!")
    
    def _pickup_worker(self, order_id: str, delay: float):
        """Worker thread to handle order pickup after delay."""
        time.sleep(delay)
        
        if not self.running:
            return
        
        # Attempt pickup
        order = self.kitchen.pickup_order(order_id)
        
        if order:
            print(f"Order {order_id} picked up successfully")
        else:
            print(f"Order {order_id} pickup failed (expired or not found)")
        
        # Remove from pending pickups
        if order_id in self.pending_pickups:
            del self.pending_pickups[order_id]
    
    def _cleanup_worker(self):
        """Worker thread to periodically clean up expired orders."""
        while self.running:
            time.sleep(1.0)  # Check every second
            self.kitchen.cleanup_expired_orders()
    
    def _final_cleanup(self):
        """Final cleanup of any remaining expired orders."""
        print("\nPerforming final cleanup...")
        self.kitchen.cleanup_expired_orders()
        
        # Show final storage status
        status = self.kitchen.get_storage_status()
        print("\nFinal Storage Status:")
        for location, info in status.items():
            print(f"  {location.title()}: {info['count']}/{info['capacity']} orders")
    
    def _submit_results(self):
        """Submit results to the challenge server."""
        print("\nPreparing to submit results...")
        
        # Get all actions
        actions = self.kitchen.get_actions_ledger()
        
        # Convert to server format
        server_actions = []
        for action in actions:
            server_action = {
                "timestamp": action.timestamp,
                "order_id": action.order_id,
                "action_type": action.action_type.value,
                "target": action.target,
                "details": action.details
            }
            server_actions.append(server_action)
        
        # Submit to server
        result = self.server.submit_actions(server_actions)
        
        # Show final statistics
        stats = self.kitchen.get_statistics()
        print(f"\nFinal Statistics:")
        for key, value in stats.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
        
        return result
    
    def stop(self):
        """Stop the execution harness."""
        self.running = False
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=1.0)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Food Order Fulfillment System Harness")
    parser.add_argument("--rate", type=float, default=2.0, 
                       help="Order placement rate in orders per second (default: 2.0)")
    parser.add_argument("--pickup-min", type=int, default=4,
                       help="Minimum pickup delay in seconds (default: 4)")
    parser.add_argument("--pickup-max", type=int, default=8,
                       help="Maximum pickup delay in seconds (default: 8)")
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.rate <= 0:
        print("Error: Rate must be positive")
        return 1
    
    if args.pickup_min < 0 or args.pickup_max < args.pickup_min:
        print("Error: Invalid pickup time range")
        return 1
    
    try:
        # Create and run harness
        harness = ExecutionHarness(
            rate=args.rate,
            pickup_min=args.pickup_min,
            pickup_max=args.pickup_max
        )
        
        harness.start()
        
    except KeyboardInterrupt:
        print("\nExecution interrupted by user")
        return 1
    except Exception as e:
        print(f"Error during execution: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())