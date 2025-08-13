# Food Order Fulfillment System (Java)

A real-time system for managing food orders in a delivery-only kitchen with concurrent order placement and pickup operations, implemented in Java.

## System Overview

This system manages food orders through three storage areas:
- **Cooler**: Holds up to 6 cold orders at cold temperature
- **Heater**: Holds up to 6 hot orders at hot temperature  
- **Shelf**: Holds up to 12 orders at room temperature

Orders are automatically placed at their ideal temperature when possible. When ideal storage is full, the system intelligently manages storage by:
1. Moving existing orders from shelf to appropriate temperature-controlled storage
2. Placing new orders on the shelf
3. Discarding orders when necessary to make room

## Features

- **Real-time order management** with concurrent placement and pickup
- **Intelligent storage optimization** prioritizing ideal temperature storage
- **Automatic freshness tracking** with accelerated degradation for non-ideal temperatures
- **Comprehensive action logging** capturing all kitchen operations
- **Thread-safe operations** using ReadWriteLock for optimal concurrent performance
- **Configurable execution parameters** for testing different scenarios
- **Modern Java features** including Java 11+ language features and concurrent utilities

## Order Discard Strategy

When the shelf is full and a new order needs to be placed, the system uses a sophisticated scoring algorithm to choose which order to discard:

1. **Expired orders** receive the highest priority (score +1000) - these are automatically discarded first
2. **Temperature mismatches** receive medium priority (score +500) - orders stored at non-ideal temperatures degrade twice as quickly
3. **Time-based scoring** - orders closer to expiration receive higher scores, with non-ideal temperature orders scoring higher due to accelerated degradation

This strategy ensures that:
- Fresh food is preserved as long as possible
- Orders stored at ideal temperatures are prioritized over those at non-ideal temperatures
- The system maximizes overall food quality and minimizes waste

## Building and Running

### Prerequisites

- Java 11 or higher
- Maven 3.6 or higher
- Docker (optional, for containerized deployment)

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd java-food-system
   ```

2. **Build the project**
   ```bash
   mvn clean compile
   ```

3. **Run tests to verify functionality**
   ```bash
   mvn test
   ```

4. **Run the demo**
   ```bash
   mvn exec:java -Dexec.mainClass="com.kitchen.Demo"
   ```

5. **Run the execution harness**
   ```bash
   # Default settings (2 orders/sec, 4-8 second pickup window)
   mvn exec:java -Dexec.mainClass="com.kitchen.Main"
   
   # Custom settings
   mvn exec:java -Dexec.mainClass="com.kitchen.Main" -Dexec.args="--rate 3.0 --pickup-min 2 --pickup-max 6"
   ```

### Maven Commands

- **Compile**: `mvn compile`
- **Test**: `mvn test`
- **Package**: `mvn package`
- **Run**: `mvn exec:java -Dexec.mainClass="com.kitchen.Main"`
- **Clean**: `mvn clean`

### Docker Deployment

1. **Build the project first**
   ```bash
   mvn clean package
   ```

2. **Build the container**
   ```bash
   docker build -t java-food-order-system .
   ```

3. **Run the system**
   ```bash
   # Default settings
   docker run java-food-order-system
   
   # Custom settings
   docker run java-food-order-system --rate 1.5 --pickup-min 3 --pickup-max 10
   ```

4. **Using docker-compose**
   ```bash
   docker-compose up
   ```

## Command Line Options

The execution harness supports the following parameters:

- `--rate`: Order placement rate in orders per second (default: 2.0)
- `--pickup-min`: Minimum pickup delay in seconds (default: 4)
- `--pickup-max`: Maximum pickup delay in seconds (default: 8)
- `--help`: Show help message

## System Architecture

### Core Components

- **KitchenSystem**: Main system managing storage, orders, and operations
- **FoodOrder**: Data structure representing individual food orders
- **ExecutionHarness**: Test harness exercising the system with configurable parameters
- **MockChallengeServer**: Simulated server for testing (replaceable with real implementation)

### Concurrency Model

The system uses Java's concurrent utilities for optimal performance:
- **ReadWriteLock**: Allows concurrent reads while maintaining write exclusivity
- **ExecutorService**: Manages thread pools for order pickup operations
- **ScheduledExecutorService**: Handles periodic cleanup of expired orders
- **ConcurrentHashMap**: Thread-safe order tracking
- **Volatile flags**: Control system state across threads

### Storage Management

Storage follows a hierarchical approach:
1. **Primary storage**: Place orders at ideal temperature when possible
2. **Secondary storage**: Move existing orders to make room for new ones
3. **Tertiary storage**: Place on shelf when temperature storage is full
4. **Emergency storage**: Discard orders when all storage is exhausted

## Testing

The system includes comprehensive tests covering:
- Basic order placement and pickup
- Storage capacity limits
- Temperature mismatch handling
- Freshness degradation
- Concurrent operations
- Action ledger functionality

Run tests with:
```bash
mvn test
```

## Action Ledger

The system maintains a complete audit trail of all kitchen operations:

- **PLACE**: New order stored (with placement details)
- **MOVE**: Order moved between storage locations
- **PICKUP**: Order picked up for delivery
- **DISCARD**: Order discarded (expired or to make room)

Each action includes:
- Timestamp
- Order ID
- Action type
- Target location
- Additional details

## Performance Characteristics

- **Order placement**: O(1) average case, O(n) worst case when moving orders
- **Order pickup**: O(1) average case
- **Storage optimization**: O(n) where n is the number of orders in shelf storage
- **Memory usage**: Linear with number of active orders
- **Concurrent operations**: Thread-safe with minimal contention using ReadWriteLock

## Design Decisions and Justifications

### 1. Thread Safety with ReadWriteLock
**Decision**: Used ReadWriteLock instead of synchronized blocks for better performance
**Justification**: Most operations are reads (status checks, action logging), with occasional writes (order placement/pickup). ReadWriteLock allows concurrent reads while maintaining write exclusivity, providing better scalability.

### 2. ExecutorService for Concurrency
**Decision**: Used ExecutorService and ScheduledExecutorService for managing concurrent operations
**Justification**: Java's concurrent utilities provide better performance, monitoring, and lifecycle management than manual thread creation. They also handle thread pool sizing and shutdown gracefully.

### 3. Freshness Degradation Algorithm
**Decision**: Non-ideal temperature orders degrade at 2x rate
**Justification**: This accurately models real-world food spoilage where temperature abuse significantly accelerates degradation.

### 4. Discard Strategy Scoring
**Decision**: Multi-factor scoring system prioritizing expired orders, then temperature mismatches, then time-based factors
**Justification**: This maximizes food quality preservation while ensuring system throughput. The scoring system is easily tunable for different business requirements.

### 5. Real-time Console Output
**Decision**: Human-readable action logging to console
**Justification**: Enables real-time monitoring and debugging, essential for production kitchen operations.

## Java-Specific Features

- **Java 11+ language features**: var keyword, enhanced switch statements, text blocks
- **Modern collections**: Stream API for functional operations
- **Concurrent utilities**: ReadWriteLock, ExecutorService, ConcurrentHashMap
- **Exception handling**: Comprehensive error handling with proper resource cleanup
- **Maven build system**: Standard Java project structure with dependency management

## Future Enhancements

- **Spring Boot integration** for web-based monitoring and REST APIs
- **Database persistence** for order history and analytics
- **Message queues** for distributed kitchen operations
- **Metrics and monitoring** with Micrometer and Prometheus
- **Kubernetes deployment** for cloud-native operations
- **Machine learning** for predictive order management

## Troubleshooting

### Common Issues

1. **OutOfMemoryError**: Increase JVM heap size with `-Xmx` flag
2. **Thread starvation**: Monitor thread pool sizes and adjust if needed
3. **Performance issues**: Check for lock contention in high-concurrency scenarios

### Debug Mode

Enable debug logging by setting the log level:
```bash
mvn exec:java -Dexec.mainClass="com.kitchen.Main" -Djava.util.logging.config.file=logging.properties
```

## License

This project is proprietary and confidential.