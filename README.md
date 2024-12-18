# int3105-55-services
Services for Software Architecture Final Project

---

## RabbitMQ
### Create Network
To set up the RabbitMQ network:
```bash
docker network create --subnet=172.30.0.0/16 rabbitmq_network
```

### Run RabbitMQ Container
Run the RabbitMQ container with management plugins enabled:
```bash
docker run -it --rm --name rabbitmq --network rabbitmq_network --ip 172.30.0.2 -p 5672:5672 -p 15672:15672 rabbitmq:4.0-management
```

---

## Exchange Rate & Gold Price Service & Message Queue Service

### Build Docker Images and Run Services
To build and run the services:
```bash
docker-compose up --build
```

### Run Sidecar Services
To start the sidecar services for monitoring:
```bash
python ./exchange-rate-service/sidecar/sidecar.py
python ./gold-price-service/sidecar/sidecar.py
python ./queue/sidecar/sidecar.py
```

---

## Initialize New Containers
### Setup for `exchange_rate_service_no3` and its Redis Container

#### Create a New Network for the Redis Container
Create a dedicated network for the Redis container:
```bash
docker network create redis_network_service_6
```

#### Create the Redis Container
Run the Redis container:
```bash
docker run -d --name redis_for_exchange_rate_service_no3 --network redis_network_service_6 -p 6385:6379 redis:latest
```

#### Run the Service Container
Run the `exchange_rate_service_no3` container:
```bash
docker run -d \
  --name exchange_rate_service_no3 \
  --network rabbitmq_network \
  --network redis_network_service_6 \
  -e REDIS_HOST=redis_for_exchange_rate_service_no3 \
  -e CONTAINER_NAME=exchange_rate_service_no3 \
  -e SIDECAR_URL=http://127.0.0.1:4006 \
  -e SERVICE_ID=1 \
  -p 3010:3007 int3105-55-services-app_3
```

### Setup for `gold_price_service_no3` and its Redis Container

#### Create a New Network for the Redis Container
Create a dedicated network for the Redis container:
```bash
docker network create redis_network_service_7
```

#### Create the Redis Container
Run the Redis container:
```bash
docker run -d --name redis_for_gold_price_service_no3 --network redis_network_service_7 -p 6388:6379 redis:latest
```

#### Run the Service Container
Run the `gold_price_service_no3` container:
```bash
docker run -d \
  --name gold_price_service_no3 \
  --network rabbitmq_network \
  --network redis_network_service_7 \
  -e REDIS_HOST=redis_for_gold_price_service_no3 \
  -e CONTAINER_NAME=gold_price_service_no3 \
  -e SIDECAR_URL=http://127.0.0.1:4007 \
  -e SERVICE_ID=2 \
  int3105-55-services-app_1
```

---

### Notes
- Replace `int3105-55-services-app_3` and `int3105-55-services-app_1` with the appropriate Docker images if they differ.
- Ensure the sidecar URLs and service IDs match the configurations in your project.
- RabbitMQ management interface is accessible at `http://<host>:15672`.

