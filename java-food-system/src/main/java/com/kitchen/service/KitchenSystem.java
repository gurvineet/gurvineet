package com.kitchen.service;

import com.kitchen.model.*;
import java.util.*;
import java.util.concurrent.locks.ReentrantReadWriteLock;
import java.util.concurrent.locks.ReadWriteLock;

/**
 * Main kitchen system managing order fulfillment and storage.
 */
public class KitchenSystem {
    // Storage containers with capacity limits
    private final List<FoodOrder> cooler = new ArrayList<>();  // Max 6 cold orders
    private final List<FoodOrder> heater = new ArrayList<>();  // Max 6 hot orders
    private final List<FoodOrder> shelf = new ArrayList<>();   // Max 12 orders
    
    // Order tracking
    private final Map<String, FoodOrder> orders = new HashMap<>();
    
    // Action ledger
    private final List<KitchenAction> actions = new ArrayList<>();
    
    // Thread safety
    private final ReadWriteLock lock = new ReentrantReadWriteLock();
    
    // Statistics
    private final Map<String, Integer> stats = new HashMap<>();
    
    public KitchenSystem() {
        stats.put("orders_placed", 0);
        stats.put("orders_picked_up", 0);
        stats.put("orders_discarded", 0);
        stats.put("orders_moved", 0);
    }
    
    /**
     * Place a new order in the kitchen system.
     * 
     * @return true if successfully placed, false otherwise
     */
    public boolean placeOrder(String orderId, String name, Temperature temperature, int freshness) {
        long currentTime = System.currentTimeMillis();
        
        lock.writeLock().lock();
        try {
            // Create the order
            FoodOrder order = new FoodOrder(orderId, name, temperature, freshness, 
                                         currentTime, currentTime, "");
            
            // Try to store at ideal temperature first
            if (tryStoreAtIdealTemperature(order)) {
                logAction(currentTime, orderId, ActionType.PLACE, 
                         order.getStorageLocation(), "Stored " + name + " at ideal temperature");
                orders.put(orderId, order);
                stats.put("orders_placed", stats.get("orders_placed") + 1);
                return true;
            }
            
            // If ideal storage is full, try to move existing orders and place on shelf
            if (tryMakeRoomAndPlace(order)) {
                logAction(currentTime, orderId, ActionType.PLACE, 
                         order.getStorageLocation(), "Stored " + name + " after making room");
                orders.put(orderId, order);
                stats.put("orders_placed", stats.get("orders_placed") + 1);
                return true;
            }
            
            // If still can't place, discard an order and place new one
            if (discardAndPlace(order)) {
                logAction(currentTime, orderId, ActionType.PLACE, 
                         order.getStorageLocation(), "Stored " + name + " after discarding old order");
                orders.put(orderId, order);
                stats.put("orders_placed", stats.get("orders_placed") + 1);
                return true;
            }
            
            return false;
        } finally {
            lock.writeLock().unlock();
        }
    }
    
    private boolean tryStoreAtIdealTemperature(FoodOrder order) {
        if (order.getTemperature() == Temperature.COLD && cooler.size() < 6) {
            cooler.add(order);
            order.setStorageLocation("cooler");
            return true;
        } else if (order.getTemperature() == Temperature.HOT && heater.size() < 6) {
            heater.add(order);
            order.setStorageLocation("heater");
            return true;
        } else if (order.getTemperature() == Temperature.ROOM && shelf.size() < 12) {
            shelf.add(order);
            order.setStorageLocation("shelf");
            return true;
        }
        return false;
    }
    
    private boolean tryMakeRoomAndPlace(FoodOrder order) {
        // Try to move cold orders from shelf to cooler
        if (order.getTemperature() == Temperature.COLD && cooler.size() < 6) {
            boolean moved = moveFromShelfToCooler();
            if (moved && shelf.size() < 12) {
                shelf.add(order);
                order.setStorageLocation("shelf");
                return true;
            }
        }
        
        // Try to move hot orders from shelf to heater
        else if (order.getTemperature() == Temperature.HOT && heater.size() < 6) {
            boolean moved = moveFromShelfToHeater();
            if (moved && shelf.size() < 12) {
                shelf.add(order);
                order.setStorageLocation("shelf");
                return true;
            }
        }
        
        // Try to place directly on shelf if there's room
        else if (shelf.size() < 12) {
            shelf.add(order);
            order.setStorageLocation("shelf");
            return true;
        }
        
        return false;
    }
    
    private boolean moveFromShelfToCooler() {
        for (int i = 0; i < shelf.size(); i++) {
            FoodOrder order = shelf.get(i);
            if (order.getTemperature() == Temperature.COLD && cooler.size() < 6) {
                FoodOrder movedOrder = shelf.remove(i);
                cooler.add(movedOrder);
                movedOrder.setStorageLocation("cooler");
                
                long currentTime = System.currentTimeMillis();
                logAction(currentTime, movedOrder.getId(), ActionType.MOVE, 
                         "cooler", "Moved " + movedOrder.getName() + " from shelf to cooler");
                stats.put("orders_moved", stats.get("orders_moved") + 1);
                return true;
            }
        }
        return false;
    }
    
    private boolean moveFromShelfToHeater() {
        for (int i = 0; i < shelf.size(); i++) {
            FoodOrder order = shelf.get(i);
            if (order.getTemperature() == Temperature.HOT && heater.size() < 6) {
                FoodOrder movedOrder = shelf.remove(i);
                heater.add(movedOrder);
                movedOrder.setStorageLocation("heater");
                
                long currentTime = System.currentTimeMillis();
                logAction(currentTime, movedOrder.getId(), ActionType.MOVE, 
                         "heater", "Moved " + movedOrder.getName() + " from shelf to heater");
                stats.put("orders_moved", stats.get("orders_moved") + 1);
                return true;
            }
        }
        return false;
    }
    
    private boolean discardAndPlace(FoodOrder order) {
        if (shelf.size() >= 12) {
            // Choose order to discard based on freshness and temperature mismatch
            Integer discardIndex = chooseOrderToDiscard();
            if (discardIndex != null) {
                FoodOrder discardedOrder = shelf.remove((int) discardIndex);
                long currentTime = System.currentTimeMillis();
                
                logAction(currentTime, discardedOrder.getId(), ActionType.DISCARD, 
                         "shelf", "Discarded " + discardedOrder.getName() + " to make room");
                stats.put("orders_discarded", stats.get("orders_discarded") + 1);
                
                // Now place the new order
                shelf.add(order);
                order.setStorageLocation("shelf");
                return true;
            }
        }
        
        return false;
    }
    
    private Integer chooseOrderToDiscard() {
        /**
         * Choose which order to discard when shelf is full.
         * 
         * Strategy: Prioritize orders that are:
         * 1. Already expired/freshness exceeded
         * 2. Stored at non-ideal temperature (degrading faster)
         * 3. Closest to expiration
         */
        long currentTime = System.currentTimeMillis();
        Integer bestDiscardIndex = null;
        double bestDiscardScore = Double.NEGATIVE_INFINITY;
        
        for (int i = 0; i < shelf.size(); i++) {
            FoodOrder order = shelf.get(i);
            // Calculate discard score (higher = better to discard)
            double score = 0;
            
            // Check if expired
            if (!order.isFresh(currentTime)) {
                score += 1000; // High priority to discard expired orders
            }
            
            // Check temperature mismatch penalty
            if (!order.getStorageLocation().equals(order.getTemperature().getValue())) {
                score += 500; // Medium priority for temperature mismatches
            }
            
            // Add time-based score (closer to expiration = higher score)
            long elapsedTime = currentTime - order.getStoredAt();
            long idealFreshness = order.getFreshness();
            double timeRatio;
            if (order.getStorageLocation().equals(order.getTemperature().getValue())) {
                timeRatio = (double) elapsedTime / idealFreshness;
            } else {
                timeRatio = (double) (elapsedTime * 2) / idealFreshness;
            }
            
            score += (int) (timeRatio * 100);
            
            if (score > bestDiscardScore) {
                bestDiscardScore = score;
                bestDiscardIndex = i;
            }
        }
        
        return bestDiscardIndex;
    }
    
    /**
     * Pick up an order for delivery.
     * 
     * @return the order if successful, null if not found or expired
     */
    public FoodOrder pickupOrder(String orderId) {
        long currentTime = System.currentTimeMillis();
        
        lock.writeLock().lock();
        try {
            if (!orders.containsKey(orderId)) {
                return null;
            }
            
            FoodOrder order = orders.get(orderId);
            
            // Check if order is still fresh
            if (!order.isFresh(currentTime)) {
                // Order expired, discard it
                removeOrderFromStorage(order);
                logAction(currentTime, orderId, ActionType.DISCARD, 
                         order.getStorageLocation(), "Discarded expired " + order.getName());
                stats.put("orders_discarded", stats.get("orders_discarded") + 1);
                orders.remove(orderId);
                return null;
            }
            
            // Remove order from storage
            removeOrderFromStorage(order);
            logAction(currentTime, orderId, ActionType.PICKUP, 
                     order.getStorageLocation(), "Picked up " + order.getName());
            stats.put("orders_picked_up", stats.get("orders_picked_up") + 1);
            
            // Remove from tracking
            orders.remove(orderId);
            
            return order;
        } finally {
            lock.writeLock().unlock();
        }
    }
    
    private void removeOrderFromStorage(FoodOrder order) {
        if ("cooler".equals(order.getStorageLocation())) {
            cooler.removeIf(o -> o.getId().equals(order.getId()));
        } else if ("heater".equals(order.getStorageLocation())) {
            heater.removeIf(o -> o.getId().equals(order.getId()));
        } else if ("shelf".equals(order.getStorageLocation())) {
            shelf.removeIf(o -> o.getId().equals(order.getId()));
        }
    }
    
    private void logAction(long timestamp, String orderId, ActionType actionType, 
                          String target, String details) {
        // Log action to the ledger
        KitchenAction action = new KitchenAction(timestamp, orderId, actionType, target, details);
        actions.add(action);
        
        // Output to console in human-readable format
        System.out.printf("[%s] %s: Order %s -> %s %s%n", 
                         action.getFormattedTimestamp(), 
                         actionType.getValue().toUpperCase(), 
                         orderId, target, details);
    }
    
    /**
     * Get current storage status.
     */
    public Map<String, Map<String, Object>> getStorageStatus() {
        lock.readLock().lock();
        try {
            Map<String, Map<String, Object>> status = new HashMap<>();
            
            // Cooler status
            Map<String, Object> coolerStatus = new HashMap<>();
            coolerStatus.put("count", cooler.size());
            coolerStatus.put("capacity", 6);
            List<Map<String, String>> coolerOrders = new ArrayList<>();
            for (FoodOrder order : cooler) {
                Map<String, String> orderInfo = new HashMap<>();
                orderInfo.put("id", order.getId());
                orderInfo.put("name", order.getName());
                orderInfo.put("temperature", order.getTemperature().getValue());
                coolerOrders.add(orderInfo);
            }
            coolerStatus.put("orders", coolerOrders);
            status.put("cooler", coolerStatus);
            
            // Heater status
            Map<String, Object> heaterStatus = new HashMap<>();
            heaterStatus.put("count", heater.size());
            heaterStatus.put("capacity", 6);
            List<Map<String, String>> heaterOrders = new ArrayList<>();
            for (FoodOrder order : heater) {
                Map<String, String> orderInfo = new HashMap<>();
                orderInfo.put("id", order.getId());
                orderInfo.put("name", order.getName());
                orderInfo.put("temperature", order.getTemperature().getValue());
                heaterOrders.add(orderInfo);
            }
            heaterStatus.put("orders", heaterOrders);
            status.put("heater", heaterStatus);
            
            // Shelf status
            Map<String, Object> shelfStatus = new HashMap<>();
            shelfStatus.put("count", shelf.size());
            shelfStatus.put("capacity", 12);
            List<Map<String, String>> shelfOrders = new ArrayList<>();
            for (FoodOrder order : shelf) {
                Map<String, String> orderInfo = new HashMap<>();
                orderInfo.put("id", order.getId());
                orderInfo.put("name", order.getName());
                orderInfo.put("temperature", order.getTemperature().getValue());
                shelfOrders.add(orderInfo);
            }
            shelfStatus.put("orders", shelfOrders);
            status.put("shelf", shelfStatus);
            
            return status;
        } finally {
            lock.readLock().unlock();
        }
    }
    
    /**
     * Get the complete actions ledger.
     */
    public List<KitchenAction> getActionsLedger() {
        lock.readLock().lock();
        try {
            return new ArrayList<>(actions);
        } finally {
            lock.readLock().unlock();
        }
    }
    
    /**
     * Get system statistics.
     */
    public Map<String, Integer> getStatistics() {
        lock.readLock().lock();
        try {
            return new HashMap<>(stats);
        } finally {
            lock.readLock().unlock();
        }
    }
    
    /**
     * Remove expired orders from storage.
     */
    public void cleanupExpiredOrders() {
        long currentTime = System.currentTimeMillis();
        
        lock.writeLock().lock();
        try {
            // Check cooler
            List<FoodOrder> expiredCooler = new ArrayList<>();
            for (FoodOrder order : cooler) {
                if (!order.isFresh(currentTime)) {
                    expiredCooler.add(order);
                }
            }
            for (FoodOrder order : expiredCooler) {
                cooler.remove(order);
                logAction(currentTime, order.getId(), ActionType.DISCARD, 
                         "cooler", "Auto-discarded expired " + order.getName());
                stats.put("orders_discarded", stats.get("orders_discarded") + 1);
                if (orders.containsKey(order.getId())) {
                    orders.remove(order.getId());
                }
            }
            
            // Check heater
            List<FoodOrder> expiredHeater = new ArrayList<>();
            for (FoodOrder order : heater) {
                if (!order.isFresh(currentTime)) {
                    expiredHeater.add(order);
                }
            }
            for (FoodOrder order : expiredHeater) {
                heater.remove(order);
                logAction(currentTime, order.getId(), ActionType.DISCARD, 
                         "heater", "Auto-discarded expired " + order.getName());
                stats.put("orders_discarded", stats.get("orders_discarded") + 1);
                if (orders.containsKey(order.getId())) {
                    orders.remove(order.getId());
                }
            }
            
            // Check shelf
            List<FoodOrder> expiredShelf = new ArrayList<>();
            for (FoodOrder order : shelf) {
                if (!order.isFresh(currentTime)) {
                    expiredShelf.add(order);
                }
            }
            for (FoodOrder order : expiredShelf) {
                shelf.remove(order);
                logAction(currentTime, order.getId(), ActionType.DISCARD, 
                         "shelf", "Auto-discarded expired " + order.getName());
                stats.put("orders_discarded", stats.get("orders_discarded") + 1);
                if (orders.containsKey(order.getId())) {
                    orders.remove(order.getId());
                }
            }
        } finally {
            lock.writeLock().unlock();
        }
    }
}