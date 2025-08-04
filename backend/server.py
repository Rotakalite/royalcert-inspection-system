from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
import os
import uuid
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB setup
MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://royalcert_user:Ccpp1144..@royalcert-cluster.l1hqqn.mongodb.net/")
DATABASE_NAME = "royalcert_db"

client = AsyncIOMotorClient(MONGO_URL)
db = client[DATABASE_NAME]

# JWT Setup
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security
security = HTTPBearer()

app = FastAPI(title="RoyalCert Periyodik Muayene Sistemi", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================== MODELS =====================

class UserRole(str):
    ADMIN = "admin"
    PLANLAMA_UZMANI = "planlama_uzmani" 
    DENETCI = "denetci"

class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str
    password: str
    role: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class Customer(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_name: str
    contact_person: str
    phone: str
    email: str
    address: str
    equipments: List[Dict[str, Any]] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CustomerCreate(BaseModel):
    company_name: str
    contact_person: str
    phone: str
    email: str
    address: str
    equipments: List[Dict[str, Any]] = []

class EquipmentTemplate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    equipment_type: str
    categories: List[Dict[str, Any]]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Inspection(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    equipment_info: Dict[str, Any]
    inspector_id: str
    planned_date: datetime
    status: str = "beklemede"  # beklemede, devam_ediyor, tamamlandi
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class InspectionCreate(BaseModel):
    customer_id: str
    equipment_info: Dict[str, Any]
    inspector_id: str
    planned_date: datetime

# ===================== AUTH FUNCTIONS =====================

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"username": username})
    if user is None:
        raise credentials_exception
    
    return User(**user)

def require_role(required_role: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker

# ===================== API ENDPOINTS =====================

@app.post("/api/auth/register", response_model=User)
async def register(user_create: UserCreate, current_user: User = Depends(require_role(UserRole.ADMIN))):
    # Check if username already exists
    existing_user = await db.users.find_one({"username": user_create.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Hash password
    hashed_password = get_password_hash(user_create.password)
    
    # Create user
    user_dict = user_create.dict()
    user_dict["password"] = hashed_password
    user_dict["id"] = str(uuid.uuid4())
    user_dict["created_at"] = datetime.utcnow()
    
    await db.users.insert_one(user_dict)
    
    # Remove password from response
    del user_dict["password"]
    return User(**user_dict)

@app.post("/api/auth/login", response_model=Token)
async def login(user_login: UserLogin):
    user = await db.users.find_one({"username": user_login.username})
    
    if not user or not verify_password(user_login.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.get("is_active", True):
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    
    # Remove password from user data
    del user["password"]
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=User(**user)
    )

@app.get("/api/auth/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

# ===================== USER MANAGEMENT =====================

@app.get("/api/users", response_model=List[User])
async def get_users(current_user: User = Depends(require_role(UserRole.ADMIN))):
    users = await db.users.find({}, {"password": 0}).to_list(1000)
    return [User(**user) for user in users]

@app.delete("/api/users/{user_id}")
async def delete_user(user_id: str, current_user: User = Depends(require_role(UserRole.ADMIN))):
    result = await db.users.delete_one({"id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

# ===================== CUSTOMER MANAGEMENT =====================

@app.post("/api/customers", response_model=Customer)
async def create_customer(customer: CustomerCreate, current_user: User = Depends(require_role(UserRole.PLANLAMA_UZMANI))):
    customer_dict = customer.dict()
    customer_dict["id"] = str(uuid.uuid4())
    customer_dict["created_at"] = datetime.utcnow()
    
    await db.customers.insert_one(customer_dict)
    return Customer(**customer_dict)

@app.get("/api/customers", response_model=List[Customer])
async def get_customers(current_user: User = Depends(get_current_user)):
    customers = await db.customers.find().to_list(1000)
    return [Customer(**customer) for customer in customers]

@app.get("/api/customers/{customer_id}", response_model=Customer)
async def get_customer(customer_id: str, current_user: User = Depends(get_current_user)):
    customer = await db.customers.find_one({"id": customer_id})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return Customer(**customer)

@app.put("/api/customers/{customer_id}", response_model=Customer)
async def update_customer(customer_id: str, customer_update: CustomerCreate, current_user: User = Depends(require_role(UserRole.PLANLAMA_UZMANI))):
    result = await db.customers.update_one(
        {"id": customer_id},
        {"$set": customer_update.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    updated_customer = await db.customers.find_one({"id": customer_id})
    return Customer(**updated_customer)

@app.delete("/api/customers/{customer_id}")
async def delete_customer(customer_id: str, current_user: User = Depends(require_role(UserRole.PLANLAMA_UZMANI))):
    result = await db.customers.delete_one({"id": customer_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Customer deleted successfully"}

# ===================== EQUIPMENT TEMPLATES =====================

@app.post("/api/equipment-templates", response_model=EquipmentTemplate)
async def create_equipment_template(template: EquipmentTemplate, current_user: User = Depends(require_role(UserRole.ADMIN))):
    template_dict = template.dict()
    await db.equipment_templates.insert_one(template_dict)
    return template

@app.get("/api/equipment-templates", response_model=List[EquipmentTemplate])
async def get_equipment_templates(current_user: User = Depends(get_current_user)):
    templates = await db.equipment_templates.find().to_list(1000)
    return [EquipmentTemplate(**template) for template in templates]

# ===================== INSPECTION MANAGEMENT =====================

@app.post("/api/inspections", response_model=Inspection)
async def create_inspection(inspection: InspectionCreate, current_user: User = Depends(require_role(UserRole.PLANLAMA_UZMANI))):
    inspection_dict = inspection.dict()
    inspection_dict["id"] = str(uuid.uuid4())
    inspection_dict["created_by"] = current_user.id
    inspection_dict["created_at"] = datetime.utcnow()
    inspection_dict["status"] = "beklemede"
    
    await db.inspections.insert_one(inspection_dict)
    return Inspection(**inspection_dict)

@app.get("/api/inspections", response_model=List[Inspection])
async def get_inspections(current_user: User = Depends(get_current_user)):
    query = {}
    if current_user.role == UserRole.DENETCI:
        query = {"inspector_id": current_user.id}
    
    inspections = await db.inspections.find(query).to_list(1000)
    return [Inspection(**inspection) for inspection in inspections]

@app.get("/api/inspections/{inspection_id}", response_model=Inspection)
async def get_inspection(inspection_id: str, current_user: User = Depends(get_current_user)):
    query = {"id": inspection_id}
    if current_user.role == UserRole.DENETCI:
        query["inspector_id"] = current_user.id
    
    inspection = await db.inspections.find_one(query)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return Inspection(**inspection)

# ===================== DASHBOARD STATS =====================

@app.get("/api/dashboard/stats")
async def get_dashboard_stats(current_user: User = Depends(get_current_user)):
    stats = {}
    
    if current_user.role in [UserRole.ADMIN, UserRole.PLANLAMA_UZMANI]:
        total_customers = await db.customers.count_documents({})
        total_inspections = await db.inspections.count_documents({})
        pending_inspections = await db.inspections.count_documents({"status": "beklemede"})
        completed_inspections = await db.inspections.count_documents({"status": "tamamlandi"})
        
        stats.update({
            "total_customers": total_customers,
            "total_inspections": total_inspections,
            "pending_inspections": pending_inspections,
            "completed_inspections": completed_inspections
        })
    
    if current_user.role == UserRole.DENETCI:
        my_inspections = await db.inspections.count_documents({"inspector_id": current_user.id})
        my_pending = await db.inspections.count_documents({"inspector_id": current_user.id, "status": "beklemede"})
        my_completed = await db.inspections.count_documents({"inspector_id": current_user.id, "status": "tamamlandi"})
        
        stats.update({
            "my_inspections": my_inspections,
            "my_pending": my_pending,
            "my_completed": my_completed
        })
    
    return stats

# ===================== STARTUP EVENT =====================

@app.on_event("startup")
async def startup_event():
    # Create default admin user if doesn't exist
    admin_exists = await db.users.find_one({"username": "admin"})
    if not admin_exists:
        admin_user = {
            "id": str(uuid.uuid4()),
            "username": "admin",
            "email": "admin@royalcert.com",
            "full_name": "System Administrator",
            "role": UserRole.ADMIN,
            "password": get_password_hash("admin123"),
            "is_active": True,
            "created_at": datetime.utcnow()
        }
        await db.users.insert_one(admin_user)
        print("✅ Default admin user created: admin/admin123")

# ===================== HEALTH CHECK =====================

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)