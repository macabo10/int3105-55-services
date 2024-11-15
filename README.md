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