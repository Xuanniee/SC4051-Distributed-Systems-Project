# Distributed Banking System

This project implements a distributed banking application using a client-server architecture over UDP. The system supports basic banking operations such as opening and closing accounts, depositing and withdrawing money, monitoring account updates, and additional operations such as balance inquiry and transfer. It also demonstrates invocation semantics through both at-least-once and at-most-once execution modes.

## Project Objectives

The main objectives of this project are:

- implement client-server communication using UDP sockets
- design and use a custom binary protocol for request and reply messages
- manually implement marshalling and unmarshalling of messages
- support multiple banking operations
- implement monitoring callbacks for account updates
- compare at-least-once and at-most-once invocation semantics
- simulate unreliable communication by dropping requests or replies

## Project Set-Up

### Frontend

# Bank Client (JavaScript)

This project implements the frontend client for a distributed banking system using Node.js and UDP sockets.

Please note that an `.env` file is required. The following keys are required but the values should be adjusted according to your archectural needs.

```
SERVER_HOST=0.0.0.0
SERVER_PORT=2222
```

---

## Running the frontend server

### Running the server with default configuration

```bash
node index.js
```

### Running the server with options

```bash
node index.js --timeout 3000 --retries 2 --monitor-duration 300
```

|     | options            | default       |
| --- | ------------------ | ------------- |
| 1.  | --timeout          | 5000 (ms)     |
| 2.  | --retries          | 2             |
| 3.  | --monitor-duration | 300 (seconds) |

---

### Backend

Run the backend server from the `server/` directory:

```bash
python server.py
```

Full command:

```bash
python server.py --semantics <at-most-once|at-least-once> --drop-request-rate <float> --drop-reply-rate <float> --timeout <float>
```

Parameters:

- `--semantics`: selects the invocation semantics mode used by the server. Allowed values are `at-most-once` and `at-least-once`. Default: `at-most-once`.
- `--drop-request-rate`: simulates request loss by randomly dropping incoming requests before processing. Type: `float`. Default: `0.0`.
- `--drop-reply-rate`: simulates reply loss by randomly dropping outgoing server replies after processing. Type: `float`. Default: `0.0`.
- `--timeout`: adds an artificial delay before the server sends a reply. Type: `float` in seconds. Default: `0.0`.

Default run:

```bash
python server.py --semantics at-most-once --drop-request-rate 0.0 --drop-reply-rate 0.0 --timeout 0.0
```

Example runs:

```bash
python server.py --semantics at-most-once
python server.py --semantics at-least-once
python server.py --drop-request-rate 0.2
python server.py --drop-reply-rate 0.3
python server.py --timeout 1.0
python server.py --semantics at-most-once --drop-request-rate 0.2 --drop-reply-rate 0.3 --timeout 1.0
```

## Features

### Core Banking Operations

- Open account
- Close account
- Deposit money
- Withdraw money

### Additional Operations

- Balance inquiry (idempotent)
- Transfer money (non-idempotent)

### Monitoring Support

- Clients can register for monitoring for a specified duration
- The server pushes callback updates whenever relevant account events occur

### Invocation Semantics

- At-least-once
- At-most-once

### Reliability Experiments

- Simulated request loss
- Simulated reply loss
- Configurable timeout and retry behaviour

## Project Structure

```text
server/
├── config/
│   └── config.py
├── handlers/
│   ├── banking_handlers.py
│   └── dispatcher.py
├── models/
│   ├── accounts.py
│   ├── enums.py
│   └── messages.py
├── protocols/
│   ├── codecs.py
│   ├── invocation_codecs.py
│   ├── marshaller.py
│   └── request_parser.py
├── services/
│   ├── bank_services.py
│   ├── invocation_service.py
│   └── monitor_service.py
├── storage/
│   └── account_store.py
├── tests/
│   ├── test_action_client.py
│   ├── test_monitor_client.py
│   └── ...
└── server.py
```

```text
client/
├── index.js
├── README.md
│
├── helpers/
│   ├── index.js
│   ├── constants.js
│   ├── buildPacket.js
│   ├── createRequestIdGenerator.js
│   ├── generateClientId.js
│   ├── getArgs.js
│   └── sendWithRetries.js
│
├── protocols/
│   ├── marshaller.js
│   ├── codecs.js
│   ├── invocationCodecs.js
│   └── monitorCallback.js
│
└── services/
    ├── index.js
    ├── openAccount.js
    ├── closeAccount.js
    ├── deposit.js
    ├── withdraw.js
    ├── monitor.js
    ├── balanceInquiry.js
    └── transfer.js
```
