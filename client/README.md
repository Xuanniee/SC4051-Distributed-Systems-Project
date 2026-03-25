# Bank Client (JavaScript)

This project implements the frontend client for a distributed banking system using Node.js and UDP sockets.

Please note that an ``.env`` file is required. The following keys are required but the values should be adjusted according to your archectural needs.

```
PORT=5000
HOST=localhost

SERVER_HOST=0.0.0.0
SERVER_PORT=2222
```

---

## Project Structure

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

---

## Running the frontend server

### Running the server with default configuration
```bash
node index.js
```

### Running the server with options
```bash
node index.js --timeout 3000 --retries 3 --monitor-duration 300
```

|     | options            | default       |
| --- | ------------------ | ------------- |
| 1.  | --timeout          | 3000 (ms)     |
| 2.  | --retries          | 3             |
| 3.  | --monitor-duration | 300 (seconds) |

---

