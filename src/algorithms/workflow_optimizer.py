"""
Workflow Optimization Algorithm

Core algorithm for optimizing kitchen workflow based on food spoilage,
order priority, and resource constraints.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import heapq
from ..models.food_item import FoodItem
from ..models.order import Order, OrderStatus, OrderPriority


@dataclass
class OptimizationResult:
    """
    Result of workflow optimization.
    
    Attributes:
        optimized_order_sequence: List of orders in optimal processing sequence
        total_processing_time: Estimated total time to process all orders
        spoilage_risk_reduction: Reduction in spoilage risk achieved
        efficiency_score: Overall efficiency score (0-1)
        recommendations: List of optimization recommendations
    """
    optimized_order_sequence: List[Order]
    total_processing_time: int
    spoilage_risk_reduction: float
    efficiency_score: float
    recommendations: List[str]


class WorkflowOptimizer:
    """
    Main class for optimizing kitchen workflow.
    
    Uses multiple algorithms to determine optimal order processing sequence
    based on spoilage risk, order priority, and resource constraints.
    """
    
    def __init__(self, max_concurrent_orders: int = 3, 
                 time_buffer_minutes: int = 15):
        """
        Initialize the workflow optimizer.
        
        Args:
            max_concurrent_orders: Maximum number of orders that can be processed simultaneously
            time_buffer_minutes: Buffer time between orders for setup/cleanup
        """
        self.max_concurrent_orders = max_concurrent_orders
        self.time_buffer_minutes = time_buffer_minutes
        self.optimization_history: List[OptimizationResult] = []
    
    def optimize_workflow(self, orders: List[Order], 
                         current_time: Optional[datetime] = None) -> OptimizationResult:
        """
        Optimize the workflow for a given set of orders.
        
        Args:
            orders: List of orders to optimize
            current_time: Current time for calculations (defaults to now)
            
        Returns:
            OptimizationResult with optimized sequence and metrics
        """
        if current_time is None:
            current_time = datetime.now()
        
        if not orders:
            return OptimizationResult(
                optimized_order_sequence=[],
                total_processing_time=0,
                spoilage_risk_reduction=0.0,
                efficiency_score=1.0,
                recommendations=["No orders to process"]
            )
        
        # Filter out completed/cancelled orders
        active_orders = [order for order in orders 
                        if order.status not in [OrderStatus.DELIVERED, OrderStatus.CANCELLED]]
        
        if not active_orders:
            return OptimizationResult(
                optimized_order_sequence=[],
                total_processing_time=0,
                spoilage_risk_reduction=0.0,
                efficiency_score=1.0,
                recommendations=["No active orders to process"]
            )
        
        # Calculate initial spoilage risk
        initial_risk = self._calculate_total_spoilage_risk(active_orders)
        
        # Apply multiple optimization strategies
        optimized_sequence = self._apply_optimization_strategies(active_orders, current_time)
        
        # Calculate final metrics
        final_risk = self._calculate_total_spoilage_risk(optimized_sequence)
        risk_reduction = initial_risk - final_risk
        
        total_time = self._calculate_total_processing_time(optimized_sequence)
        efficiency_score = self._calculate_efficiency_score(optimized_sequence, total_time)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(optimized_sequence, risk_reduction)
        
        result = OptimizationResult(
            optimized_order_sequence=optimized_sequence,
            total_processing_time=total_time,
            spoilage_risk_reduction=risk_reduction,
            efficiency_score=efficiency_score,
            recommendations=recommendations
        )
        
        # Store result in history
        self.optimization_history.append(result)
        
        return result
    
    def _apply_optimization_strategies(self, orders: List[Order], 
                                     current_time: datetime) -> List[Order]:
        """
        Apply multiple optimization strategies to determine optimal sequence.
        
        Args:
            orders: List of orders to optimize
            current_time: Current time for calculations
            
        Returns:
            Optimized order sequence
        """
        # Strategy 1: Priority-based sorting
        priority_sorted = self._priority_based_sorting(orders, current_time)
        
        # Strategy 2: Spoilage risk minimization
        spoilage_optimized = self._spoilage_risk_optimization(priority_sorted, current_time)
        
        # Strategy 3: Resource constraint optimization
        resource_optimized = self._resource_constraint_optimization(spoilage_optimized)
        
        # Strategy 4: Batch optimization for similar items
        batch_optimized = self._batch_optimization(resource_optimized)
        
        return batch_optimized
    
    def _priority_based_sorting(self, orders: List[Order], 
                               current_time: datetime) -> List[Order]:
        """
        Sort orders by priority score.
        
        Args:
            orders: List of orders to sort
            current_time: Current time for calculations
            
        Returns:
            Orders sorted by priority
        """
        # Calculate priority scores for all orders
        order_scores = []
        for order in orders:
            priority_score = order.get_priority_score()
            # Use negative score for max-heap behavior
            heapq.heappush(order_scores, (-priority_score, order.id, order))
        
        # Extract orders in priority order
        sorted_orders = []
        while order_scores:
            _, _, order = heapq.heappop(order_scores)
            sorted_orders.append(order)
        
        return sorted_orders
    
    def _spoilage_risk_optimization(self, orders: List[Order], 
                                   current_time: datetime) -> List[Order]:
        """
        Optimize order sequence to minimize spoilage risk.
        
        Args:
            orders: List of orders to optimize
            current_time: Current time for calculations
            
        Returns:
            Orders optimized for spoilage risk
        """
        if len(orders) <= 1:
            return orders
        
        # Use dynamic programming to find optimal sequence
        # This is a simplified version - in production, you might use more sophisticated algorithms
        
        # Sort by spoilage risk (highest risk first)
        risk_sorted = sorted(orders, 
                            key=lambda o: o.get_spoilage_risk_score(), 
                            reverse=True)
        
        # Apply time-based constraints
        optimized = self._apply_time_constraints(risk_sorted, current_time)
        
        return optimized
    
    def _apply_time_constraints(self, orders: List[Order], 
                               current_time: datetime) -> List[Order]:
        """
        Apply time-based constraints to order sequence.
        
        Args:
            orders: List of orders to optimize
            current_time: Current time for calculations
            
        Returns:
            Orders with time constraints applied
        """
        if not orders:
            return orders
        
        # Calculate cumulative processing time
        cumulative_time = 0
        optimized_orders = []
        
        for order in orders:
            # Check if order can be processed within spoilage time
            if order.items:
                max_spoilage_time = min(item.food_item.spoilage_rate_hours 
                                      for item in order.items)
                max_processing_time = max_spoilage_time * 60  # Convert to minutes
                
                if cumulative_time <= max_processing_time:
                    optimized_orders.append(order)
                    cumulative_time += order.estimated_preparation_time + self.time_buffer_minutes
                else:
                    # Order would spoil before processing - move to front
                    optimized_orders.insert(0, order)
                    cumulative_time = order.estimated_preparation_time + self.time_buffer_minutes
            else:
                optimized_orders.append(order)
                cumulative_time += self.time_buffer_minutes
        
        return optimized_orders
    
    def _resource_constraint_optimization(self, orders: List[Order]) -> List[Order]:
        """
        Optimize order sequence considering resource constraints.
        
        Args:
            orders: List of orders to optimize
            
        Returns:
            Orders optimized for resource constraints
        """
        if len(orders) <= self.max_concurrent_orders:
            return orders
        
        # Simple approach: ensure we don't exceed concurrent order limit
        # In production, you might use more sophisticated resource allocation
        
        optimized = []
        current_batch = []
        
        for order in orders:
            if len(current_batch) < self.max_concurrent_orders:
                current_batch.append(order)
            else:
                # Process current batch
                optimized.extend(current_batch)
                current_batch = [order]
        
        # Add remaining orders
        optimized.extend(current_batch)
        
        return optimized
    
    def _batch_optimization(self, orders: List[Order]) -> List[Order]:
        """
        Optimize order sequence by batching similar items.
        
        Args:
            orders: List of orders to optimize
            
        Returns:
            Orders optimized with batching
        """
        if len(orders) <= 1:
            return orders
        
        # Group orders by food categories
        category_groups: Dict[str, List[Order]] = {}
        
        for order in orders:
            for item in order.items:
                category = item.food_item.category.value
                if category not in category_groups:
                    category_groups[category] = []
                category_groups[category].append(order)
        
        # Process orders by category to minimize setup/cleanup time
        optimized = []
        processed_orders = set()
        
        for category, category_orders in category_groups.items():
            # Sort orders within category by priority
            category_orders.sort(key=lambda o: o.get_priority_score(), reverse=True)
            
            for order in category_orders:
                if order.id not in processed_orders:
                    optimized.append(order)
                    processed_orders.add(order.id)
        
        # Add any remaining orders
        for order in orders:
            if order.id not in processed_orders:
                optimized.append(order)
        
        return optimized
    
    def _calculate_total_spoilage_risk(self, orders: List[Order]) -> float:
        """
        Calculate total spoilage risk across all orders.
        
        Args:
            orders: List of orders to evaluate
            
        Returns:
            Total spoilage risk score
        """
        if not orders:
            return 0.0
        
        total_risk = sum(order.get_spoilage_risk_score() for order in orders)
        return total_risk / len(orders)  # Average risk
    
    def _calculate_total_processing_time(self, orders: List[Order]) -> int:
        """
        Calculate total processing time for all orders.
        
        Args:
            orders: List of orders to evaluate
            
        Returns:
            Total processing time in minutes
        """
        if not orders:
            return 0
        
        total_time = sum(order.estimated_preparation_time for order in orders)
        # Add buffer time between orders
        buffer_time = (len(orders) - 1) * self.time_buffer_minutes
        
        return total_time + buffer_time
    
    def _calculate_efficiency_score(self, orders: List[Order], 
                                  total_time: int) -> float:
        """
        Calculate overall efficiency score.
        
        Args:
            orders: List of orders to evaluate
            total_time: Total processing time
            
        Returns:
            Efficiency score (0-1, where 1 is most efficient)
        """
        if not orders:
            return 1.0
        
        # Factors affecting efficiency:
        # 1. Processing time (lower is better)
        # 2. Number of orders (higher is better for throughput)
        # 3. Spoilage risk (lower is better)
        
        # Normalize processing time (assume 8-hour shift = 480 minutes)
        time_efficiency = max(0, 1 - (total_time / 480))
        
        # Order throughput efficiency
        throughput_efficiency = min(len(orders) / 20, 1.0)  # Assume 20 orders per shift is optimal
        
        # Spoilage efficiency
        avg_spoilage_risk = self._calculate_total_spoilage_risk(orders)
        spoilage_efficiency = 1 - avg_spoilage_risk
        
        # Weighted combination
        efficiency = (0.4 * time_efficiency + 
                     0.3 * throughput_efficiency + 
                     0.3 * spoilage_efficiency)
        
        return max(0.0, min(1.0, efficiency))
    
    def _generate_recommendations(self, orders: List[Order], 
                                 risk_reduction: float) -> List[str]:
        """
        Generate optimization recommendations.
        
        Args:
            orders: List of optimized orders
            risk_reduction: Achieved spoilage risk reduction
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if risk_reduction > 0.1:
            recommendations.append(f"Significant spoilage risk reduction achieved: {risk_reduction:.2f}")
        
        # Check for high-risk items
        high_risk_orders = [order for order in orders 
                           if order.get_spoilage_risk_score() > 0.8]
        if high_risk_orders:
            recommendations.append(f"Consider expediting {len(high_risk_orders)} high-risk orders")
        
        # Check for resource utilization
        if len(orders) > self.max_concurrent_orders:
            recommendations.append(f"Consider increasing concurrent order capacity beyond {self.max_concurrent_orders}")
        
        # Check for batch optimization opportunities
        category_counts = {}
        for order in orders:
            for item in order.items:
                category = item.food_item.category.value
                category_counts[category] = category_counts.get(category, 0) + 1
        
        for category, count in category_counts.items():
            if count > 3:
                recommendations.append(f"Consider batch processing for {category} items ({count} orders)")
        
        if not recommendations:
            recommendations.append("Workflow is well-optimized with current constraints")
        
        return recommendations
    
    def get_optimization_history(self) -> List[OptimizationResult]:
        """Get history of optimization results."""
        return self.optimization_history.copy()
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Get performance metrics from optimization history."""
        if not self.optimization_history:
            return {}
        
        recent_results = self.optimization_history[-10:]  # Last 10 optimizations
        
        metrics = {
            'avg_efficiency_score': sum(r.efficiency_score for r in recent_results) / len(recent_results),
            'avg_risk_reduction': sum(r.spoilage_risk_reduction for r in recent_results) / len(recent_results),
            'avg_processing_time': sum(r.total_processing_time for r in recent_results) / len(recent_results),
            'total_orders_optimized': sum(len(r.optimized_order_sequence) for r in recent_results)
        }
        
        return metrics