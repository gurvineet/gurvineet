FROM openjdk:11-jre-slim

# Set working directory
WORKDIR /app

# Copy the JAR file
COPY target/food-order-fulfillment-1.0.0-jar-with-dependencies.jar app.jar

# Expose any ports if needed (none for this application)
# EXPOSE 8080

# Set the entry point
ENTRYPOINT ["java", "-jar", "app.jar"]

# Default command
CMD ["--help"]