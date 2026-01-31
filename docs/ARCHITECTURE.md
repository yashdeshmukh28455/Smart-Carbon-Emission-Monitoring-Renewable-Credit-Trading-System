# System Architecture

## Overview Diagram

\`\`\`mermaid
graph TB
    subgraph "IoT Layer"
        ESP[ESP32 Microcontroller]
        ACS[ACS712 Current Sensor]
        MHZ[MH-Z19 CO2 Sensor]
    end
    
    subgraph "Backend Layer"
        API[Flask REST API]
        AUTH[JWT Authentication]
        CALC[Emission Calculator]
        LIMIT[Carbon Limit Service]
        CREDIT[Credit Service]
        AI[AI Predictor]
    end
    
    subgraph "Data Layer"
        MONGO[(MongoDB)]
        USERS[Users Collection]
        EMISSIONS[Emissions Collection]
        CREDITS[Credits Collection]
    end
    
    subgraph "Frontend Layer"
        NEXT[Next.js App]
        LOGIN[Login/Register]
        DASH[Dashboard]
        CHARTS[Charts & Gauges]
        MODAL[Credit Purchase]
    end
    
    ESP --> ACS
    ESP --> MHZ
    ESP -->|HTTP POST| API
    
    API --> AUTH
    API --> CALC
    API --> LIMIT
    API --> CREDIT
    API --> AI
    
    CALC --> MONGO
    LIMIT --> MONGO
    CREDIT --> MONGO
    AI --> MONGO
    
    MONGO --> USERS
    MONGO --> EMISSIONS
    MONGO --> CREDITS
    
    NEXT --> LOGIN
    NEXT --> DASH
    DASH --> CHARTS
    DASH --> MODAL
    
    NEXT -->|Axios| API
\`\`\`

## Data Flow

### 1. Emission Data Ingestion

\`\`\`mermaid
sequenceDiagram
    participant IoT as IoT Device
    participant API as Flask API
    participant Calc as Emission Calculator
    participant DB as MongoDB
    
    IoT->>API: POST /api/iot/emission
    Note over IoT,API: {electricity_kwh, combustion_ppm}
    
    API->>Calc: calculate_total_co2()
    Note over Calc: Apply scientific formulas
    Calc->>Calc: electricity_co2 = kwh × 0.85
    Calc->>Calc: combustion_co2 = ppm × 0.0018
    Calc-->>API: {electricity_co2_kg, combustion_co2_kg}
    
    API->>DB: Insert emission record
    DB-->>API: emission_id
    API-->>IoT: Success response
\`\`\`

### 2. Carbon Status Check

\`\`\`mermaid
sequenceDiagram
    participant UI as Dashboard
    participant API as Flask API
    participant Limit as Carbon Limit Service
    participant DB as MongoDB
    
    UI->>API: GET /api/emissions/status
    API->>Limit: get_user_status()
    
    Limit->>DB: Get user household data
    DB-->>Limit: {area_sqm, occupants, limit}
    
    Limit->>DB: Get total emissions (YTD)
    DB-->>Limit: total_co2_kg
    
    Limit->>DB: Get active credits
    DB-->>Limit: total_credits_kg
    
    Limit->>Limit: Calculate net emissions
    Limit->>Limit: Determine status (safe/warning/exceeded)
    Limit-->>API: Status object
    API-->>UI: Display status
\`\`\`

### 3. Credit Purchase Flow

\`\`\`mermaid
sequenceDiagram
    participant UI as Dashboard
    participant Modal as Credit Modal
    participant API as Flask API
    participant Credit as Credit Service
    participant DB as MongoDB
    
    UI->>UI: Detect limit exceeded
    UI->>Modal: Open modal with excess_co2
    
    Modal->>Modal: User selects credit type
    Modal->>Modal: User confirms amount
    
    Modal->>API: POST /api/credits/purchase
    Note over Modal,API: {credit_type, amount_kg_co2}
    
    API->>Credit: purchase_credits()
    Credit->>DB: Insert credit record
    Note over DB: Valid for 1 year
    DB-->>Credit: credit_id
    
    Credit-->>API: Purchase confirmation
    API-->>Modal: Success
    Modal->>UI: Refresh status
    UI->>UI: Status updated to "Neutralized"
\`\`\`

### 4. AI Prediction Workflow

\`\`\`mermaid
sequenceDiagram
    participant UI as Dashboard
    participant API as Flask API
    participant AI as AI Predictor
    participant DB as MongoDB
    
    UI->>API: GET /api/predictions/forecast
    
    API->>AI: get_prediction_with_warning()
    
    AI->>DB: Get historical emissions (60 days)
    DB-->>AI: emission_records[]
    
    AI->>AI: Prepare features
    Note over AI: day, month, occupants, 7d_avg
    
    AI->>AI: Train Linear Regression
    Note over AI: X = features, y = total_co2
    
    AI->>AI: Generate predictions (30 days)
    AI->>AI: Check if will exceed limit
    
    AI-->>API: {predictions, warning}
    API-->>UI: Display forecast graph
\`\`\`

## Component Architecture

### Backend Services

\`\`\`mermaid
graph LR
    subgraph "Core Services"
        EC[Emission Calculator]
        CLS[Carbon Limit Service]
        CS[Credit Service]
        AIP[AI Predictor]
    end
    
    subgraph "Models"
        UM[User Model]
        EM[Emission Model]
        CM[Credit Model]
    end
    
    EC -.->|Uses| EM
    CLS -.->|Uses| UM
    CLS -.->|Uses| EM
    CLS -.->|Uses| CM
    CS -.->|Uses| CM
    AIP -.->|Uses| EM
\`\`\`

### Frontend Components

\`\`\`mermaid
graph TB
    subgraph "Pages"
        LP[Login Page]
        RP[Register Page]
        DP[Dashboard Page]
    end
    
    subgraph "Components"
        SB[StatusBadge]
        EG[EmissionGauge]
        CLM[CarbonLimitMeter]
        EC[EmissionChart]
        CPM[CreditPurchaseModal]
        PG[PredictionGraph]
    end
    
    subgraph "Context"
        AC[AuthContext]
    end
    
    LP --> AC
    RP --> AC
    DP --> AC
    
    DP --> SB
    DP --> EG
    DP --> CLM
    DP --> EC
    DP --> CPM
    DP --> PG
\`\`\`

## Database Schema

### Users Collection

\`\`\`json
{
  "_id": ObjectId,
  "email": String,
  "password_hash": String,
  "household": {
    "area_sqm": Number,
    "occupants": Number,
    "annual_carbon_limit_kg": Number
  },
  "created_at": DateTime
}
\`\`\`

### Emissions Collection

\`\`\`json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "timestamp": DateTime,
  "electricity_kwh": Number,
  "electricity_co2_kg": Number,
  "combustion_ppm": Number,
  "combustion_co2_kg": Number,
  "total_co2_kg": Number,
  "source": "iot" | "simulated"
}
\`\`\`

### Credits Collection

\`\`\`json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "credit_type": "solar" | "wind" | "bio",
  "amount_kg_co2": Number,
  "purchase_date": DateTime,
  "expiry_date": DateTime,
  "status": "active" | "expired",
  "transaction_id": String
}
\`\`\`

## Technology Stack Details

### Backend Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Flask | 3.0.0 | Web framework |
| PyMongo | 4.6.1 | MongoDB driver |
| Flask-JWT-Extended | 4.6.0 | Authentication |
| Scikit-learn | 1.4.0 | Machine learning |
| NumPy | 1.26.3 | Numerical computing |
| Pandas | 2.2.0 | Data manipulation |

### Frontend Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 14 | React framework |
| TypeScript | 5.x | Type safety |
| Tailwind CSS | 3.x | Styling |
| Recharts | 2.x | Data visualization |
| Axios | 1.x | HTTP client |

## Security Architecture

### Authentication Flow

1. User registers/logs in
2. Server generates JWT token (24h expiry)
3. Client stores token in localStorage
4. All API requests include `Authorization: Bearer <token>`
5. Server validates token on each request

### Data Protection

- Passwords hashed with bcrypt
- JWT secret key in environment variables
- CORS enabled for frontend origin only
- Input validation on all endpoints

## Scalability Considerations

### Horizontal Scaling

- Stateless API (JWT-based auth)
- MongoDB sharding for large datasets
- Load balancer for multiple Flask instances

### Performance Optimization

- Database indexes on user_id and timestamp
- Aggregation pipelines for emission queries
- Client-side caching with React Query (future)

### Monitoring

- API response time tracking
- Database query performance
- Error logging and alerting

---

This architecture is designed for **production deployment** while maintaining **hackathon-friendly simplicity**.
