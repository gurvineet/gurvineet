package com.kitchen.model;

import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;

/**
 * Represents a kitchen action for the ledger.
 */
public class KitchenAction {
    private final long timestamp;
    private final String orderId;
    private final ActionType actionType;
    private final String target; // Storage location or action description
    private final String details;
    
    public KitchenAction(long timestamp, String orderId, ActionType actionType, String target, String details) {
        this.timestamp = timestamp;
        this.orderId = orderId;
        this.actionType = actionType;
        this.target = target;
        this.details = details;
    }
    
    public KitchenAction(long timestamp, String orderId, ActionType actionType, String target) {
        this(timestamp, orderId, actionType, target, "");
    }
    
    // Getters
    public long getTimestamp() { return timestamp; }
    public String getOrderId() { return orderId; }
    public ActionType getActionType() { return actionType; }
    public String getTarget() { return target; }
    public String getDetails() { return details; }
    
    /**
     * Get formatted timestamp string for display.
     */
    public String getFormattedTimestamp() {
        LocalDateTime dateTime = LocalDateTime.ofInstant(Instant.ofEpochMilli(timestamp), ZoneId.systemDefault());
        return dateTime.format(DateTimeFormatter.ofPattern("HH:mm:ss.SSS"));
    }
    
    @Override
    public String toString() {
        return String.format("KitchenAction{timestamp=%d, orderId='%s', actionType=%s, target='%s', details='%s'}", 
                           timestamp, orderId, actionType, target, details);
    }
}