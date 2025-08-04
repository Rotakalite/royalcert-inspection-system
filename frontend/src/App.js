import React, { useState, useEffect, createContext, useContext } from 'react';
import axios from 'axios';
import './App.css';

// Create Auth Context
const AuthContext = createContext(null);

// API Configuration
const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
const api = axios.create({
  baseURL: `${API_BASE_URL}/api`,
});

// Token interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      window.location.reload();
    }
    return Promise.reject(error);
  }
);

// Auth Provider Component
const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      checkAuthStatus();
    } else {
      setLoading(false);
    }
  }, []);

  const checkAuthStatus = async () => {
    try {
      const response = await api.get('/auth/me');
      setUser(response.data);
    } catch (error) {
      localStorage.removeItem('token');
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    try {
      const response = await api.post('/auth/login', { username, password });
      const { access_token, user } = response.data;
      
      localStorage.setItem('token', access_token);
      setUser(user);
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Giriş başarısız' 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  const value = {
    user,
    login,
    logout,
    loading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook to use auth context
const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Login Component
const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await login(username, password);
    
    if (!result.success) {
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-royal-50 to-royal-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <div className="mx-auto w-20 h-20 mb-4 flex items-center justify-center">
            <img 
              src="https://customer-assets.emergentagent.com/job_yeni-yazilim/artifacts/7675i2kn_WhatsApp%20G%C3%B6rsel%202025-08-04%20saat%2012.57.00_7b510c6c.jpg"
              alt="RoyalCert Logo"
              className="w-full h-full object-contain"
            />
          </div>
          <h2 className="text-2xl font-bold text-royal-900">RoyalCert</h2>
          <p className="text-royal-600 mt-2">Belgelendirme ve Gözetim Hizmetleri</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          )}
          
          <div>
            <label className="block text-sm font-medium text-royal-700 mb-2">
              Kullanıcı Adı
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-3 border border-royal-300 rounded-lg focus:ring-2 focus:ring-red-900 focus:border-transparent"
              placeholder="Kullanıcı adınızı girin"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-royal-700 mb-2">
              Şifre
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 border border-royal-300 rounded-lg focus:ring-2 focus:ring-red-900 focus:border-transparent"
              placeholder="Şifrenizi girin"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-red-900 text-white py-3 rounded-lg font-medium hover:bg-red-800 focus:ring-2 focus:ring-red-900 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition duration-200"
          >
            {loading ? 'Giriş Yapılıyor...' : 'Giriş Yap'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-sm text-royal-500">
            Test kullanıcısı: <span className="font-semibold">admin / admin123</span>
          </p>
        </div>
      </div>
    </div>
  );
};

// Utility StatCard Component  
const StatCard = ({ title, value, color, icon }) => (
  <div className={`${color} rounded-xl p-6`}>
    <div className="flex items-center">
      <div className="flex-shrink-0">
        {icon}
      </div>
      <div className="ml-5 w-0 flex-1">
        <dl>
          <dt className="text-sm font-medium text-gray-500 truncate">{title}</dt>
          <dd className="text-lg font-medium text-gray-900">{value}</dd>
        </dl>
      </div>
    </div>
  </div>
);

const AdminDashboard = () => {
  const [stats, setStats] = useState({});
  const [users, setUsers] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [showCustomerManagement, setShowCustomerManagement] = useState(false);
  const [showInspectionPlanning, setShowInspectionPlanning] = useState(false);
  
  // User Management States
  const [showUserForm, setShowUserForm] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [passwordModalUser, setPasswordModalUser] = useState(null);
  const [userFormData, setUserFormData] = useState({
    username: '',
    email: '',
    full_name: '',
    role: 'denetci',
    password: '',
    confirm_password: '',
    is_active: true
  });

  useEffect(() => {
    fetchStats();
    fetchUsers();
    fetchTemplates();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await api.get('/dashboard/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Stats error:', error);
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await api.get('/users');
      setUsers(response.data);
    } catch (error) {
      console.error('Users error:', error);
    }
  };

  const fetchTemplates = async () => {
    try {
      const response = await api.get('/equipment-templates');
      setTemplates(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Templates error:', error);
      setLoading(false);
    }
  };

  const initializeCaraskalTemplate = async () => {
    try {
      const response = await api.post('/equipment-templates/initialize');
      alert(response.data.message);
      fetchTemplates();
    } catch (error) {
      alert('Caraskal template başlatma hatası: ' + (error.response?.data?.detail || 'Bilinmeyen hata'));
    }
  };

  // User Management Functions
  const handleCreateUser = async (e) => {
    e.preventDefault();
    
    if (userFormData.password !== userFormData.confirm_password) {
      alert('Şifreler eşleşmiyor');
      return;
    }

    if (userFormData.password.length < 6) {
      alert('Şifre en az 6 karakter olmalıdır');
      return;
    }

    try {
      const userData = {
        username: userFormData.username,
        email: userFormData.email,
        full_name: userFormData.full_name,
        role: userFormData.role,
        password: userFormData.password
      };

      if (editingUser) {
        // Update user
        await api.put(`/users/${editingUser.id}`, userData);
        alert('Kullanıcı başarıyla güncellendi');
      } else {
        // Create user
        await api.post('/auth/register', userData);
        alert('Kullanıcı başarıyla oluşturuldu');
      }

      setShowUserForm(false);
      setEditingUser(null);
      setUserFormData({
        username: '',
        email: '',
        full_name: '',
        role: 'denetci',
        password: '',
        confirm_password: '',
        is_active: true
      });
      fetchUsers();
    } catch (error) {
      console.error('User creation error:', error);
      alert('Kullanıcı oluşturma hatası: ' + (error.response?.data?.detail || 'Bilinmeyen hata'));
    }
  };

  const handleEditUser = (user) => {
    setEditingUser(user);
    setUserFormData({
      username: user.username,
      email: user.email,
      full_name: user.full_name,
      role: user.role,
      password: '',
      confirm_password: '',
      is_active: user.is_active
    });
    setShowUserForm(true);
  };

  const handleToggleUserStatus = async (user) => {
    try {
      await api.put(`/users/${user.id}`, {
        is_active: !user.is_active
      });
      alert(`Kullanıcı ${!user.is_active ? 'aktif' : 'pasif'} duruma getirildi`);
      fetchUsers();
    } catch (error) {
      console.error('User status toggle error:', error);
      alert('Kullanıcı durumu değiştirme hatası: ' + (error.response?.data?.detail || 'Bilinmeyen hata'));
    }
  };

  const handleDeleteUser = async (user) => {
    if (!window.confirm(`${user.full_name} kullanıcısını silmek istediğinizden emin misiniz?`)) {
      return;
    }

    try {
      await api.delete(`/users/${user.id}`);
      alert('Kullanıcı başarıyla silindi');
      fetchUsers();
    } catch (error) {
      console.error('User deletion error:', error);
      alert('Kullanıcı silme hatası: ' + (error.response?.data?.detail || 'Bilinmeyen hata'));
    }
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const newPassword = formData.get('new_password');
    const confirmPassword = formData.get('confirm_password');

    if (newPassword !== confirmPassword) {
      alert('Şifreler eşleşmiyor');
      return;
    }

    if (newPassword.length < 6) {
      alert('Şifre en az 6 karakter olmalıdır');
      return;
    }

    try {
      await api.put(`/users/${passwordModalUser.id}/password`, {
        new_password: newPassword
      });
      alert('Şifre başarıyla değiştirildi');
      setShowPasswordModal(false);
      setPasswordModalUser(null);
    } catch (error) {
      console.error('Password change error:', error);
      alert('Şifre değiştirme hatası: ' + (error.response?.data?.detail || 'Bilinmeyen hata'));
    }
  };

  // Show Customer Management
  if (showCustomerManagement) {
    return (
      <CustomerManagement 
        onBack={() => {
          setShowCustomerManagement(false);
          fetchStats();
        }} 
      />
    );
  }

  // Show Inspection Planning
  if (showInspectionPlanning) {
    return (
      <InspectionPlanning 
        onBack={() => {
          setShowInspectionPlanning(false);
          fetchStats();
        }} 
      />
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <img 
            src="https://customer-assets.emergentagent.com/job_yeni-yazilim/artifacts/7675i2kn_WhatsApp%20G%C3%B6rsel%202025-08-04%20saat%2012.57.00_7b510c6c.jpg"
            alt="RoyalCert Logo"
            className="w-16 h-16 object-contain mx-auto mb-4"
          />
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-900 mx-auto"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('overview')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'overview'
                ? 'border-red-900 text-red-900'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Genel Bakış
          </button>
          <button
            onClick={() => setActiveTab('users')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'users'
                ? 'border-red-900 text-red-900'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Kullanıcı Yönetimi
          </button>
          <button
            onClick={() => setActiveTab('templates')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'templates'
                ? 'border-red-900 text-red-900'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Ekipman Template'leri
          </button>
          <button
            onClick={() => setActiveTab('customers')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'customers'
                ? 'border-red-900 text-red-900'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Müşteri Yönetimi
          </button>
          <button
            onClick={() => setActiveTab('inspections')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'inspections'
                ? 'border-red-900 text-red-900'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Denetim Planlama
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatCard
              title="Toplam Müşteri"
              value={stats.total_customers || 0}
              color="bg-blue-100"
              icon={<svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>}
            />
            <StatCard
              title="Toplam Denetim"
              value={stats.total_inspections || 0}
              color="bg-green-100"
              icon={<svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>}
            />
            <StatCard
              title="Bekleyen"
              value={stats.pending_inspections || 0}
              color="bg-yellow-100"
              icon={<svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>}
            />
            <StatCard
              title="Tamamlanan"
              value={stats.completed_inspections || 0}
              color="bg-purple-100"
              icon={<svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"></path></svg>}
            />
          </div>
        </div>
      )}

      {activeTab === 'users' && (
        <div className="bg-white rounded-xl shadow-sm">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Kullanıcılar</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ad Soyad</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Kullanıcı Adı</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">E-posta</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rol</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Durum</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {users.map((user) => (
                  <tr key={user.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {user.full_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {user.username}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {user.email}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        user.role === 'admin' ? 'bg-red-100 text-red-800' :
                        user.role === 'planlama_uzmani' ? 'bg-blue-100 text-blue-800' :
                        user.role === 'teknik_yonetici' ? 'bg-purple-100 text-purple-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {user.role === 'admin' ? 'Admin' : 
                         user.role === 'planlama_uzmani' ? 'Planlama Uzmanı' :
                         user.role === 'teknik_yonetici' ? 'Teknik Yönetici' : 'Denetçi'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        user.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                      }`}>
                        {user.is_active ? 'Aktif' : 'Pasif'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'templates' && (
        <div className="space-y-6">
          {/* Template Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <StatCard
              title="Toplam Template"
              value={templates.length}
              color="bg-indigo-100"
              icon={<svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>}
            />
            <StatCard
              title="Aktif Template"
              value={templates.filter(t => t.is_active).length}
              color="bg-green-100"
              icon={<svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>}
            />
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">Hızlı İşlem</p>
                  <button
                    onClick={initializeCaraskalTemplate}
                    className="mt-2 px-4 py-2 bg-red-900 text-white text-sm rounded-md hover:bg-red-800 focus:outline-none focus:ring-2 focus:ring-red-900"
                  >
                    Caraskal Template Başlat
                  </button>
                </div>
                <div className="flex-shrink-0 p-3 rounded-lg bg-red-100">
                  <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                  </svg>
                </div>
              </div>
            </div>
          </div>

          {/* Templates Table */}
          <div className="bg-white rounded-xl shadow-sm">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-lg font-semibold text-gray-900">Ekipman Template'leri</h2>
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ekipman Tipi</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Açıklama</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Kategori Sayısı</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Kontrol Maddesi</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Oluşturulma</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Durum</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">İşlemler</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {templates.map((template) => (
                    <tr key={template.id}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10">
                            <div className="h-10 w-10 rounded-full bg-red-100 flex items-center justify-center">
                              <svg className="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                              </svg>
                            </div>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">{template.equipment_type}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {template.description}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {template.categories.length} kategori
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {template.categories.reduce((total, cat) => total + cat.items.length, 0)} madde
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(template.created_at).toLocaleDateString('tr-TR')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          template.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {template.is_active ? 'Aktif' : 'Pasif'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button className="text-indigo-600 hover:text-indigo-900 mr-3">Görüntüle</button>
                        <button className="text-red-600 hover:text-red-900">Düzenle</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            {templates.length === 0 && (
              <div className="text-center py-12">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
                <h3 className="mt-2 text-sm font-medium text-gray-900">Henüz template yok</h3>
                <p className="mt-1 text-sm text-gray-500">Caraskal template'ini başlatmak için yukarıdaki butonu kullanın.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'customers' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Müşteri Yönetimi</h2>
              <button
                onClick={() => setShowCustomerManagement(true)}
                className="px-4 py-2 bg-red-900 text-white rounded-md hover:bg-red-800"
              >
                Müşteri Yönetimi'ne Git
              </button>
            </div>
            <p className="text-gray-600">
              Müşteri kayıtlarını, ekipmanları ve toplu içe aktarım işlemlerini yönetin.
            </p>
          </div>
        </div>
      )}

      {activeTab === 'inspections' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Denetim Planlama</h2>
              <button
                onClick={() => setShowInspectionPlanning(true)}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Denetim Planlama'ya Git
              </button>
            </div>
            <p className="text-gray-600">
              Denetim planlama, denetçi atama ve takip işlemlerini yönetin.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

// Bulk Import Modal Component
const BulkImportModal = ({ onClose, onSuccess }) => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [importResult, setImportResult] = useState(null);
  const [showResults, setShowResults] = useState(false);

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      const fileType = selectedFile.name.toLowerCase();
      if (fileType.endsWith('.xlsx') || fileType.endsWith('.xls') || fileType.endsWith('.csv')) {
        setFile(selectedFile);
        setImportResult(null);
        setShowResults(false);
      } else {
        alert('Sadece Excel (.xlsx, .xls) veya CSV dosyaları kabul edilir');
      }
    }
  };

  const handleUpload = async () => {
    if (!file) {
      alert('Lütfen bir dosya seçin');
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await api.post('/customers/bulk-import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setImportResult(response.data);
      setShowResults(true);
      
      if (response.data.successful_imports > 0) {
        onSuccess();
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert('Yükleme hatası: ' + (error.response?.data?.detail || 'Bilinmeyen hata'));
    } finally {
      setUploading(false);
    }
  };

  const downloadTemplate = async () => {
    try {
      const response = await api.get('/customers/bulk-import/template');
      
      // Convert hex string back to binary
      const hexString = response.data.content;
      const bytes = new Uint8Array(hexString.match(/.{1,2}/g).map(byte => parseInt(byte, 16)));
      
      // Create blob and download
      const blob = new Blob([bytes], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'musteri_listesi_template.xlsx';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
    } catch (error) {
      console.error('Template download error:', error);
      alert('Template indirme hatası: ' + (error.response?.data?.detail || 'Bilinmeyen hata'));
    }
  };

  const resetForm = () => {
    setFile(null);
    setImportResult(null);
    setShowResults(false);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto m-4">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-900">Toplu Müşteri İçe Aktarımı</h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
        </div>

        <div className="p-6">
          {!showResults ? (
            <div className="space-y-6">
              {/* Instructions */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-medium text-blue-900 mb-2">Kullanım Talimatları:</h3>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>• Excel dosyasında 12 sütun bulunmalıdır</li>
                  <li>• Sütun sırası: Muayene Alanı, Muayene Alt Alanı, Muayene Türü, Referans, Muayene Tarihi, Zorunlu/Gönüllü Alan, Müşteri Adı, Müşteri Adresi, Denetçi Adı, Denetçi Lokasyonu, Rapor Onay Tarihi, Rapor Onaylayan</li>
                  <li>• Müşteri Adı ve Müşteri Adresi zorunludur</li>
                  <li>• Boş alanlar "-" işareti ile belirtilebilir</li>
                  <li>• Mevcut müşteriler güncellenecek, yenileri eklenecek</li>
                </ul>
              </div>

              {/* Template Download */}
              <div className="text-center">
                <p className="text-gray-600 mb-4">Önce template dosyasını indirip örnek formatı inceleyin:</p>
                <button
                  onClick={downloadTemplate}
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                >
                  📥 Template İndir
                </button>
              </div>

              <div className="border-t border-gray-200 pt-6">
                {/* File Upload */}
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Excel Dosyası Seçin (.xlsx, .xls, .csv)
                    </label>
                    <input
                      type="file"
                      accept=".xlsx,.xls,.csv"
                      onChange={handleFileSelect}
                      className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-red-50 file:text-red-700 hover:file:bg-red-100"
                    />
                  </div>

                  {file && (
                    <div className="text-sm text-gray-600">
                      Seçilen dosya: <span className="font-medium">{file.name}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Upload Button */}
              <div className="flex justify-end space-x-3">
                <button
                  onClick={onClose}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
                >
                  İptal
                </button>
                <button
                  onClick={handleUpload}
                  disabled={!file || uploading}
                  className="px-6 py-2 bg-red-900 text-white rounded-md hover:bg-red-800 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {uploading ? 'Yükleniyor...' : 'Dosyayı Yükle'}
                </button>
              </div>
            </div>
          ) : (
            /* Results Display */
            <div className="space-y-6">
              <div className="text-center">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">İçe Aktarım Sonuçları</h3>
                
                <div className="grid grid-cols-3 gap-4 mb-6">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">{importResult.total_rows}</div>
                    <div className="text-sm text-blue-800">Toplam Satır</div>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">{importResult.successful_imports}</div>
                    <div className="text-sm text-green-800">Başarılı</div>
                  </div>
                  <div className="bg-red-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-red-600">{importResult.failed_imports}</div>
                    <div className="text-sm text-red-800">Başarısız</div>
                  </div>
                </div>
              </div>

              {/* Warnings */}
              {importResult.warnings && importResult.warnings.length > 0 && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <h4 className="font-medium text-yellow-900 mb-2">Uyarılar:</h4>
                  <ul className="text-sm text-yellow-800 space-y-1">
                    {importResult.warnings.map((warning, index) => (
                      <li key={index}>• {warning}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Errors */}
              {importResult.errors && importResult.errors.length > 0 && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <h4 className="font-medium text-red-900 mb-2">Hatalar:</h4>
                  <div className="text-sm text-red-800 space-y-2 max-h-40 overflow-y-auto">
                    {importResult.errors.map((error, index) => (
                      <div key={index} className="border-b border-red-200 pb-2 last:border-b-0">
                        <strong>Satır {error.row}:</strong> {error.error}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex justify-end space-x-3">
                <button
                  onClick={resetForm}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
                >
                  Yeni Import
                </button>
                <button
                  onClick={onClose}
                  className="px-6 py-2 bg-red-900 text-white rounded-md hover:bg-red-800"
                >
                  Kapat
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const CustomerManagement = ({ onBack }) => {
  const [customers, setCustomers] = useState([]);
  const [equipmentTemplates, setEquipmentTemplates] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [showBulkImport, setShowBulkImport] = useState(false);
  const [editingCustomer, setEditingCustomer] = useState(null);
  const [loading, setLoading] = useState(true);
  const [formData, setFormData] = useState({
    company_name: '',
    contact_person: '',
    phone: '',
    email: '',
    address: '',
    equipments: []
  });

  useEffect(() => {
    fetchCustomers();
    fetchEquipmentTemplates();
  }, []);

  const fetchCustomers = async () => {
    try {
      const response = await api.get('/customers');
      setCustomers(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Customers error:', error);
      setLoading(false);
    }
  };

  const fetchEquipmentTemplates = async () => {
    try {
      const response = await api.get('/equipment-templates');
      setEquipmentTemplates(response.data);
    } catch (error) {
      console.error('Templates error:', error);
    }
  };

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleEquipmentChange = (templateId, isChecked) => {
    const template = equipmentTemplates.find(t => t.id === templateId);
    if (!template) return;

    setFormData(prev => ({
      ...prev,
      equipments: isChecked 
        ? [...prev.equipments, {
            template_id: templateId,
            equipment_type: template.equipment_type,
            description: template.description,
            serial_number: '',
            capacity: '',
            manufacturing_year: ''
          }]
        : prev.equipments.filter(eq => eq.template_id !== templateId)
    }));
  };

  const handleEquipmentDetailChange = (templateId, field, value) => {
    setFormData(prev => ({
      ...prev,
      equipments: prev.equipments.map(eq => 
        eq.template_id === templateId 
          ? { ...eq, [field]: value }
          : eq
      )
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingCustomer) {
        await api.put(`/customers/${editingCustomer.id}`, formData);
      } else {
        await api.post('/customers', formData);
      }
      
      setShowForm(false);
      setEditingCustomer(null);
      setFormData({
        company_name: '',
        contact_person: '',
        phone: '',
        email: '',
        address: '',
        equipments: []
      });
      fetchCustomers();
    } catch (error) {
      console.error('Save error:', error);
      alert('Kaydetme hatası: ' + (error.response?.data?.detail || 'Bilinmeyen hata'));
    }
  };

  const handleEdit = (customer) => {
    setEditingCustomer(customer);
    setFormData({
      company_name: customer.company_name,
      contact_person: customer.contact_person,
      phone: customer.phone,
      email: customer.email,
      address: customer.address,
      equipments: customer.equipments || []
    });
    setShowForm(true);
  };

  const handleDelete = async (customerId) => {
    if (!window.confirm('Bu müşteriyi silmek istediğinizden emin misiniz?')) return;
    
    try {
      await api.delete(`/customers/${customerId}`);
      fetchCustomers();
    } catch (error) {
      console.error('Delete error:', error);
      alert('Silme hatası: ' + (error.response?.data?.detail || 'Bilinmeyen hata'));
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <img 
            src="https://customer-assets.emergentagent.com/job_yeni-yazilim/artifacts/7675i2kn_WhatsApp%20G%C3%B6rsel%202025-08-04%20saat%2012.57.00_7b510c6c.jpg"
            alt="RoyalCert Logo"
            className="w-16 h-16 object-contain mx-auto mb-4"
          />
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-900 mx-auto mb-4"></div>
          <p className="text-royal-600">Müşteriler yükleniyor...</p>
        </div>
      </div>
    );
  }

  // Customer Form
  if (showForm) {
    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-gray-900">
            {editingCustomer ? 'Müşteri Düzenle' : 'Yeni Müşteri Ekle'}
          </h1>
          <button
            onClick={() => {
              setShowForm(false);
              setEditingCustomer(null);
            }}
            className="px-4 py-2 text-gray-600 hover:text-gray-800"
          >
            ← Geri Dön
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Customer Basic Info */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Müşteri Bilgileri</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Firma Adı *
                </label>
                <input
                  type="text"
                  value={formData.company_name}
                  onChange={(e) => handleInputChange('company_name', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-900 focus:border-transparent"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  İletişim Kişisi *
                </label>
                <input
                  type="text"
                  value={formData.contact_person}
                  onChange={(e) => handleInputChange('contact_person', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-900 focus:border-transparent"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Telefon *
                </label>
                <input
                  type="tel"
                  value={formData.phone}
                  onChange={(e) => handleInputChange('phone', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-900 focus:border-transparent"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  E-posta *
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleInputChange('email', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-900 focus:border-transparent"
                  required
                />
              </div>
            </div>
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Adres *
              </label>
              <textarea
                value={formData.address}
                onChange={(e) => handleInputChange('address', e.target.value)}
                rows="2"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-900 focus:border-transparent"
                required
              />
            </div>
          </div>

          {/* Equipment Selection */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Ekipman Seçimi</h2>
            <div className="space-y-4">
              {equipmentTemplates.map((template) => {
                const isSelected = formData.equipments.some(eq => eq.template_id === template.id);
                const selectedEquipment = formData.equipments.find(eq => eq.template_id === template.id);
                
                return (
                  <div key={template.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center mb-3">
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={(e) => handleEquipmentChange(template.id, e.target.checked)}
                        className="mr-3"
                      />
                      <div>
                        <h3 className="font-medium text-gray-900">{template.equipment_type}</h3>
                        <p className="text-sm text-gray-500">{template.description}</p>
                      </div>
                    </div>
                    
                    {isSelected && (
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 ml-6 pt-3 border-t border-gray-100">
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">
                            Seri Numarası
                          </label>
                          <input
                            type="text"
                            value={selectedEquipment?.serial_number || ''}
                            onChange={(e) => handleEquipmentDetailChange(template.id, 'serial_number', e.target.value)}
                            className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-red-900"
                            placeholder="Seri numarası"
                          />
                        </div>
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">
                            Kapasite
                          </label>
                          <input
                            type="text"
                            value={selectedEquipment?.capacity || ''}
                            onChange={(e) => handleEquipmentDetailChange(template.id, 'capacity', e.target.value)}
                            className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-red-900"
                            placeholder="Kapasite"
                          />
                        </div>
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">
                            İmalat Yılı
                          </label>
                          <input
                            type="text"
                            value={selectedEquipment?.manufacturing_year || ''}
                            onChange={(e) => handleEquipmentDetailChange(template.id, 'manufacturing_year', e.target.value)}
                            className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:ring-1 focus:ring-red-900"
                            placeholder="İmalat yılı"
                          />
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-end space-x-4">
            <button
              type="button"
              onClick={() => {
                setShowForm(false);
                setEditingCustomer(null);
              }}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            >
              İptal
            </button>
            <button
              type="submit"
              className="px-6 py-2 bg-red-900 text-white rounded-md hover:bg-red-800"
            >
              {editingCustomer ? 'Güncelle' : 'Müşteri Ekle'}
            </button>
          </div>
        </form>
      </div>
    );
  }

  // Customer List
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Müşteri Yönetimi</h1>
        <div className="space-x-3">
          <button
            onClick={() => setShowForm(true)}
            className="px-4 py-2 bg-red-900 text-white rounded-md hover:bg-red-800"
          >
            Yeni Müşteri Ekle
          </button>
          <button
            onClick={() => setShowBulkImport(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Toplu İçe Aktar
          </button>
          <button
            onClick={onBack}
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
          >
            Dashboard'a Dön
          </button>
        </div>
      </div>

      {/* Bulk Import Modal */}
      {showBulkImport && <BulkImportModal onClose={() => setShowBulkImport(false)} onSuccess={fetchCustomers} />}

      {/* Customers Table */}
      <div className="bg-white rounded-xl shadow-sm">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">
            Müşteriler ({customers.length})
          </h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Firma</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">İletişim Kişisi</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Telefon</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ekipman Sayısı</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Kayıt Tarihi</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">İşlemler</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {customers.map((customer) => (
                <tr key={customer.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{customer.company_name}</div>
                    <div className="text-sm text-gray-500">{customer.email}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {customer.contact_person}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {customer.phone}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {customer.equipments?.length || 0} ekipman
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(customer.created_at).toLocaleDateString('tr-TR')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                    <button
                      onClick={() => handleEdit(customer)}
                      className="text-indigo-600 hover:text-indigo-900"
                    >
                      Düzenle
                    </button>
                    <button
                      onClick={() => handleDelete(customer.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      Sil
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {customers.length === 0 && (
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">Henüz müşteri yok</h3>
            <p className="mt-1 text-sm text-gray-500">İlk müşteriyi eklemek için yukarıdaki butonu kullanın.</p>
          </div>
        )}
      </div>
    </div>
  );
};

// Inspection Planning Component - Phase 5.1
const InspectionPlanning = ({ onBack }) => {
  const [customers, setCustomers] = useState([]);
  const [inspectors, setInspectors] = useState([]);
  const [inspections, setInspections] = useState([]);
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [showCreateInspection, setShowCreateInspection] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [customersRes, usersRes, inspectionsRes] = await Promise.all([
        api.get('/customers'),
        api.get('/users'),
        api.get('/inspections')
      ]);
      
      setCustomers(customersRes.data);
      setInspectors(usersRes.data.filter(user => user.role === 'denetci'));
      setInspections(inspectionsRes.data);
      setLoading(false);
    } catch (error) {
      console.error('Data loading error:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <img 
            src="https://customer-assets.emergentagent.com/job_yeni-yazilim/artifacts/7675i2kn_WhatsApp%20G%C3%B6rsel%202025-08-04%20saat%2012.57.00_7b510c6c.jpg"
            alt="RoyalCert Logo"
            className="w-16 h-16 object-contain mx-auto mb-4"
          />
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-900 mx-auto mb-4"></div>
          <p className="text-royal-600">Denetim planlama verileri yükleniyor...</p>
        </div>
      </div>
    );
  }

  // Show Create Inspection Form
  if (showCreateInspection) {
    return (
      <CreateInspectionForm 
        customers={customers}
        inspectors={inspectors}
        onBack={() => setShowCreateInspection(false)}
        onSuccess={() => {
          setShowCreateInspection(false);
          fetchData();
        }}
      />
    );
  }

  // Calculate statistics
  const stats = {
    totalCustomers: customers.length,
    totalEquipments: customers.reduce((total, customer) => total + (customer.equipments?.length || 0), 0),
    totalInspectors: inspectors.length,
    availableInspectors: inspectors.filter(inspector => inspector.is_active).length,
    pendingInspections: inspections.filter(inspection => inspection.status === 'beklemede').length,
    activeInspections: inspections.filter(inspection => inspection.status === 'devam_ediyor').length,
    completedInspections: inspections.filter(inspection => ['onaylandi', 'rapor_yazildi'].includes(inspection.status)).length,
    totalInspections: inspections.length
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Denetim Planlama Sistemi</h1>
        <div className="space-x-3">
          <button
            onClick={() => setShowCreateInspection(true)}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            + Yeni Denetim Planla
          </button>
          <button
            onClick={onBack}
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
          >
            ← Geri Dön
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('overview')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'overview'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Genel Bakış
          </button>
          <button
            onClick={() => setActiveTab('planning')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'planning'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Planlama Dashboard
          </button>
          <button
            onClick={() => setActiveTab('tracking')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'tracking'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Denetim Takip
          </button>
        </nav>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatCard
              title="Toplam Müşteri"
              value={stats.totalCustomers}
              color="bg-blue-100"
              icon={<svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>}
            />
            <StatCard
              title="Toplam Ekipman"
              value={stats.totalEquipments}
              color="bg-green-100"
              icon={<svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>}
            />
            <StatCard
              title="Aktif Denetçi"
              value={stats.availableInspectors}
              color="bg-purple-100"
              icon={<svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>}
            />
            <StatCard
              title="Bekleyen Denetim"
              value={stats.pendingInspections}
              color="bg-yellow-100"
              icon={<svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>}
            />
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Hızlı İşlemler</h3>
              <div className="space-y-3">
                <button
                  onClick={() => setShowCreateInspection(true)}
                  className="w-full flex items-center px-4 py-3 bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100"
                >
                  <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                  </svg>
                  Yeni Denetim Planla
                </button>
                <button
                  onClick={() => setActiveTab('tracking')}
                  className="w-full flex items-center px-4 py-3 bg-green-50 text-green-700 rounded-lg hover:bg-green-100"
                >
                  <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                  </svg>
                  Denetimleri Takip Et
                </button>
              </div>
            </div>

            <div className="bg-white rounded-xl shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Denetçi Durumu</h3>
              <div className="space-y-3">
                {inspectors.slice(0, 3).map((inspector) => (
                  <div key={inspector.id} className="flex items-center justify-between">
                    <div className="flex items-center">
                      <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center mr-3">
                        <svg className="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                        </svg>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">{inspector.full_name}</p>
                        <p className="text-xs text-gray-500">{inspector.email}</p>
                      </div>
                    </div>
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      inspector.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {inspector.is_active ? 'Aktif' : 'Pasif'}
                    </span>
                  </div>
                ))}
                {inspectors.length === 0 && (
                  <p className="text-sm text-gray-500">Henüz denetçi kaydedilmemiş</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Planning Dashboard Tab */}
      {activeTab === 'planning' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Customer-Equipment List */}
            <div className="bg-white rounded-xl shadow-sm">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Müşteri-Ekipman Kombinasyonları</h3>
              </div>
              <div className="p-6">
                <div className="space-y-4 max-h-96 overflow-y-auto">
                  {customers.map((customer) => (
                    <div key={customer.id} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium text-gray-900">{customer.company_name}</h4>
                        <span className="text-sm text-gray-500">{customer.equipments?.length || 0} ekipman</span>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{customer.contact_person} • {customer.phone}</p>
                      
                      {customer.equipments && customer.equipments.length > 0 ? (
                        <div className="space-y-2">
                          {customer.equipments.map((equipment, index) => (
                            <div key={index} className="flex items-center justify-between bg-gray-50 rounded p-2">
                              <div className="text-sm">
                                <span className="font-medium">{equipment.equipment_type || equipment.muayene_alt_alani || 'Bilinmeyen Ekipman'}</span>
                                {equipment.serial_number && <span className="text-gray-500 ml-2">SN: {equipment.serial_number}</span>}
                              </div>
                              <button
                                onClick={() => {
                                  // Set selected customer and equipment for planning
                                  console.log('Plan inspection for:', customer.company_name, equipment);
                                  setShowCreateInspection(true);
                                }}
                                className="px-3 py-1 bg-blue-600 text-white text-xs rounded hover:bg-blue-700"
                              >
                                Denetim Planla
                              </button>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <p className="text-sm text-gray-500 italic">Ekipman bilgisi yok</p>
                      )}
                    </div>
                  ))}
                  {customers.length === 0 && (
                    <div className="text-center py-8">
                      <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 515.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 919.288 0M15 7a3 3 0 11-6 0 3 3 0 616 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                      </svg>
                      <h3 className="mt-2 text-sm font-medium text-gray-900">Müşteri bulunamadı</h3>
                      <p className="mt-1 text-sm text-gray-500">Önce müşteri ekleyip ekipman bilgilerini tanımlayın.</p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Inspector Availability */}
            <div className="bg-white rounded-xl shadow-sm">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Denetçi Listesi ve Müsaitlik</h3>
              </div>
              <div className="p-6">
                <div className="space-y-4">
                  {inspectors.map((inspector) => {
                    const inspectorInspections = inspections.filter(
                      inspection => inspection.inspector_id === inspector.id && 
                      ['beklemede', 'devam_ediyor'].includes(inspection.status)
                    );
                    
                    return (
                      <div key={inspector.id} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center">
                            <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center mr-3">
                              <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                              </svg>
                            </div>
                            <div>
                              <h4 className="font-medium text-gray-900">{inspector.full_name}</h4>
                              <p className="text-sm text-gray-500">{inspector.email}</p>
                            </div>
                          </div>
                          <div className="text-right">
                            <span className={`inline-block px-2 py-1 text-xs rounded-full mb-1 ${
                              inspector.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                            }`}>
                              {inspector.is_active ? 'Aktif' : 'Pasif'}
                            </span>
                            <p className="text-sm text-gray-600">{inspectorInspections.length} aktif denetim</p>
                          </div>
                        </div>
                        
                        {inspectorInspections.length > 0 && (
                          <div className="bg-gray-50 rounded p-2 mt-2">
                            <p className="text-xs text-gray-600 font-medium mb-1">Mevcut Denetimler:</p>
                            {inspectorInspections.slice(0, 2).map((inspection) => (
                              <div key={inspection.id} className="text-xs text-gray-600">
                                • {inspection.equipment_info?.equipment_type || 'Ekipman'} - {new Date(inspection.planned_date).toLocaleDateString('tr-TR')}
                              </div>
                            ))}
                            {inspectorInspections.length > 2 && (
                              <p className="text-xs text-gray-500">+{inspectorInspections.length - 2} diğer</p>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                  
                  {inspectors.length === 0 && (
                    <div className="text-center py-8">
                      <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                      </svg>
                      <h3 className="mt-2 text-sm font-medium text-gray-900">Denetçi bulunamadı</h3>
                      <p className="mt-1 text-sm text-gray-500">Admin panelinden denetçi kullanıcısı ekleyin.</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tracking Tab */}
      {activeTab === 'tracking' && (
        <InspectionTracking inspections={inspections} customers={customers} inspectors={inspectors} onRefresh={fetchData} />
      )}
    </div>
  );
};

// Create Inspection Form Component - Phase 5.2
const CreateInspectionForm = ({ customers, inspectors, onBack, onSuccess }) => {
  const [selectedCustomer, setSelectedCustomer] = useState('');
  const [selectedEquipment, setSelectedEquipment] = useState('');
  const [selectedInspector, setSelectedInspector] = useState('');
  const [inspectionDate, setInspectionDate] = useState('');
  const [inspectionType, setInspectionType] = useState('PERİYODİK');
  const [notes, setNotes] = useState('');
  const [saving, setSaving] = useState(false);

  const selectedCustomerData = customers.find(c => c.id === selectedCustomer);
  const availableEquipments = selectedCustomerData?.equipments || [];

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedCustomer || !selectedInspector || !inspectionDate) {
      alert('Lütfen zorunlu alanları doldurun');
      return;
    }

    setSaving(true);
    try {
      const equipmentData = availableEquipments.find((_, index) => index.toString() === selectedEquipment) || {};
      
      const inspectionData = {
        customer_id: selectedCustomer,
        inspector_id: selectedInspector,
        planned_date: new Date(inspectionDate).toISOString(),
        equipment_info: {
          equipment_type: equipmentData.equipment_type || equipmentData.muayene_alt_alani || 'Genel Ekipman',
          serial_number: equipmentData.serial_number || '',
          capacity: equipmentData.capacity || '',
          manufacturing_year: equipmentData.manufacturing_year || '',
          inspection_type: inspectionType,
          notes: notes
        }
      };

      await api.post('/inspections', inspectionData);
      alert('Denetim başarıyla planlandı!');
      onSuccess();
    } catch (error) {
      console.error('Inspection creation error:', error);
      alert('Denetim planlama hatası: ' + (error.response?.data?.detail || 'Bilinmeyen hata'));
    } finally {
      setSaving(false);
    }
  };

  // Get today's date for min date
  const today = new Date().toISOString().split('T')[0];

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Yeni Denetim Planla</h1>
        <button
          onClick={onBack}
          className="px-4 py-2 text-gray-600 hover:text-gray-800"
        >
          ← Geri Dön
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Denetim Detayları</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Customer Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Müşteri Seçimi *
              </label>
              <select
                value={selectedCustomer}
                onChange={(e) => {
                  setSelectedCustomer(e.target.value);
                  setSelectedEquipment(''); // Reset equipment selection
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-600 focus:border-transparent"
                required
              >
                <option value="">Müşteri seçin...</option>
                {customers.map((customer) => (
                  <option key={customer.id} value={customer.id}>
                    {customer.company_name} ({customer.contact_person})
                  </option>
                ))}
              </select>
            </div>

            {/* Equipment Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Ekipman Seçimi
              </label>
              <select
                value={selectedEquipment}
                onChange={(e) => setSelectedEquipment(e.target.value)}
                disabled={!selectedCustomer}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-600 focus:border-transparent disabled:bg-gray-100"
              >
                <option value="">Ekipman seçin...</option>
                {availableEquipments.map((equipment, index) => (
                  <option key={index} value={index.toString()}>
                    {equipment.equipment_type || equipment.muayene_alt_alani || 'Bilinmeyen Ekipman'}
                    {equipment.serial_number && ` (SN: ${equipment.serial_number})`}
                  </option>
                ))}
              </select>
              {selectedCustomer && availableEquipments.length === 0 && (
                <p className="text-sm text-gray-500 mt-1">Bu müşteri için kayıtlı ekipman bulunmuyor</p>
              )}
            </div>

            {/* Inspector Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Denetçi Atama *
              </label>
              <select
                value={selectedInspector}
                onChange={(e) => setSelectedInspector(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-600 focus:border-transparent"
                required
              >
                <option value="">Denetçi seçin...</option>
                {inspectors.filter(inspector => inspector.is_active).map((inspector) => (
                  <option key={inspector.id} value={inspector.id}>
                    {inspector.full_name} ({inspector.email})
                  </option>
                ))}
              </select>
            </div>

            {/* Inspection Date */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Denetim Tarihi *
              </label>
              <input
                type="date"
                value={inspectionDate}
                onChange={(e) => setInspectionDate(e.target.value)}
                min={today}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-600 focus:border-transparent"
                required
              />
            </div>

            {/* Inspection Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Denetim Türü
              </label>
              <select
                value={inspectionType}
                onChange={(e) => setInspectionType(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-600 focus:border-transparent"
              >
                <option value="İLK MONTAJ">İlk Montaj</option>
                <option value="PERİYODİK">Periyodik</option>
                <option value="TAKİP">Takip</option>
              </select>
            </div>
          </div>

          {/* Notes */}
          <div className="mt-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Notlar
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows="3"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-600 focus:border-transparent"
              placeholder="Denetim ile ilgili ek notlar..."
            />
          </div>

          {/* Selected Equipment Details */}
          {selectedEquipment && availableEquipments[parseInt(selectedEquipment)] && (
            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <h3 className="font-medium text-blue-900 mb-2">Seçilen Ekipman Detayları</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium text-blue-800">Tip:</span>
                  <span className="ml-2 text-blue-700">
                    {availableEquipments[parseInt(selectedEquipment)].equipment_type || 
                     availableEquipments[parseInt(selectedEquipment)].muayene_alt_alani || 
                     'Belirtilmemiş'}
                  </span>
                </div>
                {availableEquipments[parseInt(selectedEquipment)].serial_number && (
                  <div>
                    <span className="font-medium text-blue-800">Seri No:</span>
                    <span className="ml-2 text-blue-700">{availableEquipments[parseInt(selectedEquipment)].serial_number}</span>
                  </div>
                )}
                {availableEquipments[parseInt(selectedEquipment)].capacity && (
                  <div>
                    <span className="font-medium text-blue-800">Kapasite:</span>
                    <span className="ml-2 text-blue-700">{availableEquipments[parseInt(selectedEquipment)].capacity}</span>
                  </div>
                )}
                {availableEquipments[parseInt(selectedEquipment)].manufacturing_year && (
                  <div>
                    <span className="font-medium text-blue-800">İmalat Yılı:</span>
                    <span className="ml-2 text-blue-700">{availableEquipments[parseInt(selectedEquipment)].manufacturing_year}</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Submit Button */}
        <div className="flex justify-end space-x-4">
          <button
            type="button"
            onClick={onBack}
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
          >
            İptal
          </button>
          <button
            type="submit"
            disabled={saving}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {saving ? 'Planlanıyor...' : 'Denetimi Planla'}
          </button>
        </div>
      </form>
    </div>
  );
};

// Inspection Tracking Component - Phase 5.3
const InspectionTracking = ({ inspections, customers, inspectors, onRefresh }) => {
  const [filter, setFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('planned_date');

  // Get customer name by id
  const getCustomerName = (customerId) => {
    const customer = customers.find(c => c.id === customerId);
    return customer ? customer.company_name : 'Bilinmeyen Müşteri';
  };

  // Get inspector name by id
  const getInspectorName = (inspectorId) => {
    const inspector = inspectors.find(i => i.id === inspectorId);
    return inspector ? inspector.full_name : 'Bilinmeyen Denetçi';
  };

  // Filter and sort inspections
  const filteredInspections = inspections
    .filter(inspection => {
      if (filter !== 'all' && inspection.status !== filter) return false;
      if (searchTerm) {
        const customerName = getCustomerName(inspection.customer_id).toLowerCase();
        const inspectorName = getInspectorName(inspection.inspector_id).toLowerCase();
        const searchLower = searchTerm.toLowerCase();
        return customerName.includes(searchLower) || inspectorName.includes(searchLower);
      }
      return true;
    })
    .sort((a, b) => {
      if (sortBy === 'planned_date') {
        return new Date(a.planned_date) - new Date(b.planned_date);
      }
      return 0;
    });

  // Get overdue inspections (planned date is in the past and status is still beklemede or devam_ediyor)
  const overdueInspections = inspections.filter(inspection => {
    const plannedDate = new Date(inspection.planned_date);
    const today = new Date();
    return plannedDate < today && ['beklemede', 'devam_ediyor'].includes(inspection.status);
  });

  const getStatusColor = (status) => {
    switch (status) {
      case 'beklemede': return 'bg-yellow-100 text-yellow-800';
      case 'devam_ediyor': return 'bg-blue-100 text-blue-800';
      case 'rapor_yazildi': return 'bg-green-100 text-green-800';
      case 'onaylandi': return 'bg-emerald-100 text-emerald-800';
      case 'reddedildi': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'beklemede': return 'Beklemede';
      case 'devam_ediyor': return 'Devam Ediyor';
      case 'rapor_yazildi': return 'Rapor Yazıldı';
      case 'onaylandi': return 'Onaylandı';
      case 'reddedildi': return 'Reddedildi';
      default: return 'Bilinmeyen';
    }
  };

  const isOverdue = (inspection) => {
    const plannedDate = new Date(inspection.planned_date);
    const today = new Date();
    return plannedDate < today && ['beklemede', 'devam_ediyor'].includes(inspection.status);
  };

  return (
    <div className="space-y-6">
      {/* Overdue Warning */}
      {overdueInspections.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <svg className="w-5 h-5 text-red-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
            </svg>
            <h3 className="text-red-800 font-medium">
              Gecikmeli Denetim Uyarısı: {overdueInspections.length} adet denetim süresi geçmiş
            </h3>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Durum Filtresi</label>
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-600 focus:border-transparent"
            >
              <option value="all">Tümü</option>
              <option value="beklemede">Beklemede</option>
              <option value="devam_ediyor">Devam Eden</option>
              <option value="rapor_yazildi">Rapor Yazıldı</option>
              <option value="onaylandi">Onaylandı</option>
              <option value="reddedildi">Reddedildi</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Arama</label>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Müşteri veya denetçi ara..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-600 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Sıralama</label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-600 focus:border-transparent"
            >
              <option value="planned_date">Planlanan Tarihe Göre</option>
              <option value="created_at">Oluşturma Tarihine Göre</option>
            </select>
          </div>
        </div>
      </div>

      {/* Inspections List */}
      <div className="bg-white rounded-xl shadow-sm">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold text-gray-900">
              Denetimler ({filteredInspections.length})
            </h3>
            <button
              onClick={onRefresh}
              className="px-3 py-2 text-blue-600 hover:text-blue-800"
            >
              🔄 Yenile
            </button>
          </div>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Müşteri</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ekipman</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Denetçi</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Planlanan Tarih</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Durum</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">İşlemler</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredInspections.map((inspection) => (
                <tr key={inspection.id} className={isOverdue(inspection) ? 'bg-red-50' : ''}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {getCustomerName(inspection.customer_id)}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {inspection.equipment_info?.equipment_type || 'Genel Ekipman'}
                    </div>
                    {inspection.equipment_info?.serial_number && (
                      <div className="text-sm text-gray-500">SN: {inspection.equipment_info.serial_number}</div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {getInspectorName(inspection.inspector_id)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {new Date(inspection.planned_date).toLocaleDateString('tr-TR')}
                    {isOverdue(inspection) && (
                      <div className="text-xs text-red-600 font-medium">Süre Geçmiş</div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(inspection.status)}`}>
                      {getStatusText(inspection.status)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button className="text-blue-600 hover:text-blue-900 mr-3">Görüntüle</button>
                    <button className="text-indigo-600 hover:text-indigo-900">Düzenle</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredInspections.length === 0 && (
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">Denetim bulunamadı</h3>
            <p className="mt-1 text-sm text-gray-500">
              {filter === 'all' ? 'Henüz denetim planlanmamış' : 'Bu filtreye uygun denetim bulunamadı'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

const PlanlamaDashboard = () => {
  const [stats, setStats] = useState({});
  const [customers, setCustomers] = useState([]);
  const [showCustomerManagement, setShowCustomerManagement] = useState(false);

  useEffect(() => {
    fetchStats();
    fetchCustomers();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await api.get('/dashboard/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Stats error:', error);
    }
  };

  const fetchCustomers = async () => {
    try {
      const response = await api.get('/customers');
      setCustomers(response.data);
    } catch (error) {
      console.error('Customers error:', error);
    }
  };

  // Show Customer Management
  if (showCustomerManagement) {
    return (
      <CustomerManagement 
        onBack={() => {
          setShowCustomerManagement(false);
          fetchStats();
          fetchCustomers();
        }} 
      />
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Planlama Dashboard</h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard
          title="Toplam Müşteri"
          value={stats.total_customers || 0}
          color="bg-blue-100"
          icon={<svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>}
        />
        <StatCard
          title="Bekleyen Denetimler"
          value={stats.pending_inspections || 0}
          color="bg-yellow-100"
          icon={<svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>}
        />
        <StatCard
          title="Tamamlanan"
          value={stats.completed_inspections || 0}
          color="bg-green-100"
          icon={<svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>}
        />
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-500">Hızlı İşlem</p>
              <button
                onClick={() => setShowCustomerManagement(true)}
                className="mt-2 px-4 py-2 bg-red-900 text-white text-sm rounded-md hover:bg-red-800 focus:outline-none focus:ring-2 focus:ring-red-900"
              >
                Müşteri Yönetimi
              </button>
            </div>
            <div className="flex-shrink-0 p-3 rounded-lg bg-red-100">
              <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 515.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 919.288 0M15 7a3 3 0 11-6 0 3 3 0 616 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Customers */}
      <div className="bg-white rounded-xl shadow-sm">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h2 className="text-lg font-semibold text-gray-900">Son Eklenen Müşteriler</h2>
            <button
              onClick={() => setShowCustomerManagement(true)}
              className="text-red-900 hover:text-red-700 text-sm font-medium"
            >
              Tümünü Görüntüle →
            </button>
          </div>
        </div>
        <div className="p-6">
          {customers.length === 0 ? (
            <div className="text-center py-8">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 515.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 919.288 0M15 7a3 3 0 11-6 0 3 3 0 616 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">Henüz müşteri eklenmemiş</h3>
              <p className="mt-1 text-sm text-gray-500">İlk müşteriyi eklemek için müşteri yönetimi sayfasına gidin.</p>
              <button
                onClick={() => setShowCustomerManagement(true)}
                className="mt-4 px-4 py-2 bg-red-900 text-white text-sm rounded-md hover:bg-red-800"
              >
                Müşteri Ekle
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              {customers.slice(0, 5).map((customer) => (
                <div key={customer.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                  <div className="flex items-center">
                    <div className="flex-shrink-0 h-10 w-10 bg-red-100 rounded-full flex items-center justify-center">
                      <svg className="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                      </svg>
                    </div>
                    <div className="ml-4">
                      <h3 className="font-medium text-gray-900">{customer.company_name}</h3>
                      <p className="text-sm text-gray-500">{customer.contact_person} • {customer.phone}</p>
                    </div>
                  </div>
                  <div className="text-sm text-gray-500">
                    <span className="inline-flex px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
                      {customer.equipments?.length || 0} ekipman
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const DynamicInspectionForm = ({ inspectionId, onBack, onSave }) => {
  const [formData, setFormData] = useState(null);
  const [formResults, setFormResults] = useState({});
  const [generalInfo, setGeneralInfo] = useState({});
  const [equipmentInfo, setEquipmentInfo] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchFormData();
  }, [inspectionId]);

  const fetchFormData = async () => {
    try {
      const response = await api.get(`/inspections/${inspectionId}/form`);
      const data = response.data;
      setFormData(data);
      
      // Initialize form results
      if (data.existing_data && data.existing_data.form_results) {
        const results = {};
        data.existing_data.form_results.forEach(result => {
          results[result.item_id] = {
            value: result.value,
            comment: result.comment || ''
          };
        });
        setFormResults(results);
      }
      
      // Set general and equipment info
      setGeneralInfo(data.existing_data?.general_info || {});
      setEquipmentInfo(data.existing_data?.equipment_info || {});
      
      setLoading(false);
    } catch (error) {
      console.error('Form data error:', error);
      setLoading(false);
    }
  };

  const handleResultChange = (itemId, field, value) => {
    setFormResults(prev => ({
      ...prev,
      [itemId]: {
        ...prev[itemId],
        [field]: value
      }
    }));
  };

  const handleSave = async (isDraft = true) => {
    setSaving(true);
    try {
      // Convert form results to API format
      const apiFormResults = Object.entries(formResults).map(([itemId, data]) => ({
        item_id: parseInt(itemId),
        category: getItemCategory(parseInt(itemId)),
        value: data.value || '',
        comment: data.comment || null
      }));

      const formPayload = {
        general_info: {
          company_name: formData.customer.company_name,
          contact_person: formData.customer.contact_person,
          phone: formData.customer.phone,
          email: formData.customer.email,
          inspection_date: new Date(formData.inspection.planned_date).toISOString(),
          ...generalInfo
        },
        equipment_info: {
          equipment_type: formData.template.equipment_type,
          ...equipmentInfo
        },
        form_results: apiFormResults,
        defects: generalInfo.defects || null,
        notes: generalInfo.notes || null,
        conclusion: generalInfo.conclusion || null
      };

      await api.post(`/inspections/${inspectionId}/form`, formPayload);
      
      if (onSave) onSave();
      alert(isDraft ? 'Form kaydedildi!' : 'Form tamamlandı!');
    } catch (error) {
      console.error('Save error:', error);
      alert('Kaydetme hatası: ' + (error.response?.data?.detail || 'Bilinmeyen hata'));
    } finally {
      setSaving(false);
    }
  };

  const getItemCategory = (itemId) => {
    if (!formData?.template?.categories) return '';
    for (const category of formData.template.categories) {
      const item = category.items.find(item => item.id === itemId);
      if (item) return category.code;
    }
    return '';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <img 
            src="https://customer-assets.emergentagent.com/job_yeni-yazilim/artifacts/7675i2kn_WhatsApp%20G%C3%B6rsel%202025-08-04%20saat%2012.57.00_7b510c6c.jpg"
            alt="RoyalCert Logo"
            className="w-16 h-16 object-contain mx-auto mb-4"
          />
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-900 mx-auto mb-4"></div>
          <p className="text-royal-600">Form yükleniyor...</p>
        </div>
      </div>
    );
  }

  if (!formData) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Form verisi yüklenemedi.</p>
        <button
          onClick={onBack}
          className="mt-4 px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
        >
          Geri Dön
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {formData.template.equipment_type} Muayene Formu
            </h1>
            <p className="text-gray-600 mt-1">
              {formData.customer.company_name} - {formData.customer.contact_person}
            </p>
          </div>
          <button
            onClick={onBack}
            className="px-4 py-2 text-gray-600 hover:text-gray-800"
          >
            ← Geri Dön
          </button>
        </div>
      </div>

      {/* Form Categories */}
      {formData.template.categories.map((category, catIndex) => (
        <div key={category.code} className="bg-white rounded-xl shadow-sm">
          <div className="px-6 py-4 border-b border-gray-200 bg-red-50">
            <h2 className="text-lg font-semibold text-red-900">
              {category.code}. {category.name}
            </h2>
          </div>
          <div className="p-6">
            <div className="space-y-6">
              {category.items.map((item, itemIndex) => (
                <div key={item.id} className="border-b border-gray-100 pb-4 last:border-b-0">
                  <div className="flex items-start space-x-4">
                    <div className="flex-shrink-0 w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                      <span className="text-sm font-medium text-gray-600">{item.id}</span>
                    </div>
                    <div className="flex-1">
                      <p className="text-sm text-gray-900 mb-3">{item.text}</p>
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {/* Değerlendirme Dropdown */}
                        <div>
                          <label className="block text-xs font-medium text-gray-700 mb-1">
                            Değerlendirme {item.required && <span className="text-red-500">*</span>}
                          </label>
                          {item.input_type === 'dropdown' ? (
                            <select
                              value={formResults[item.id]?.value || ''}
                              onChange={(e) => handleResultChange(item.id, 'value', e.target.value)}
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-900 focus:border-transparent text-sm"
                            >
                              <option value="">Seçin...</option>
                              <option value="U">U - Uygun</option>
                              <option value="UD">UD - Uygun Değil</option>
                              <option value="U.Y">U.Y - Uygulaması Yok</option>
                            </select>
                          ) : (
                            <input
                              type="text"
                              value={formResults[item.id]?.value || ''}
                              onChange={(e) => handleResultChange(item.id, 'value', e.target.value)}
                              placeholder="Değer girin..."
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-900 focus:border-transparent text-sm"
                            />
                          )}
                        </div>
                        
                        {/* Yorum Alanı */}
                        {item.has_comment && (
                          <div>
                            <label className="block text-xs font-medium text-gray-700 mb-1">
                              Açıklama/Yorum
                            </label>
                            <textarea
                              value={formResults[item.id]?.comment || ''}
                              onChange={(e) => handleResultChange(item.id, 'comment', e.target.value)}
                              placeholder="Varsa açıklama yazın..."
                              rows="2"
                              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-900 focus:border-transparent text-sm resize-none"
                            />
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ))}

      {/* Additional Info Section */}
      <div className="bg-white rounded-xl shadow-sm">
        <div className="px-6 py-4 border-b border-gray-200 bg-yellow-50">
          <h2 className="text-lg font-semibold text-yellow-900">Ek Bilgiler</h2>
        </div>
        <div className="p-6 space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Kusur Açıklamaları
            </label>
            <textarea
              value={generalInfo.defects || ''}
              onChange={(e) => setGeneralInfo(prev => ({...prev, defects: e.target.value}))}
              rows="3"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-900 focus:border-transparent"
              placeholder="Tespit edilen kusurları detaylı olarak açıklayın..."
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Notlar
            </label>
            <textarea
              value={generalInfo.notes || ''}
              onChange={(e) => setGeneralInfo(prev => ({...prev, notes: e.target.value}))}
              rows="2"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-900 focus:border-transparent"
              placeholder="Ek notlar..."
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Sonuç ve Kanaat
            </label>
            <select
              value={generalInfo.conclusion || ''}
              onChange={(e) => setGeneralInfo(prev => ({...prev, conclusion: e.target.value}))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-900 focus:border-transparent"
            >
              <option value="">Sonuç seçin...</option>
              <option value="UYGUN">Ekipmanın kullanılması UYGUNDUR</option>
              <option value="SAKINCALI">Ekipmanın kullanılması SAKINCALIDIR</option>
            </select>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="flex justify-between items-center">
          <div className="text-sm text-gray-600">
            Form otomatik kaydedilmektedir
          </div>
          <div className="space-x-4">
            <button
              onClick={() => handleSave(true)}
              disabled={saving}
              className="px-6 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 disabled:opacity-50"
            >
              {saving ? 'Kaydediliyor...' : 'Taslak Kaydet'}
            </button>
            <button
              onClick={() => handleSave(false)}
              disabled={saving}
              className="px-6 py-2 bg-red-900 text-white rounded-md hover:bg-red-800 disabled:opacity-50"
            >
              {saving ? 'Tamamlanıyor...' : 'Formu Tamamla'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

const DenetciDashboard = () => {
  const [stats, setStats] = useState({});
  const [inspections, setInspections] = useState([]);
  const [selectedInspection, setSelectedInspection] = useState(null);
  const [showForm, setShowForm] = useState(false);

  useEffect(() => {
    fetchStats();
    fetchInspections();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await api.get('/dashboard/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Stats error:', error);
    }
  };

  const fetchInspections = async () => {
    try {
      const response = await api.get('/inspections');
      setInspections(response.data);
    } catch (error) {
      console.error('Inspections error:', error);
    }
  };

  const handleStatusUpdate = async (inspectionId, newStatus) => {
    try {
      await api.put(`/inspections/${inspectionId}`, { status: newStatus });
      fetchStats();
      fetchInspections();
    } catch (error) {
      console.error('Status update error:', error);
    }
  };

  const openInspectionForm = (inspection) => {
    setSelectedInspection(inspection);
    setShowForm(true);
  };

  const closeInspectionForm = () => {
    setShowForm(false);
    setSelectedInspection(null);
    fetchStats();
    fetchInspections();
  };

  // Show inspection form
  if (showForm && selectedInspection) {
    return (
      <DynamicInspectionForm 
        inspectionId={selectedInspection.id}
        onBack={closeInspectionForm}
        onSave={closeInspectionForm}
      />
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Denetçi Dashboard</h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard
          title="Toplam Denetimlerim"
          value={stats.my_inspections || 0}
          color="bg-blue-100"
          icon={<svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path></svg>}
        />
        <StatCard
          title="Bekleyen"
          value={stats.my_pending || 0}
          color="bg-yellow-100"
          icon={<svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>}
        />
        <StatCard
          title="Devam Eden"
          value={stats.my_in_progress || 0}
          color="bg-blue-100"
          icon={<svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>}
        />
        <StatCard
          title="Rapor Yazıldı"
          value={stats.my_completed || 0}
          color="bg-green-100"
          icon={<svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>}
        />
      </div>

      {/* My Inspections */}
      <div className="bg-white rounded-xl shadow-sm">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Denetimlerim</h2>
        </div>
        <div className="p-6">
          {inspections.length === 0 ? (
            <p className="text-gray-500 text-center py-8">Size henüz denetim atanmamış</p>
          ) : (
            <div className="space-y-4">
              {inspections.map((inspection) => (
                <div key={inspection.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900">
                        {inspection.equipment_info?.equipment_type || 'Ekipman'} Muayenesi
                      </h3>
                      <p className="text-sm text-gray-500 mt-1">
                        Planlanan: {new Date(inspection.planned_date).toLocaleDateString('tr-TR')}
                      </p>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`px-3 py-1 text-xs font-semibold rounded-full ${
                        inspection.status === 'beklemede' ? 'bg-yellow-100 text-yellow-800' :
                        inspection.status === 'devam_ediyor' ? 'bg-blue-100 text-blue-800' :
                        inspection.status === 'rapor_yazildi' ? 'bg-green-100 text-green-800' :
                        inspection.status === 'onaylandi' ? 'bg-emerald-100 text-emerald-800' :
                        inspection.status === 'reddedildi' ? 'bg-red-100 text-red-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {inspection.status === 'beklemede' ? 'Beklemede' :
                         inspection.status === 'devam_ediyor' ? 'Devam Ediyor' :
                         inspection.status === 'rapor_yazildi' ? 'Rapor Yazıldı' :
                         inspection.status === 'onaylandi' ? 'Onaylandı' :
                         inspection.status === 'reddedildi' ? 'Reddedildi' : 'Bilinmeyen'}
                      </span>
                    </div>
                  </div>
                  
                  {/* Action Buttons */}
                  <div className="mt-3 flex space-x-2">
                    {inspection.status === 'beklemede' && (
                      <>
                        <button
                          onClick={() => handleStatusUpdate(inspection.id, 'devam_ediyor')}
                          className="px-3 py-1 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700"
                        >
                          Denetime Başla
                        </button>
                        <button
                          onClick={() => openInspectionForm(inspection)}
                          className="px-3 py-1 bg-green-600 text-white text-sm rounded-md hover:bg-green-700"
                        >
                          Formu Aç
                        </button>
                      </>
                    )}
                    {inspection.status === 'devam_ediyor' && (
                      <>
                        <button
                          onClick={() => openInspectionForm(inspection)}
                          className="px-3 py-1 bg-red-900 text-white text-sm rounded-md hover:bg-red-800"
                        >
                          Formu Doldur
                        </button>
                        <button
                          onClick={() => handleStatusUpdate(inspection.id, 'rapor_yazildi')}
                          className="px-3 py-1 bg-green-600 text-white text-sm rounded-md hover:bg-green-700"
                        >
                          Raporu Teslim Et
                        </button>
                      </>
                    )}
                    {inspection.status === 'reddedildi' && (
                      <>
                        <button
                          onClick={() => openInspectionForm(inspection)}
                          className="px-3 py-1 bg-red-900 text-white text-sm rounded-md hover:bg-red-800"
                        >
                          Formu Düzenle
                        </button>
                        <button
                          onClick={() => handleStatusUpdate(inspection.id, 'devam_ediyor')}
                          className="px-3 py-1 bg-orange-600 text-white text-sm rounded-md hover:bg-orange-700"
                        >
                          Düzeltmeye Başla
                        </button>
                      </>
                    )}
                    {(inspection.status === 'rapor_yazildi' || inspection.status === 'onaylandi') && (
                      <button
                        onClick={() => openInspectionForm(inspection)}
                        className="px-3 py-1 bg-gray-600 text-white text-sm rounded-md hover:bg-gray-700"
                      >
                        Formu Görüntüle
                      </button>
                    )}
                  </div>

                  {/* Approval/Rejection Notes */}
                  {inspection.approval_notes && inspection.status === 'reddedildi' && (
                    <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-md">
                      <p className="text-sm text-red-800">
                        <strong>Red Nedeni:</strong> {inspection.approval_notes}
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const TeknikYoneticiDashboard = () => {
  const [stats, setStats] = useState({});
  const [pendingInspections, setPendingInspections] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
    fetchPendingInspections();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await api.get('/dashboard/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Stats error:', error);
    }
  };

  const fetchPendingInspections = async () => {
    try {
      const response = await api.get('/inspections/pending-approval');
      setPendingInspections(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Pending inspections error:', error);
      setLoading(false);
    }
  };

  const handleApproval = async (inspectionId, action, notes = '') => {
    try {
      await api.post(`/inspections/${inspectionId}/approve`, {
        action,
        notes
      });
      fetchStats();
      fetchPendingInspections();
    } catch (error) {
      console.error('Approval error:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <img 
            src="https://customer-assets.emergentagent.com/job_yeni-yazilim/artifacts/7675i2kn_WhatsApp%20G%C3%B6rsel%202025-08-04%20saat%2012.57.00_7b510c6c.jpg"
            alt="RoyalCert Logo"
            className="w-16 h-16 object-contain mx-auto mb-4"
          />
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-900 mx-auto"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Teknik Yönetici Dashboard</h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard
          title="Onay Bekleyen"
          value={stats.pending_approval || 0}
          color="bg-yellow-100"
          icon={<svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>}
        />
        <StatCard
          title="Bugün Onaylanan"
          value={stats.approved_today || 0}
          color="bg-green-100"
          icon={<svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>}
        />
        <StatCard
          title="Reddedilen"
          value={stats.rejected_reports || 0}
          color="bg-red-100"
          icon={<svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>}
        />
        <StatCard
          title="Toplam Onaylanan"
          value={stats.total_approved || 0}
          color="bg-blue-100"
          icon={<svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path></svg>}
        />
      </div>

      {/* Pending Approvals */}
      <div className="bg-white rounded-xl shadow-sm">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Onay Bekleyen Raporlar</h2>
        </div>
        <div className="p-6">
          {pendingInspections.length === 0 ? (
            <p className="text-gray-500 text-center py-8">Onay bekleyen rapor bulunmuyor</p>
          ) : (
            <div className="space-y-4">
              {pendingInspections.map((inspection) => (
                <div key={inspection.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900">
                        {inspection.equipment_info?.equipment_type || 'Ekipman'} Muayenesi
                      </h3>
                      <p className="text-sm text-gray-500 mt-1">
                        Denetim Tarihi: {new Date(inspection.planned_date).toLocaleDateString('tr-TR')}
                      </p>
                      <p className="text-sm text-gray-500">
                        Rapor Oluşturulma: {new Date(inspection.updated_at || inspection.created_at).toLocaleDateString('tr-TR')}
                      </p>
                    </div>
                    <div className="flex space-x-2 ml-4">
                      <button
                        onClick={() => handleApproval(inspection.id, 'approve')}
                        className="px-3 py-1 bg-green-600 text-white text-sm rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
                      >
                        Onayla
                      </button>
                      <button
                        onClick={() => {
                          const notes = prompt('Red nedeni (opsiyonel):');
                          handleApproval(inspection.id, 'reject', notes);
                        }}
                        className="px-3 py-1 bg-red-600 text-white text-sm rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500"
                      >
                        Reddet
                      </button>
                    </div>
                  </div>
                  {inspection.report_data && (
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      <p className="text-sm text-gray-600">
                        <strong>Rapor Özeti:</strong> Kontrol maddeleri tamamlandı
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Main Layout Component
const Layout = ({ children }) => {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0 flex items-center">
                <img 
                  src="https://customer-assets.emergentagent.com/job_yeni-yazilim/artifacts/7675i2kn_WhatsApp%20G%C3%B6rsel%202025-08-04%20saat%2012.57.00_7b510c6c.jpg"
                  alt="RoyalCert Logo"
                  className="h-8 w-8 object-contain mr-3"
                />
                <h1 className="text-xl font-bold text-red-900">RoyalCert</h1>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-700">
                <span className="font-medium">{user?.full_name}</span>
                <span className="ml-2 text-gray-500">
                  ({user?.role === 'admin' ? 'Admin' : 
                    user?.role === 'planlama_uzmani' ? 'Planlama Uzmanı' : 
                    user?.role === 'teknik_yonetici' ? 'Teknik Yönetici' : 'Denetçi'})
                </span>
              </div>
              <button
                onClick={logout}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
              >
                Çıkış Yap
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  );
};

// Main App Component
const App = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};

const AppContent = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <img 
            src="https://customer-assets.emergentagent.com/job_yeni-yazilim/artifacts/7675i2kn_WhatsApp%20G%C3%B6rsel%202025-08-04%20saat%2012.57.00_7b510c6c.jpg"
            alt="RoyalCert Logo"
            className="w-20 h-20 object-contain mx-auto mb-4"
          />
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-900 mx-auto mb-4"></div>
          <p className="text-royal-600">Yükleniyor...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <LoginPage />;
  }

  return (
    <Layout>
      {user.role === 'admin' && <AdminDashboard />}
      {user.role === 'planlama_uzmani' && <PlanlamaDashboard />}
      {user.role === 'denetci' && <DenetciDashboard />}
      {user.role === 'teknik_yonetici' && <TeknikYoneticiDashboard />}
    </Layout>
  );
};

export default App;