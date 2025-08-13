package com.kitchen.harness;

import com.kitchen.model.ActionType;
import java.util.*;

/**
 * Mock challenge server for testing purposes.
 */
public class MockChallengeServer {
    // Sample food items with realistic properties
    private final List<Map<String, Object>> foodItems = Arrays.asList(
        Map.of("name", "Cheese Pizza", "temperature", "hot", "freshness", 300),      // 5 min
        Map.of("name", "Caesar Salad", "temperature", "cold", "freshness", 600),     // 10 min
        Map.of("name", "Chicken Wings", "temperature", "hot", "freshness", 450),     // 7.5 min
        Map.of("name", "Ice Cream", "temperature", "cold", "freshness", 900),        // 15 min
        Map.of("name", "Sandwich", "temperature", "room", "freshness", 1200),        // 20 min
        Map.of("name", "Soup", "temperature", "hot", "freshness", 600),             // 10 min
        Map.of("name", "Sushi", "temperature", "cold", "freshness", 300),           // 5 min
        Map.of("name", "Bread", "temperature", "room", "freshness", 1800),          // 30 min
        Map.of("name", "Steak", "temperature", "hot", "freshness", 480),            // 8 min
        Map.of("name", "Milk", "temperature", "cold", "freshness", 720)             // 12 min
    );
    
    private final Random random = new Random();
    
    /**
     * Get a list of orders for testing.
     */
    public List<Map<String, Object>> getOrders(int count) {
        List<Map<String, Object>> orders = new ArrayList<>();
        for (int i = 0; i < count; i++) {
            Map<String, Object> foodItem = foodItems.get(random.nextInt(foodItems.size()));
            Map<String, Object> order = new HashMap<>();
            order.put("id", String.format("order_%03d_%d", i, random.nextInt(9000) + 1000));
            order.put("name", foodItem.get("name"));
            order.put("temperature", foodItem.get("temperature"));
            order.put("freshness", foodItem.get("freshness"));
            orders.add(order);
        }
        return orders;
    }
    
    /**
     * Submit actions to the challenge server.
     */
    public Map<String, Object> submitActions(List<Map<String, Object>> actions) {
        // In a real implementation, this would send data to the actual server
        System.out.println("\n=== SUBMITTING ACTIONS TO CHALLENGE SERVER ===");
        System.out.println("Total actions: " + actions.size());
        
        // Simulate server response
        Map<String, Object> result = new HashMap<>();
        result.put("status", "success");
        result.put("message", "Actions submitted successfully");
        result.put("action_count", actions.size());
        result.put("timestamp", System.currentTimeMillis());
        
        System.out.println("Server response: " + result);
        return result;
    }
}