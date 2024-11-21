# int3105-55-services
 Services for Software Architecture final project

##  Exchange Rate Service
### 1. Build docker and run
```sh
cd exchange-rate-service
docker-compose up --build
```

- Container 1 runs on port 3304

- Container 2 runs on port 3305
### 2. Run sidecar
```sh
python .\sidecar\sidecar.py
```

## RabbitMQ
### Create network
```sh
docker network create --subnet=172.30.0.0/16 service_network
```

### Run rabbitMQ container
```sh
docker run -it --rm --name rabbitmq --network service_network --ip 172.30.0.2 -p 5672:5672 -p 15672:15672 rabbitmq:4.0-management
```
