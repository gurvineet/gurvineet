package com.kitchen.model;

import java.time.Instant;

/**
 * Represents a food order with all required attributes.
 */
public class FoodOrder {
    private final String id;
    private final String name;
    private final Temperature temperature;
    private final int freshness; // Duration in seconds
    private final long placedAt; // Timestamp when placed
    private long storedAt; // Timestamp when stored
    private String storageLocation; // "cooler", "heater", or "shelf"
    
    public FoodOrder(String id, String name, Temperature temperature, int freshness, 
                    long placedAt, long storedAt, String storageLocation) {
        this.id = id;
        this.name = name;
        this.temperature = temperature;
        this.freshness = freshness;
        this.placedAt = placedAt;
        this.storedAt = storedAt;
        this.storageLocation = storageLocation;
    }
    
    /**
     * Check if the order is still fresh at current time.
     */
    public boolean isFresh(long currentTime) {
        long elapsedTime = currentTime - storedAt;
        long idealFreshness = freshness;
        
        // If stored at ideal temperature, use normal freshness
        // If stored at non-ideal temperature, degrade twice as quickly
        if (storageLocation.equals(temperature.getValue())) {
            return elapsedTime < idealFreshness;
        } else {
            return elapsedTime < (idealFreshness / 2);
        }
    }
    
    // Getters
    public String getId() { return id; }
    public String getName() { return name; }
    public Temperature getTemperature() { return temperature; }
    public int getFreshness() { return freshness; }
    public long getPlacedAt() { return placedAt; }
    public long getStoredAt() { return storedAt; }
    public String getStorageLocation() { return storageLocation; }
    
    // Setters
    public void setStoredAt(long storedAt) { this.storedAt = storedAt; }
    public void setStorageLocation(String storageLocation) { this.storageLocation = storageLocation; }
    
    @Override
    public String toString() {
        return String.format("FoodOrder{id='%s', name='%s', temperature=%s, freshness=%d, storageLocation='%s'}", 
                           id, name, temperature, freshness, storageLocation);
    }
    
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        FoodOrder that = (FoodOrder) obj;
        return id.equals(that.id);
    }
    
    @Override
    public int hashCode() {
        return id.hashCode();
    }
}