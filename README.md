# 🚀 Skynopy Challenge – Satellite Communication Stack

Welcome to the simulation of a satellite communication between a modem simulator and a client, via a cloud infrastructure.  
This project was carried out as part of a technical challenge (Skynopy), aiming to demonstrate a reliable, real-time, and scalable communication between the different elements.

---

## 🎯 Project Objective

- **Receive Telemetries (TM)** from the modem (real-time TCP flow)
- **Send Telecommands (TC)** to the modem (TCP uplink flow)
- **Retrieve modem metrics** (via REST API)

---

## 📦 Service Architecture

| Service           | Role                                                       |
|-------------------|------------------------------------------------------------|
| `modem_simulator` | Simulates a modem with API (FastAPI), TM (port 1234), TC (4321) |
| `data_pipeline`   | Transfers TM and TC via RabbitMQ                        |
| `client_script`   | Consumes TM, sends TC, reads modem metrics           |
| `rabbitmq`        | Central message broker (RabbitMQ 3-management)            |

---

## ⚙️ Prerequisites

- ✅ [Docker](https://www.docker.com/products/docker-desktop)
- ✅ [Python 3.10+](https://www.python.org/)

**Note**: Configure the environment variables `RABBITMQ_USER` and `RABBITMQ_PASS` for RabbitMQ credentials.

---

## 🚀 Launch the Complete Stack

```bash
docker-compose up -d --build
```

This starts all services (modem, pipeline, client, rabbitmq).

### Access :
- 📡 Modem API : [http://localhost:8000/metrics/status](http://localhost:8000/metrics/status)
- 🐰 RabbitMQ Interface : [http://localhost:15672](http://localhost:15672)  
  credentials : `user` / `pass`

---

## 📦 Modem API

- **GET** `/metrics/status`: Returns the system status.
- **GET** `/metrics/signal_strength`: Returns the signal strength.
- **GET** `/metrics/bit_error_rate`: Returns the binary error rate.
- **GET** `/metrics/statistics`: Returns the system statistics.

---

## 🧪 Run the Tests

### ▶️ All Tests (to be done from the container or locally) :

Use the following script to run the tests :

```bash
docker-compose up --build
docker-compose exec client pytest tests/ -v
```

---

## 📁 Project Directory Structure

```
skynopy-challenge-full-project/
├── client_script/            # Client logic TM/TC/API
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── tests/                # Unit/integration tests
├── data_pipeline/            # Routing via RabbitMQ
│   ├── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── modem_simulator/          # FastAPI + sockets TM/TC
├── docker-compose.yml        # Multi-service stack
├── requirements.txt          # Dependencies for tests
└── README.md
```

---

## 🤖 Continuous Integration (CI)

This project includes a CI pipeline via **GitHub Actions** (`.github/workflows/test.yml`) that :
- Installs dependencies
- Runs unit tests
- Starts all containers
- Executes integration tests

---

## ✅ Recommended Test Scenarios

| Scenario                          | Expected |
|----------------------------------|---------|
| 🔄 TM Flow                       | The client displays received packets |
| 📤 TC Sending                   | The modem displays `[TC RECEIVED]` and returns `ACK` |
| 📦 Metrics API                   | The client logs `/metrics/...` responses |
| 🔌 Modem Restart                | The client continues to receive data |
| 🔀 Multiple Clients             | All receive the same TM via RabbitMQ |

---

## 💡 Evolution Ideas

- CLI or Web (Streamlit) interface to visualize flows
- Prometheus / Grafana integration for metrics
- Cloud deployment (Render, Railway, EC2...)

---

## 👨‍💻 Authors

Challenge completed as part of a technical demonstration  
📤 GitHub Share : `viconnex`, `polcout`

---

Made with ❤️ in **Python**, **Docker**, **FastAPI**, **RabbitMQ**, **asyncio**