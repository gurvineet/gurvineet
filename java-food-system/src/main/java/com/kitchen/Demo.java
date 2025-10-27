package com.kitchen;

import com.kitchen.model.*;
import com.kitchen.service.KitchenSystem;
import java.util.Map;

/**
 * Demo class for the Food Order Fulfillment System.
 */
public class Demo {
    
    public static void main(String[] args) {
        runDemo();
    }
    
    public static void runDemo() {
        System.out.println("🍕 Food Order Fulfillment System Demo");
        System.out.println("=".repeat(50));
        
        // Initialize the kitchen
        KitchenSystem kitchen = new KitchenSystem();
        
        System.out.println("Kitchen initialized with empty storage:");
        printStorageStatus(kitchen);
        
        // Scenario 1: Place some orders
        System.out.println("\n📦 Placing orders...");
        
        String[][] orders = {
            {"pizza_001", "Margherita Pizza", "hot", "300"},
            {"salad_001", "Caesar Salad", "cold", "600"},
            {"bread_001", "Fresh Baguette", "room", "1200"},
            {"ice_cream_001", "Vanilla Ice Cream", "cold", "900"},
            {"soup_001", "Tomato Soup", "hot", "600"}
        };
        
        for (String[] orderData : orders) {
            String orderId = orderData[0];
            String name = orderData[1];
            Temperature temp = Temperature.fromString(orderData[2]);
            int freshness = Integer.parseInt(orderData[3]);
            
            boolean success = kitchen.placeOrder(orderId, name, temp, freshness);
            if (success) {
                System.out.println("  ✓ " + name + " placed successfully");
            } else {
                System.out.println("  ❌ Failed to place " + name);
            }
        }
        
        System.out.println("\nStorage status after placing orders:");
        printStorageStatus(kitchen);
        
        // Scenario 2: Show some pickups
        System.out.println("\n🚚 Picking up orders...");
        
        // Pickup pizza
        FoodOrder order = kitchen.pickupOrder("pizza_001");
        if (order != null) {
            System.out.println("  ✓ " + order.getName() + " picked up successfully");
        } else {
            System.out.println("  ❌ Failed to pickup pizza_001");
        }
        
        // Pickup salad
        order = kitchen.pickupOrder("salad_001");
        if (order != null) {
            System.out.println("  ✓ " + order.getName() + " picked up successfully");
        } else {
            System.out.println("  ❌ Failed to pickup salad_001");
        }
        
        System.out.println("\nStorage status after pickups:");
        printStorageStatus(kitchen);
        
        // Scenario 3: Show action ledger
        System.out.println("\n📋 Action Ledger:");
        var actions = kitchen.getActionsLedger();
        for (var action : actions) {
            System.out.printf("  [%s] %s: %s -> %s%n", 
                            action.getFormattedTimestamp(), 
                            action.getActionType().getValue().toUpperCase(), 
                            action.getOrderId(), action.getTarget());
        }
        
        // Scenario 4: Show statistics
        System.out.println("\n📊 System Statistics:");
        var stats = kitchen.getStatistics();
        for (var entry : stats.entrySet()) {
            String key = entry.getKey();
            Integer value = entry.getValue();
            System.out.printf("  %s: %d%n", 
                            key.replace("_", " ").toUpperCase(), value);
        }
        
        System.out.println("\n🎉 Demo completed successfully!");
    }
    
    private static void printStorageStatus(KitchenSystem kitchen) {
        Map<String, Map<String, Object>> status = kitchen.getStorageStatus();
        
        for (var entry : status.entrySet()) {
            String location = entry.getKey();
            Map<String, Object> info = entry.getValue();
            System.out.printf("  %s: %d/%d orders%n", 
                            location.substring(0, 1).toUpperCase() + location.substring(1),
                            info.get("count"), info.get("capacity"));
            
            @SuppressWarnings("unchecked")
            var orders = (java.util.List<Map<String, String>>) info.get("orders");
            for (var order : orders) {
                System.out.printf("    - %s (%s)%n", 
                                order.get("name"), order.get("temperature"));
            }
        }
    }
}