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

## Running Tests

```
python -m tests.test_monitor_client
python -m tests.test_action_client
python -m tests.test_bank_services
python -m tests.test_at_most_once
python -m tests.test_transfer
```

## Server

1. Drop-Reply-Rate: Server sent reply so monitor client will see it, but client who make request wont
2. Drop-Request-Rate: Server never received the request, so the monitor client will not receive anything
3. Timeout: Specify the number of seconds for the server to sleep to force the client to timeout and retransmit a request
4. Semantics: Which semantics to use. Either at most once or at least once
