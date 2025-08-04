# 🏛️ RoyalCert Periyodik Muayene Sistemi

**RoyalCert Belgelendirme ve Gözetim Hizmetleri A.Ş.** için geliştirilmiş kapsamlı periyodik muayene yönetim sistemi.

## 📊 Sistem Mimarisi

```
Frontend (React) ↔ Backend (FastAPI) ↔ MongoDB Atlas
     ↓                    ↓                ↓
   Vercel             Railway        Cloud Database
```

## 🎯 Ana Özellikler

### 👥 **3 Farklı Kullanıcı Rolü**
- **Admin**: Sistem yönetimi, kullanıcı ekleme, template yönetimi
- **Planlama Uzmanı**: Müşteri kayıt, denetim planlama, toplu import
- **Denetçi**: Atanan denetimleri gerçekleştirme, rapor oluşturma

### 🏢 **Müşteri Yönetimi**
- Müşteri bilgileri + ekipman tek form
- Excel/CSV ile toplu müşteri import
- Müşteri-ekipman ilişki yönetimi

### 📋 **Dynamic Template System**
- 60+ farklı ekipman tipi desteği
- Her ekipman için özel kontrol listeleri
- 8 ana kategori: Kumanda, Sınırlayıcılar, Fren, Zincir, Yapısal, Erişim, vb.
- U/UD/U.Y değerlendirme sistemi

### 📅 **Denetim Planlama**
- Müşteri-ekipman-denetçi eşleştirmesi
- Takvim bazlı planlama
- Denetim durumu takibi

### ✅ **Denetim Gerçekleştirme**
- Mobile-responsive inspection forms
- Kategori bazında kontrol maddeleri
- Fotoğraf upload desteği
- Draft kaydetme özelliği

### 📄 **Rapor Sistemi**
- PDF export (Word template formatı)
- Kontrol formu ve Muayene raporu ayrımı
- Digital signature support
- QR code doğrulama

### 📊 **Dashboard & Analytics**
- Role-based dashboard görünümleri
- Real-time istatistikler
- Performance tracking

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern, fast Python web framework
- **Motor** - Async MongoDB driver
- **JWT** - Authentication & authorization
- **Pydantic** - Data validation
- **Passlib** - Password hashing

### Frontend
- **React 18** - Modern UI framework
- **Tailwind CSS** - Utility-first CSS
- **Axios** - HTTP client
- **Context API** - State management

### Database
- **MongoDB Atlas** - Cloud database
- **UUID** - Primary keys (no ObjectID)
- **Indexed queries** - Performance optimization

## 🚀 Hızlı Başlangıç

### Prerequisites
- Node.js 16+
- Python 3.9+
- MongoDB Atlas account

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

### Frontend Setup
```bash
cd frontend
yarn install
yarn start
```

## 🔐 Varsayılan Kullanıcı

Sistem ilk başlatıldığında otomatik admin kullanıcısı oluşturulur:

```
Kullanıcı Adı: admin
Şifre: admin123
```

## 📱 API Endpoints

### Authentication
- `POST /api/auth/login` - Kullanıcı girişi
- `POST /api/auth/register` - Yeni kullanıcı (Admin only)
- `GET /api/auth/me` - Mevcut kullanıcı bilgisi

### Customer Management
- `GET /api/customers` - Müşteri listesi
- `POST /api/customers` - Yeni müşteri
- `PUT /api/customers/{id}` - Müşteri güncelleme
- `DELETE /api/customers/{id}` - Müşteri silme

### Inspection Management
- `GET /api/inspections` - Denetim listesi (role-based)
- `POST /api/inspections` - Yeni denetim planlama
- `GET /api/inspections/{id}` - Denetim detayı

### Equipment Templates
- `GET /api/equipment-templates` - Template listesi
- `POST /api/equipment-templates` - Yeni template (Admin only)

### Dashboard
- `GET /api/dashboard/stats` - Dashboard istatistikleri

## 🎨 UI/UX Features

- **Modern Design** - Clean, professional interface
- **Responsive** - Mobile, tablet, desktop uyumlu
- **Dark Mode Ready** - Theme support
- **Loading States** - Smooth user experience
- **Error Handling** - Comprehensive error messages
- **Toast Notifications** - Real-time feedback

## 📊 Database Schema

### Users Collection
```javascript
{
  id: "uuid",
  username: "string",
  email: "string", 
  full_name: "string",
  role: "admin|planlama_uzmani|denetci",
  is_active: boolean,
  created_at: datetime
}
```

### Customers Collection
```javascript
{
  id: "uuid",
  company_name: "string",
  contact_person: "string",
  phone: "string",
  email: "string", 
  address: "string",
  equipments: [equipment_objects],
  created_at: datetime
}
```

### Equipment Templates Collection
```javascript
{
  id: "uuid",
  equipment_type: "string",
  categories: [
    {
      name: "string",
      items: [
        {
          id: number,
          text: "string",
          input_type: "dropdown|text|number",
          has_comment: boolean
        }
      ]
    }
  ],
  created_at: datetime
}
```

### Inspections Collection
```javascript
{
  id: "uuid",
  customer_id: "uuid",
  equipment_info: object,
  inspector_id: "uuid",
  planned_date: datetime,
  status: "beklemede|devam_ediyor|tamamlandi",
  created_by: "uuid",
  created_at: datetime
}
```

## 🚀 Deployment

### Railway (Backend)
```bash
# Auto-deploy from GitHub
# Environment variables needed:
MONGO_URL=mongodb+srv://...
SECRET_KEY=your-secret-key
DATABASE_NAME=royalcert_db
```

### Vercel (Frontend)
```bash
# Auto-deploy from GitHub
# Environment variables needed:
REACT_APP_BACKEND_URL=https://your-railway-url
```

## 🔧 Environment Variables

### Backend (.env)
```
MONGO_URL=mongodb+srv://royalcert_user:Ccpp1144..@royalcert-cluster.l1hqqn.mongodb.net/
SECRET_KEY=royalcert-super-secret-key-2025
DATABASE_NAME=royalcert_db
```

### Frontend (.env)
```
REACT_APP_BACKEND_URL=http://localhost:8001
GENERATE_SOURCEMAP=false
```

## 📈 Roadmap

### Phase 1: Core System ✅
- [x] Authentication & Authorization
- [x] User Management
- [x] Customer Management  
- [x] Basic Dashboard

### Phase 2: Templates & Forms (In Progress)
- [ ] Equipment Template Management
- [ ] Dynamic Form Builder
- [ ] Caraskal Template Implementation

### Phase 3: Inspection System
- [ ] Inspection Planning Interface
- [ ] Mobile Inspection Forms
- [ ] Photo Upload Support

### Phase 4: Reporting
- [ ] PDF Generation
- [ ] Report Templates
- [ ] Digital Signatures

### Phase 5: Advanced Features
- [ ] Bulk Import System
- [ ] Advanced Analytics
- [ ] Mobile App (React Native)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

**RoyalCert Belgelendirme ve Gözetim Hizmetleri A.Ş.**
- Email: info@royalcert.com
- Website: https://royalcert.com

---

**Development Status**: ✅ Phase 1 Complete - Core system operational
**Last Updated**: March 2025