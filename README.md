# 🌍 Smart Carbon Emission Monitoring & Renewable Credit Trading Platform

A **production-ready, hackathon-winning** web platform that monitors household-level carbon emissions in real-time, predicts future emissions using AI, and enforces sustainability through a renewable-backed carbon credit trading system.

![Platform Status](https://img.shields.io/badge/status-production--ready-success)
![Tech Stack](https://img.shields.io/badge/stack-Flask%20%2B%20Next.js-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 🎯 Project Overview

This platform collects emission data from IoT devices (ESP32 + sensors), calculates CO₂ emissions using **transparent rule-based logic**, compares it against household carbon limits, predicts future emissions using **explainable AI**, and forces sustainability investment via **renewable energy credits** when limits are exceeded.

### Key Features

✅ **Real-time Emission Monitoring** - Track electricity and combustion CO₂  
✅ **Rule-Based Calculations** - Transparent, auditable emission formulas  
✅ **AI Predictions** - Linear Regression for future emission forecasting  
✅ **Carbon Limit System** - Automatic household-based limit calculation  
✅ **Renewable Credit Trading** - Solar, Wind, Bio-energy credits (no tree offsets)  
✅ **Beautiful Dashboard** - Dark theme with eco-green glassmorphism  
✅ **IoT-Ready** - ESP32 + ACS712 + MH-Z19 sensor support  
✅ **Demo Mode** - One-click simulation for presentations  

---

## 🏗️ System Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   IoT Devices   │─────▶│   Flask Backend  │◀────▶│  Next.js UI     │
│  (ESP32 + MH-Z19)│      │  (Python + ML)   │      │  (React + TS)   │
└─────────────────┘      └──────────────────┘      └─────────────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │    MongoDB       │
                         │  (Time-Series)   │
                         └──────────────────┘
```

### Data Flow

1. **IoT Sensors** → Send electricity (kWh) + combustion (ppm) data
2. **Emission Calculator** → Apply scientific formulas (NO ML)
3. **Database** → Store time-series emission records
4. **AI Predictor** → Train Linear Regression on historical data
5. **Carbon Limit Service** → Compare emissions vs household limit
6. **Credit Trading** → Purchase renewable credits if exceeded
7. **Dashboard** → Visualize everything beautifully

---

## 🛠️ Tech Stack

### Backend
- **Flask** - RESTful API server
- **MongoDB** - Time-series emission storage
- **JWT** - Secure authentication
- **Scikit-learn** - Linear Regression AI
- **NumPy/Pandas** - Data processing

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Recharts** - Beautiful data visualizations
- **Axios** - API communication

### Design
- **Dark Theme** - `#0a0e1a` background
- **Eco-Green Accents** - `#10b981` primary color
- **Glassmorphism** - Frosted glass effects
- **Smooth Animations** - CSS transitions + keyframes

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- MongoDB (local or cloud)

### 1. Backend Setup

\`\`\`bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your MongoDB URI

# Start server
python app.py
\`\`\`

Backend runs on **http://localhost:5000**

### 2. Frontend Setup

\`\`\`bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
\`\`\`

Frontend runs on **http://localhost:3000**

### 3. MongoDB Setup

**Option A: Local MongoDB**
\`\`\`bash
# Install MongoDB Community Edition
# Start MongoDB service
mongod --dbpath /path/to/data
\`\`\`

**Option B: MongoDB Atlas (Cloud)**
1. Create free cluster at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Get connection string
3. Update `MONGO_URI` in `backend/.env`

---

## 📊 API Documentation

### Authentication

#### Register User
\`\`\`http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepass",
  "area_sqm": 100,
  "occupants": 4
}
\`\`\`

#### Login
\`\`\`http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepass"
}
\`\`\`

### IoT Data Ingestion

#### Send Emission Data
\`\`\`http
POST /api/iot/emission
Authorization: Bearer <token>
Content-Type: application/json

{
  "electricity_kwh": 5.2,
  "combustion_ppm": 450
}
\`\`\`

**Response:**
\`\`\`json
{
  "success": true,
  "calculated_emissions": {
    "electricity_co2_kg": 4.42,
    "combustion_co2_kg": 0.81,
    "total_co2_kg": 5.23
  }
}
\`\`\`

### Emissions

#### Get Status
\`\`\`http
GET /api/emissions/status
Authorization: Bearer <token>
\`\`\`

**Response:**
\`\`\`json
{
  "status": "exceeded",
  "annual_limit_kg": 9000,
  "total_emitted_kg": 9500,
  "percentage_used": 105.56,
  "excess_co2_kg": 500,
  "needs_credits": true
}
\`\`\`

### Credits

#### Purchase Credits
\`\`\`http
POST /api/credits/purchase
Authorization: Bearer <token>
Content-Type: application/json

{
  "credit_type": "solar",
  "amount_kg_co2": 500
}
\`\`\`

### Predictions

#### Get AI Forecast
\`\`\`http
GET /api/predictions/forecast?days=30
Authorization: Bearer <token>
\`\`\`

### Demo

#### Generate Demo Data
\`\`\`http
POST /api/demo/simulate-exceed
Authorization: Bearer <token>
\`\`\`

---

## 🧮 Emission Calculation Methodology

### Why Rule-Based (NOT ML)?

Core emission calculations use **transparent, scientific formulas** for:
- ✅ Auditability
- ✅ Explainability
- ✅ Regulatory compliance
- ✅ User trust

### Formulas

**Electricity CO₂:**
\`\`\`
CO₂ (kg) = kWh × 0.85
\`\`\`
*Based on average grid emission factor*

**Combustion CO₂:**
\`\`\`
CO₂ (kg) = ppm × 0.0018
\`\`\`
*Conversion from ppm to kg under standard conditions*

**Carbon Limit:**
\`\`\`
Annual Limit = (area_sqm × 50) + (occupants × 1000)
\`\`\`
*Household-based sustainable limit*

---

## 🤖 AI Model Explanation

### Why Linear Regression?

| Feature | Linear Regression | LSTM |
|---------|------------------|------|
| Explainability | ✅ High | ❌ Low |
| Training Speed | ✅ Fast | ❌ Slow |
| Data Requirements | ✅ Low | ❌ High |
| Judge-Friendly | ✅ Yes | ❌ Complex |

### Features Used

1. **Day of Month** - Temporal pattern
2. **Month** - Seasonal variation
3. **Occupants** - Household size
4. **7-Day Avg Electricity** - Recent trend
5. **7-Day Avg Combustion** - Recent trend

### Model Output

- **Predictions** - Next 7/14/30 days
- **Warning** - If projected to exceed limit
- **Coefficients** - Feature importance (explainability)

### Future Scope (Not Implemented)

- LSTM for complex patterns
- Multi-household collaborative filtering
- Weather-based adjustments

---

## 🎨 UI/UX Design

### Color Palette

| Color | Hex | Usage |
|-------|-----|-------|
| Dark BG | `#0a0e1a` | Background |
| Dark Surface | `#141824` | Cards |
| Eco Green | `#10b981` | Primary actions |
| Status Safe | `#10b981` | ≤70% limit |
| Status Warning | `#fbbf24` | 70-100% limit |
| Status Exceeded | `#ef4444` | >100% limit |

### Design Principles

✨ **Glassmorphism** - Frosted glass cards  
🌊 **Smooth Animations** - 300ms transitions  
📱 **Responsive** - Mobile-first design  
🎯 **Judge-Friendly** - Clear visual hierarchy  

---

## 🎮 Demo Mode

Perfect for hackathon presentations!

### Quick Demo Flow

1. **Register** → Create account with household info
2. **Generate Data** → Click "Generate Demo Data" button
3. **View Dashboard** → See real-time gauges, charts, predictions
4. **Exceed Limit** → Demo data triggers limit exceed
5. **Purchase Credits** → Simulate credit purchase
6. **Status Update** → See "Neutralized" status

### Demo Scenarios

- **Safe Scenario** - Stable emissions within limit
- **Exceed Scenario** - Gradual increase to trigger credits
- **Custom Pattern** - Configurable emission patterns

---

## 📁 Project Structure

\`\`\`
carbon-trading-platform/
├── backend/
│   ├── app.py                    # Flask application
│   ├── config.py                 # Configuration
│   ├── models/                   # MongoDB models
│   │   ├── user.py
│   │   ├── emission.py
│   │   └── credit.py
│   ├── services/                 # Business logic
│   │   ├── emission_calculator.py
│   │   ├── carbon_limit_service.py
│   │   ├── credit_service.py
│   │   └── ai_predictor.py
│   ├── routes/                   # API endpoints
│   │   ├── auth.py
│   │   ├── emissions.py
│   │   ├── credits.py
│   │   └── predictions.py
│   └── utils/
│       └── demo_data_generator.py
│
├── frontend/
│   ├── app/                      # Next.js pages
│   │   ├── login/
│   │   ├── register/
│   │   └── dashboard/
│   ├── components/               # React components
│   │   ├── StatusBadge.tsx
│   │   ├── EmissionGauge.tsx
│   │   ├── CarbonLimitMeter.tsx
│   │   ├── EmissionChart.tsx
│   │   ├── CreditPurchaseModal.tsx
│   │   └── PredictionGraph.tsx
│   ├── contexts/
│   │   └── AuthContext.tsx
│   └── lib/
│       └── api.ts
│
└── README.md
\`\`\`

---

## 🔌 IoT Integration

### Supported Sensors

- **ESP32** - Microcontroller
- **ACS712** - Current sensor (electricity)
- **MH-Z19** - CO₂ sensor (combustion)

### Sample ESP32 Code

\`\`\`cpp
#include <WiFi.h>
#include <HTTPClient.h>

const char* API_URL = "http://your-server.com/api/iot/emission";
const char* TOKEN = "your_jwt_token";

void sendEmissionData(float kwh, float ppm) {
  HTTPClient http;
  http.begin(API_URL);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("Authorization", "Bearer " + String(TOKEN));
  
  String payload = "{\"electricity_kwh\":" + String(kwh) + 
                   ",\"combustion_ppm\":" + String(ppm) + "}";
  
  int httpCode = http.POST(payload);
  http.end();
}
\`\`\`

---

## 🏆 Hackathon Pitch Points

### Problem Statement
❌ Traditional carbon offsetting (tree planting) is slow and unverifiable  
❌ Households lack real-time emission awareness  
❌ No enforcement mechanism for carbon limits  

### Our Solution
✅ **Real-time monitoring** via IoT sensors  
✅ **Transparent calculations** (no black-box ML)  
✅ **Renewable credits** (solar/wind/bio) instead of trees  
✅ **AI predictions** to prevent limit exceeds  
✅ **Immediate enforcement** through credit trading  

### Impact
🌍 **Environmental** - Direct renewable energy investment  
📊 **Transparency** - Auditable emission tracking  
⚡ **Scalability** - Cloud-ready architecture  
🎯 **Policy-Ready** - Regulatory compliance built-in  

### Technical Excellence
🔧 **Production-Ready** - Full error handling, validation  
🎨 **Beautiful UI** - Judge-friendly design  
🤖 **Explainable AI** - Linear Regression with coefficients  
📡 **IoT-Ready** - ESP32 integration  

---

## 🔮 Future Enhancements

- [ ] Blockchain-based credit verification
- [ ] Mobile app (React Native)
- [ ] Smart appliance automation
- [ ] Government carbon policy integration
- [ ] Multi-household community features
- [ ] Advanced ML models (LSTM, Prophet)
- [ ] Carbon credit marketplace
- [ ] Real-time sensor dashboard

---

## 📄 License

MIT License - feel free to use for hackathons, projects, or production!

---

## 👥 Contributors

Built with ❤️ for sustainability and innovation.

---

## 📞 Support

For questions or issues:
- 📧 Email: support@carbontradingplatform.com
- 🐛 Issues: GitHub Issues
- 📚 Docs: See `/docs` folder

---

**🌱 Let's build a sustainable future together!**
