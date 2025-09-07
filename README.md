# Inventory Service

A standalone **Inventory Service** for an e-commerce platform, built with **Spring Boot (Java)**, **React**, and **MySQL**.  
It provides RESTful APIs for inventory management along with a modern frontend dashboard.  
The project is fully Dockerized for local development and includes OpenAPI (Swagger) documentation.

---

## ✨ Features
- CRUD operations for inventory items (Create, Read, Update, Delete)
- Stock quantity management
- Real-time updated dashboard
- OpenAPI (Swagger) documentation for APIs
- Docker Compose setup for local dev (backend + frontend + MySQL)

---

## 🛠 Tech Stack
- **Backend:** Spring Boot (Java 17)
- **Frontend:** React.js
- **Database:** MySQL
- **DevOps:** Docker, Docker Compose

---

## 🚀 Getting Started

### Prerequisites
- [Docker](https://docs.docker.com/get-docker/) & Docker Compose
- Java 17+ (for manual backend build/run)
- Node.js (for manual frontend build/run)

---

### Local Development (Recommended)

1. Clone the repository:
   ```sh
   git clone <repo-url>
   cd inventory-service

2. Start all services:

  cd infra
  docker-compose up --build

3. Access the services:

   Backend API: http://localhost:8080/api/v1/inventory

   Swagger UI: http://localhost:8080/swagger-ui.html

   Frontend: http://localhost:3000

### Manual Development (Alternative)

  -> Backend:

    cd backend
    ./mvnw spring-boot:run
  
  -> Frontend:

    cd frontend
    npm install
    npm start

  -> Database (MySQL):

     => Ensure MySQL is running locally.
     => Update backend/src/main/resources/application.properties with your credentials.

### 🗄 Database Schema
The service auto-creates the inventory_items table:

Column	Type	Notes
id	BIGINT (PK)	Auto-increment
name	VARCHAR	Item name
sku	VARCHAR	Stock Keeping Unit
quantity	INT	Current stock
location	VARCHAR	Warehouse location
updated_at	TIMESTAMP	Auto-updated

### 📖 API Documentation
   Once running, explore APIs via Swagger UI:
   👉 http://localhost:8080/swagger-ui.html

### 🐳 Docker Setup
   Backend, frontend, and MySQL are containerized.
   Use the provided docker-compose.yml in the infra/ directory for orchestration.

### 📜 License
This project is licensed under the MIT License.

### 🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you’d like to change.
