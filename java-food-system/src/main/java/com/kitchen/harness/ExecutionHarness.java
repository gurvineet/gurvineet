package com.kitchen.harness;

import com.kitchen.model.*;
import com.kitchen.service.KitchenSystem;
import java.util.*;
import java.util.concurrent.*;

/**
 * Main execution harness for the kitchen system.
 */
public class ExecutionHarness {
    private final double rate; // orders per second
    private final int pickupMin; // minimum pickup delay in seconds
    private final int pickupMax; // maximum pickup delay in seconds
    
    private final KitchenSystem kitchen;
    private final MockChallengeServer server;
    
    // Order tracking
    private final Map<String, Long> pendingPickups = new ConcurrentHashMap<>(); // order_id -> pickup_time
    private final List<Future<?>> pickupFutures = new ArrayList<>();
    
    // Control flags
    private volatile boolean running = false;
    private ScheduledExecutorService cleanupExecutor;
    private ExecutorService pickupExecutor;
    
    public ExecutionHarness(double rate, int pickupMin, int pickupMax) {
        this.rate = rate;
        this.pickupMin = pickupMin;
        this.pickupMax = pickupMax;
        
        this.kitchen = new KitchenSystem();
        this.server = new MockChallengeServer();
        
        System.out.println("Kitchen System Initialized");
        System.out.println("Order Rate: " + this.rate + " orders/second");
        System.out.println("Pickup Window: " + this.pickupMin + "-" + this.pickupMax + " seconds");
        System.out.println("=".repeat(50));
    }
    
    /**
     * Start the execution harness.
     */
    public void start() {
        running = true;
        
        // Initialize executors
        cleanupExecutor = Executors.newScheduledThreadPool(1);
        pickupExecutor = Executors.newCachedThreadPool();
        
        // Start cleanup thread for expired orders
        cleanupExecutor.scheduleAtFixedRate(
            () -> {
                if (running) {
                    kitchen.cleanupExpiredOrders();
                }
            }, 
            1, 1, TimeUnit.SECONDS
        );
        
        // Get orders from server
        List<Map<String, Object>> orders = server.getOrders(5); // Get 5 orders for testing
        
        System.out.println("Received " + orders.size() + " orders from server");
        System.out.println("Starting order placement...");
        
        // Place orders at specified rate
        for (int i = 0; i < orders.size(); i++) {
            if (!running) {
                break;
            }
            
            Map<String, Object> orderData = orders.get(i);
            
            // Place the order
            boolean success = kitchen.placeOrder(
                (String) orderData.get("id"),
                (String) orderData.get("name"),
                Temperature.fromString((String) orderData.get("temperature")),
                (Integer) orderData.get("freshness")
            );
            
            if (success) {
                // Schedule pickup
                double pickupDelay = pickupMin + random.nextDouble() * (pickupMax - pickupMin);
                long pickupTime = System.currentTimeMillis() + (long) (pickupDelay * 1000);
                pendingPickups.put((String) orderData.get("id"), pickupTime);
                
                // Start pickup task
                Future<?> pickupFuture = pickupExecutor.submit(() -> 
                    pickupWorker((String) orderData.get("id"), pickupDelay)
                );
                pickupFutures.add(pickupFuture);
                
                System.out.printf("Order %s placed successfully, pickup scheduled in %.1fs%n", 
                                orderData.get("id"), pickupDelay);
            } else {
                System.out.println("Failed to place order " + orderData.get("id"));
            }
            
            // Wait for next order based on rate
            if (i < orders.size() - 1) { // Don't wait after last order
                try {
                    Thread.sleep((long) (1000.0 / rate));
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    break;
                }
            }
        }
        
        System.out.println("All orders placed. Waiting for pickups to complete...");
        
        // Wait for all pickups to complete
        for (Future<?> future : pickupFutures) {
            try {
                future.get();
            } catch (InterruptedException | ExecutionException e) {
                System.err.println("Error waiting for pickup: " + e.getMessage());
            }
        }
        
        // Final cleanup
        finalCleanup();
        
        // Submit actions to server
        submitResults();
        
        System.out.println("Execution completed successfully!");
        
        // Shutdown executors
        shutdown();
    }
    
    private final Random random = new Random();
    
    private void pickupWorker(String orderId, double delay) {
        try {
            Thread.sleep((long) (delay * 1000));
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return;
        }
        
        if (!running) {
            return;
        }
        
        // Attempt pickup
        FoodOrder order = kitchen.pickupOrder(orderId);
        
        if (order != null) {
            System.out.println("Order " + orderId + " picked up successfully");
        } else {
            System.out.println("Order " + orderId + " pickup failed (expired or not found)");
        }
        
        // Remove from pending pickups
        pendingPickups.remove(orderId);
    }
    
    private void finalCleanup() {
        System.out.println("\nPerforming final cleanup...");
        kitchen.cleanupExpiredOrders();
        
        // Show final storage status
        Map<String, Map<String, Object>> status = kitchen.getStorageStatus();
        System.out.println("\nFinal Storage Status:");
        for (Map.Entry<String, Map<String, Object>> entry : status.entrySet()) {
            String location = entry.getKey();
            Map<String, Object> info = entry.getValue();
            System.out.printf("  %s: %d/%d orders%n", 
                            location.substring(0, 1).toUpperCase() + location.substring(1),
                            info.get("count"), info.get("capacity"));
        }
    }
    
    private void submitResults() {
        System.out.println("\nPreparing to submit results...");
        
        // Get all actions
        List<KitchenAction> actions = kitchen.getActionsLedger();
        
        // Convert to server format
        List<Map<String, Object>> serverActions = new ArrayList<>();
        for (KitchenAction action : actions) {
            Map<String, Object> serverAction = new HashMap<>();
            serverAction.put("timestamp", action.getTimestamp());
            serverAction.put("order_id", action.getOrderId());
            serverAction.put("action_type", action.getActionType().getValue());
            serverAction.put("target", action.getTarget());
            serverAction.put("details", action.getDetails());
            serverActions.add(serverAction);
        }
        
        // Submit to server
        Map<String, Object> result = server.submitActions(serverActions);
        
        // Show final statistics
        Map<String, Integer> stats = kitchen.getStatistics();
        System.out.println("\nFinal Statistics:");
        for (Map.Entry<String, Integer> entry : stats.entrySet()) {
            String key = entry.getKey();
            Integer value = entry.getValue();
            System.out.printf("  %s: %d%n", 
                            key.replace("_", " ").toUpperCase(), value);
        }
    }
    
    private void shutdown() {
        if (cleanupExecutor != null) {
            cleanupExecutor.shutdown();
            try {
                if (!cleanupExecutor.awaitTermination(5, TimeUnit.SECONDS)) {
                    cleanupExecutor.shutdownNow();
                }
            } catch (InterruptedException e) {
                cleanupExecutor.shutdownNow();
                Thread.currentThread().interrupt();
            }
        }
        
        if (pickupExecutor != null) {
            pickupExecutor.shutdown();
            try {
                if (!pickupExecutor.awaitTermination(5, TimeUnit.SECONDS)) {
                    pickupExecutor.shutdownNow();
                }
            } catch (InterruptedException e) {
                pickupExecutor.shutdownNow();
                Thread.currentThread().interrupt();
            }
        }
    }
    
    /**
     * Stop the execution harness.
     */
    public void stop() {
        running = false;
        shutdown();
    }
}