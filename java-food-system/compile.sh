#!/bin/bash

# Simple compilation script for Food Order Fulfillment System (Java)
# This script compiles the Java code without requiring Maven

echo "🍕 Compiling Food Order Fulfillment System (Java)"
echo "=================================================="

# Check Java version
JAVA_VERSION=$(java -version 2>&1 | head -n 1 | awk -F '"' '{print $2}' | cut -d'.' -f1,2)
echo "☕ Java version: $JAVA_VERSION"

# Create output directory
mkdir -p target/classes

# Compile all Java files in dependency order
echo "🔨 Compiling Java files..."

# Step 1: Compile model classes (no dependencies)
echo "  📦 Compiling model classes..."
javac -d target/classes src/main/java/com/kitchen/model/*.java
if [ $? -ne 0 ]; then
    echo "❌ Failed to compile model classes"
    exit 1
fi

# Step 2: Compile service classes (depend on model)
echo "  🔧 Compiling service classes..."
javac -cp target/classes -d target/classes src/main/java/com/kitchen/service/*.java
if [ $? -ne 0 ]; then
    echo "❌ Failed to compile service classes"
    exit 1
fi

# Step 3: Compile harness classes (depend on model and service)
echo "  🎯 Compiling harness classes..."
javac -cp target/classes -d target/classes src/main/java/com/kitchen/harness/*.java
if [ $? -ne 0 ]; then
    echo "❌ Failed to compile harness classes"
    exit 1
fi

# Step 4: Compile main classes (depend on all above)
echo "  🚀 Compiling main classes..."
javac -cp target/classes -d target/classes src/main/java/com/kitchen/*.java
if [ $? -ne 0 ]; then
    echo "❌ Failed to compile main classes"
    exit 1
fi

echo "✅ Compilation successful"
    
# Create a simple run script
cat > run.sh << 'EOF'
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
EOF

chmod +x run.sh

# Create a demo run script
cat > run-demo.sh << 'EOF'
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
EOF

chmod +x run-demo.sh

echo ""
echo "🎉 Compilation completed successfully!"
echo ""
echo "🚀 To run the system:"
echo "  ./run.sh"
echo ""
echo "🎭 To run the demo:"
echo "  ./run-demo.sh"
echo ""
echo "📁 Compiled classes are in: target/classes/"