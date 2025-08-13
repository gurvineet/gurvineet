package com.kitchen.model;

/**
 * Food storage temperature requirements.
 */
public enum Temperature {
    HOT("hot"),
    COLD("cold"),
    ROOM("room");
    
    private final String value;
    
    Temperature(String value) {
        this.value = value;
    }
    
    public String getValue() {
        return value;
    }
    
    public static Temperature fromString(String value) {
        for (Temperature temp : Temperature.values()) {
            if (temp.value.equalsIgnoreCase(value)) {
                return temp;
            }
        }
        throw new IllegalArgumentException("Unknown temperature: " + value);
    }
}