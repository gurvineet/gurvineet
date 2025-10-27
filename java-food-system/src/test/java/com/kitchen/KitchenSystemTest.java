package com.kitchen;

import com.kitchen.model.*;
import com.kitchen.service.KitchenSystem;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

import java.util.List;
import java.util.Map;

/**
 * Test class for KitchenSystem.
 */
public class KitchenSystemTest {
    
    private KitchenSystem kitchen;
    
    @BeforeEach
    void setUp() {
        kitchen = new KitchenSystem();
    }
    
    @Test
    void testBasicFunctionality() {
        // Test 1: Place a simple order
        boolean success = kitchen.placeOrder("test_001", "Hot Pizza", Temperature.HOT, 300);
        assertTrue(success, "Failed to place simple order");
        
        // Test 2: Check storage status
        Map<String, Map<String, Object>> status = kitchen.getStorageStatus();
        assertEquals(1, status.get("heater").get("count"), "Order not stored in heater");
        
        // Test 3: Pickup order
        FoodOrder order = kitchen.pickupOrder("test_001");
        assertNotNull(order, "Failed to pickup order");
        assertEquals("Hot Pizza", order.getName(), "Wrong order picked up");
        
        // Test 4: Check storage is empty
        status = kitchen.getStorageStatus();
        assertEquals(0, status.get("heater").get("count"), "Heater not empty after pickup");
    }
    
    @Test
    void testStorageCapacity() {
        // Fill cooler to capacity
        for (int i = 0; i < 6; i++) {
            boolean success = kitchen.placeOrder("cold_" + i, "Cold Item " + i, Temperature.COLD, 600);
            assertTrue(success, "Failed to place cold order " + i);
        }
        
        // Try to place one more cold order
        boolean success = kitchen.placeOrder("cold_extra", "Extra Cold Item", Temperature.COLD, 600);
        assertFalse(success, "Should not be able to place order when cooler is full");
        
        // Fill heater to capacity
        for (int i = 0; i < 6; i++) {
            success = kitchen.placeOrder("hot_" + i, "Hot Item " + i, Temperature.HOT, 600);
            assertTrue(success, "Failed to place hot order " + i);
        }
        
        // Try to place one more hot order
        success = kitchen.placeOrder("hot_extra", "Extra Hot Item", Temperature.HOT, 600);
        assertFalse(success, "Should not be able to place order when heater is full");
    }
    
    @Test
    void testTemperatureMismatch() {
        // Fill cooler and heater
        for (int i = 0; i < 6; i++) {
            kitchen.placeOrder("cold_" + i, "Cold Item " + i, Temperature.COLD, 600);
            kitchen.placeOrder("hot_" + i, "Hot Item " + i, Temperature.HOT, 600);
        }
        
        // Try to place a cold order (should go to shelf)
        boolean success = kitchen.placeOrder("cold_shelf", "Cold on Shelf", Temperature.COLD, 600);
        assertTrue(success, "Failed to place cold order on shelf when cooler full");
        
        // Check it's on shelf
        Map<String, Map<String, Object>> status = kitchen.getStorageStatus();
        assertEquals(1, status.get("shelf").get("count"), "Order not placed on shelf");
    }
    
    @Test
    void testFreshnessDegradation() {
        // Place order at ideal temperature
        kitchen.placeOrder("ideal", "Ideal Temp", Temperature.HOT, 100);
        
        // Place order at non-ideal temperature
        kitchen.placeOrder("non_ideal", "Non-Ideal Temp", Temperature.HOT, 100);
        
        // Wait for some time
        try {
            Thread.sleep(100); // 100ms
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        
        // Check freshness
        FoodOrder idealOrder = kitchen.pickupOrder("ideal");
        FoodOrder nonIdealOrder = kitchen.pickupOrder("non_ideal");
        
        assertNotNull(idealOrder, "Ideal order not found");
        assertNotNull(nonIdealOrder, "Non-ideal order not found");
    }
    
    @Test
    void testActionLedger() {
        // Place and pickup an order
        kitchen.placeOrder("ledger_test", "Test Item", Temperature.HOT, 600);
        kitchen.pickupOrder("ledger_test");
        
        // Check ledger
        List<KitchenAction> actions = kitchen.getActionsLedger();
        assertEquals(2, actions.size(), "Expected 2 actions");
        
        // Check action types
        boolean hasPlace = actions.stream().anyMatch(a -> a.getActionType() == ActionType.PLACE);
        boolean hasPickup = actions.stream().anyMatch(a -> a.getActionType() == ActionType.PICKUP);
        
        assertTrue(hasPlace, "Place action not logged");
        assertTrue(hasPickup, "Pickup action not logged");
    }
    
    @Test
    void testStatistics() {
        // Place and pickup some orders
        kitchen.placeOrder("stat_1", "Item 1", Temperature.HOT, 600);
        kitchen.placeOrder("stat_2", "Item 2", Temperature.COLD, 600);
        kitchen.pickupOrder("stat_1");
        
        Map<String, Integer> stats = kitchen.getStatistics();
        assertEquals(2, stats.get("orders_placed"), "Wrong orders placed count");
        assertEquals(1, stats.get("orders_picked_up"), "Wrong orders picked up count");
    }
}