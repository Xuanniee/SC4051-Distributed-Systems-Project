# Bank Backend Server (Python)

This project implements the backend server for a distributed banking system using UDP sockets.

The backend is organized into separate modules so that protocol handling, transport, storage, banking logic, monitoring, and reliability features are clearly separated.

---

## Project Structure

```text
bank_backend/
├── server.py
├── requirements.txt
├── README.md
├── app/
│   ├── config.py
│   ├── models/
│   │   ├── account.py
│   │   ├── enums.py
│   │   └── messages.py
│   │
│   ├── protocol/
│   │   ├── marshaller.py
│   │   ├── packet.py
│   │   ├── codecs.py
│   │   └── request_parser.py
│   │
│   ├── services/
│   │   ├── bank_service.py
│   │   ├── monitor_service.py
│   │   └── callback_service.py
│   │
│   ├── storage/
│   │   ├── account_store.py
│   │   ├── monitor_store.py
│   │   └── history_store.py
│   │
│   ├── reliability/
│   │   ├── semantics.py
│   │   ├── retry.py
│   │   ├── dedup.py
│   │   └── loss_simulator.py
│   │
│   ├── udp-transport-wrapper/
│   │   ├── udp_server.py
│   │   └── udp_socket_wrapper.py
│   │
│   ├── handlers/
│   │   ├── dispatcher.py
│   │   └── banking_handlers.py
│   │
│   └── utils/
```

## Brief Module Descriptions

### `server.py`

Main startup file for the backend server.  
It should initialize the configuration, create all required objects, connect the modules together, and start the UDP server loop.

---

## `app/config.py`

Stores global configuration values.  
This includes things like host, port, timeout, retry count, packet loss rate, and which invocation semantics mode to use.

---

## `app/models/`

Contains the core data definitions used by the system.

### `account.py`

Defines the bank account structure.  
It should store fields like account number, account holder name, password, currency, and balance.

### `enums.py`

Defines enums used across the project.  
Examples include currency type, operation code, message type, status code, and invocation semantics.

### `messages.py`

Defines request and response objects.  
These represent the logical data for operations like open account, close account, deposit, withdraw, monitor registration, and callback updates.

---

## `app/protocol/`

Handles the message format and byte-level encoding/decoding.

### `marshaller.py`

Implements low-level conversion between Python values and raw bytes.  
This includes integers, floats, enums, booleans, and variable-length strings.

### `packet.py`

Defines the overall UDP packet structure.  
It should handle packet headers, packet creation, and packet decoding.

### `codecs.py`

Encodes and decodes the higher-level message objects.  
It acts as the bridge between request/response classes and raw byte payloads.

### `request_parser.py`

Chooses the correct request type based on the opcode.  
It should decode incoming payload bytes into the correct request object.

---

## `app/services/`

Contains the actual banking logic.

### `bank_service.py`

Implements the main account operations.  
This includes opening accounts, closing accounts, deposits, withdrawals, and the extra idempotent/non-idempotent operations.

### `monitor_service.py`

Manages monitoring registrations.  
It should store which clients are monitoring updates, track monitor intervals, and remove expired monitor subscriptions.

### `callback_service.py`

Sends callback updates to monitoring clients.  
Whenever an account is opened, closed, deposited into, or withdrawn from, this module should notify active monitoring clients.

---

## `app/storage/`

Handles in-memory data storage.

### `account_store.py`

Stores account records.  
It should support creating, retrieving, updating, and deleting accounts.

### `monitor_store.py`

Stores monitoring client registrations.  
It should track client IP, port, and expiry time for each monitor registration.

### `history_store.py`

Stores request/reply history for reliability.  
It is mainly used for duplicate detection and cached replies in at-most-once semantics.

---

## `app/reliability/`

Handles reliability features required for UDP communication.

### `__init__.py`

Marks the folder as a Python package.

### `semantics.py`

Implements invocation semantics behavior.  
It should contain the logic for at-least-once and at-most-once handling.

### `retry.py`

Handles retry-related settings or helper logic.  
This may include timeout values, retry counts, and resend policy.

### `dedup.py`

Handles duplicate request detection.  
It should check whether a request ID has already been processed and decide whether to re-execute or replay a cached reply.

### `loss_simulator.py`

Simulates dropped request or reply packets.  
This is used for testing and experiments comparing at-least-once and at-most-once behavior.

---

## `app/udp-transport-wrapper/`

Handles raw UDP communication.

### `udp_server.py`

Implements the main UDP receive/send loop.  
It should receive packets, pass them to the handler layer, and send replies back to clients.

### `udp_socket_wrapper.py`

Wraps Python’s UDP socket operations.  
It should provide helper methods for sending, receiving, timeouts, and optional packet loss simulation.

---

## `app/handlers/`

Connects incoming requests to the correct business logic.

### `dispatcher.py`

Routes incoming operations to the correct handler function.  
It should map opcodes to the corresponding banking handler.

### `banking_handlers.py`

Implements one handler per operation.  
Each handler should decode the request, call the correct service method, and encode the response.

---

## `app/utils/`

Contains shared helper functions used across the project.  
Examples include logging helpers, ID generation, and time-related utilities.
