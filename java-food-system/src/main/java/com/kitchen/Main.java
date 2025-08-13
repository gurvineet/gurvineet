package com.kitchen;

import com.kitchen.harness.ExecutionHarness;
import java.util.Scanner;

/**
 * Main entry point for the Food Order Fulfillment System.
 */
public class Main {
    
    public static void main(String[] args) {
        // Parse command line arguments
        double rate = 2.0; // Default: 2 orders per second
        int pickupMin = 4; // Default: 4 seconds minimum pickup delay
        int pickupMax = 8; // Default: 8 seconds maximum pickup delay
        
        // Simple argument parsing
        for (int i = 0; i < args.length; i++) {
            switch (args[i]) {
                case "--rate":
                    if (i + 1 < args.length) {
                        try {
                            rate = Double.parseDouble(args[++i]);
                        } catch (NumberFormatException e) {
                            System.err.println("Error: Invalid rate value: " + args[i]);
                            System.exit(1);
                        }
                    }
                    break;
                case "--pickup-min":
                    if (i + 1 < args.length) {
                        try {
                            pickupMin = Integer.parseInt(args[++i]);
                        } catch (NumberFormatException e) {
                            System.err.println("Error: Invalid pickup-min value: " + args[i]);
                            System.exit(1);
                        }
                    }
                    break;
                case "--pickup-max":
                    if (i + 1 < args.length) {
                        try {
                            pickupMax = Integer.parseInt(args[++i]);
                        } catch (NumberFormatException e) {
                            System.err.println("Error: Invalid pickup-max value: " + args[i]);
                            System.exit(1);
                        }
                    }
                    break;
                case "--help":
                    printUsage();
                    System.exit(0);
                    break;
                default:
                    System.err.println("Error: Unknown argument: " + args[i]);
                    printUsage();
                    System.exit(1);
            }
        }
        
        // Validate arguments
        if (rate <= 0) {
            System.err.println("Error: Rate must be positive");
            System.exit(1);
        }
        
        if (pickupMin < 0 || pickupMax < pickupMin) {
            System.err.println("Error: Invalid pickup time range");
            System.exit(1);
        }
        
        try {
            // Create and run harness
            ExecutionHarness harness = new ExecutionHarness(rate, pickupMin, pickupMax);
            
            // Add shutdown hook for graceful termination
            Runtime.getRuntime().addShutdownHook(new Thread(() -> {
                System.out.println("\nShutdown signal received, stopping harness...");
                harness.stop();
            }));
            
            harness.start();
            
        } catch (Exception e) {
            System.err.println("Error during execution: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
    
    private static void printUsage() {
        System.out.println("Food Order Fulfillment System");
        System.out.println();
        System.out.println("Usage: java -cp <classpath> com.kitchen.Main [options]");
        System.out.println();
        System.out.println("Options:");
        System.out.println("  --rate <value>        Order placement rate in orders per second (default: 2.0)");
        System.out.println("  --pickup-min <value>  Minimum pickup delay in seconds (default: 4)");
        System.out.println("  --pickup-max <value>  Maximum pickup delay in seconds (default: 8)");
        System.out.println("  --help                Show this help message");
        System.out.println();
        System.out.println("Examples:");
        System.out.println("  java -cp . com.kitchen.Main");
        System.out.println("  java -cp . com.kitchen.Main --rate 3.0 --pickup-min 2 --pickup-max 6");
    }
}