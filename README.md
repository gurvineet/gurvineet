# Food Order Fulfillment System

A real-time system for managing food orders in a delivery-only kitchen with concurrent order placement and pickup operations.

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
- **Thread-safe operations** ensuring system stability under concurrent load
- **Configurable execution parameters** for testing different scenarios

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

- Python 3.7+ (uses dataclasses and type hints)
- No external dependencies required

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd food-order-fulfillment
   ```

2. **Run tests to verify functionality**
   ```bash
   python src/test_kitchen.py
   ```

3. **Run the execution harness**
   ```bash
   # Default settings (2 orders/sec, 4-8 second pickup window)
   python src/execution_harness.py
   
   # Custom settings
   python src/execution_harness.py --rate 3.0 --pickup-min 2 --pickup-max 6
   ```

### Docker Deployment

1. **Build the container**
   ```bash
   docker build -t food-order-system .
   ```

2. **Run the system**
   ```bash
   # Default settings
   docker run food-order-system python src/execution_harness.py
   
   # Custom settings
   docker run food-order-system python src/execution_harness.py --rate 1.5 --pickup-min 3 --pickup-max 10
   ```

## Command Line Options

The execution harness supports the following parameters:

- `--rate`: Order placement rate in orders per second (default: 2.0)
- `--pickup-min`: Minimum pickup delay in seconds (default: 4)
- `--pickup-max`: Maximum pickup delay in seconds (default: 8)

## System Architecture

### Core Components

- **KitchenSystem**: Main system managing storage, orders, and operations
- **FoodOrder**: Data structure representing individual food orders
- **ExecutionHarness**: Test harness exercising the system with configurable parameters
- **MockChallengeServer**: Simulated server for testing (replaceable with real implementation)

### Concurrency Model

The system uses Python's threading module to handle concurrent operations:
- **Thread-safe operations** with RLock for read/write operations
- **Concurrent order placement** and pickup without blocking
- **Background cleanup** of expired orders
- **Synchronized action logging** ensuring complete audit trail

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
python src/test_kitchen.py
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
- **Concurrent operations**: Thread-safe with minimal contention

## Design Decisions and Justifications

### 1. Thread Safety with RLock
**Decision**: Used RLock instead of Lock for better performance with multiple readers
**Justification**: Most operations are reads (status checks, action logging), with occasional writes (order placement/pickup). RLock allows concurrent reads while maintaining write exclusivity.

### 2. Freshness Degradation Algorithm
**Decision**: Non-ideal temperature orders degrade at 2x rate
**Justification**: This accurately models real-world food spoilage where temperature abuse significantly accelerates degradation.

### 3. Discard Strategy Scoring
**Decision**: Multi-factor scoring system prioritizing expired orders, then temperature mismatches, then time-based factors
**Justification**: This maximizes food quality preservation while ensuring system throughput. The scoring system is easily tunable for different business requirements.

### 4. Storage Hierarchy
**Decision**: Three-tier storage system with automatic optimization
**Justification**: Balances food quality (ideal temperature storage) with system efficiency (shelf overflow). The automatic movement logic ensures optimal resource utilization.

### 5. Real-time Console Output
**Decision**: Human-readable action logging to console
**Justification**: Enables real-time monitoring and debugging, essential for production kitchen operations.

## Future Enhancements

- **Persistent storage** for order history and analytics
- **API endpoints** for external system integration
- **Advanced analytics** for kitchen efficiency optimization
- **Machine learning** for predictive order management
- **Multi-kitchen support** for distributed operations

## License

This project is proprietary and confidential.