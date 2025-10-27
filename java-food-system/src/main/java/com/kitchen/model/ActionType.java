package com.kitchen.model;

/**
 * Types of kitchen actions.
 */
public enum ActionType {
    PLACE("place"),
    MOVE("move"),
    PICKUP("pickup"),
    DISCARD("discard");
    
    private final String value;
    
    ActionType(String value) {
        this.value = value;
    }
    
    public String getValue() {
        return value;
    }
    
    public static ActionType fromString(String value) {
        for (ActionType action : ActionType.values()) {
            if (action.value.equalsIgnoreCase(value)) {
                return action;
            }
        }
        throw new IllegalArgumentException("Unknown action type: " + value);
    }
}