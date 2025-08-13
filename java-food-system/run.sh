#!/bin/bash
# Simple run script for the Food Order Fulfillment System

echo "🚀 Running Food Order Fulfillment System"
echo "========================================"

# Check if class files exist
if [ ! -d "target/classes" ]; then
    echo "❌ Compiled classes not found. Run compile.sh first."
    exit 1
fi

# Run the main class
java -cp target/classes com.kitchen.Main "$@"
