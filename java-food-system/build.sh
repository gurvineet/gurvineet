#!/bin/bash

# Build script for Food Order Fulfillment System (Java)

echo "🍕 Building Food Order Fulfillment System (Java)"
echo "================================================"

# Check if Maven is installed
if ! command -v mvn &> /dev/null; then
    echo "❌ Maven is not installed. Please install Maven 3.6+ first."
    exit 1
fi

# Check Maven version
MAVEN_VERSION=$(mvn -version | head -n 1 | awk '{print $3}' | cut -d'.' -f1,2)
echo "📦 Maven version: $MAVEN_VERSION"

# Check Java version
JAVA_VERSION=$(java -version 2>&1 | head -n 1 | awk -F '"' '{print $2}' | cut -d'.' -f1,2)
echo "☕ Java version: $JAVA_VERSION"

# Clean previous builds
echo "🧹 Cleaning previous builds..."
mvn clean

# Compile the project
echo "🔨 Compiling project..."
if mvn compile; then
    echo "✅ Compilation successful"
else
    echo "❌ Compilation failed"
    exit 1
fi

# Run tests
echo "🧪 Running tests..."
if mvn test; then
    echo "✅ Tests passed"
else
    echo "❌ Tests failed"
    exit 1
fi

# Package the project
echo "📦 Packaging project..."
if mvn package; then
    echo "✅ Packaging successful"
else
    echo "❌ Packaging failed"
    exit 1
fi

# Create executable JAR
echo "🎯 Creating executable JAR..."
if mvn assembly:single; then
    echo "✅ Executable JAR created"
else
    echo "❌ Failed to create executable JAR"
    exit 1
fi

echo ""
echo "🎉 Build completed successfully!"
echo ""
echo "📁 Generated files:"
echo "  - target/food-order-fulfillment-1.0.0.jar"
echo "  - target/food-order-fulfillment-1.0.0-jar-with-dependencies.jar"
echo ""
echo "🚀 To run the system:"
echo "  java -jar target/food-order-fulfillment-1.0.0-jar-with-dependencies.jar"
echo ""
echo "🧪 To run tests:"
echo "  mvn test"
echo ""
echo "🎭 To run demo:"
echo "  mvn exec:java -Dexec.mainClass=\"com.kitchen.Demo\""