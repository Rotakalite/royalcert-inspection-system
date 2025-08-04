# RoyalCert Backend API

## FastAPI Backend for Periyodik Muayene Sistemi

### Features
- JWT Authentication
- Role-based Access Control (Admin, Planlama Uzmanı, Denetçi)
- Customer Management
- Equipment Templates
- Inspection Management
- Dashboard Statistics

### Setup
```bash
pip install -r requirements.txt
uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

### Default Admin User
- Username: admin
- Password: admin123

### API Documentation
Once running, visit: http://localhost:8001/docs