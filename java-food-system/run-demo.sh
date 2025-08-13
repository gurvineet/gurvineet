#!/bin/bash
# Simple demo run script for the Food Order Fulfillment System

echo "🎭 Running Food Order Fulfillment System Demo"
echo "============================================="

# Check if class files exist
if [ ! -d "target/classes" ]; then
    echo "❌ Compiled classes not found. Run compile.sh first."
    exit 1
fi

# Run the demo class
java -cp target/classes com.kitchen.Demo
