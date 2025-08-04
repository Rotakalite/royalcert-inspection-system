import React, { useState, useEffect, createContext, useContext } from 'react';
import TemplateBuilderModal from './components/TemplateBuilderModal';
import SimpleTemplateBuilder from './components/SimpleTemplateBuilder';
import axios from 'axios';
import './App.css';

// Create Auth Context
const AuthContext = createContext(null);

// API Configuration
const API_BASE_URL = process.env.REACT_APP_ROYALCERT_API_URL || 'http://localhost:8001/api';
const api = axios.create({
  baseURL: API_BASE_URL,
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
      
      // Save both token and user to localStorage
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(user));
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
    localStorage.removeItem('user');
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

// Template Form Modal Component
const TemplateFormModal = ({ onClose, onSave, editingTemplate }) => {
  const [formData, setFormData] = useState({
    name: '',
    equipment_type: '',
    description: '',
    is_active: true
  });

  useEffect(() => {
    if (editingTemplate) {
      setFormData({
        name: editingTemplate.name || '',
        equipment_type: editingTemplate.equipment_type || '',
        description: editingTemplate.description || '',
        is_active: editingTemplate.is_active !== undefined ? editingTemplate.is_active : true
      });
    }
  }, [editingTemplate]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl max-w-md w-full mx-4">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-900">
              {editingTemplate ? 'Template Düzenle' : 'Yeni Template Ekle'}
            </h2>
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
        
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Template Adı *</label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500 focus:border-transparent"
              placeholder="Örn: CARASKAL, İSKELE, FORKLIFT"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Ekipman Tipi *</label>
            <input
              type="text"
              required
              value={formData.equipment_type}
              onChange={(e) => setFormData({...formData, equipment_type: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500 focus:border-transparent"
              placeholder="Ekipman kategorisi"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Açıklama</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500 focus:border-transparent"
              placeholder="Template hakkında açıklama"
              rows="3"
            />
          </div>
          
          <div className="flex items-center">
            <input
              type="checkbox"
              checked={formData.is_active}
              onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
              className="mr-2 h-4 w-4 text-red-600 focus:ring-red-500 border-gray-300 rounded"
            />
            <label className="text-sm text-gray-700">Bu template'i aktif olarak işaretle</label>
          </div>
          
          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            >
              İptal
            </button>
            <button
              type="submit"
              className="px-6 py-2 bg-red-900 text-white rounded-md hover:bg-red-800"
            >
              {editingTemplate ? 'Güncelle' : 'Template Oluştur'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Template Upload Modal Component
const TemplateUploadModal = ({ onClose, selectedFiles, onFileSelect, onSingleUpload, onBulkUpload, uploading }) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full mx-4">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-900">Template Yükle</h2>
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

        <div className="p-6 space-y-6">
          {/* Instructions */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start">
              <svg className="w-5 h-5 text-blue-600 mt-0.5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <div className="text-sm text-blue-800">
                <p className="font-medium mb-1">Template Yükleme Talimatları:</p>
                <ul className="list-disc list-inside space-y-1">
                  <li>Sadece Word dosyaları (.docx, .doc) desteklenmektedir</li>
                  <li>Maksimum 50 dosya aynı anda yükleyebilirsiniz</li>
                  <li>Her dosya otomatik olarak parse edilip template'e dönüştürülür</li>
                  <li>Aynı isimde template varsa yükleme başarısız olur</li>
                </ul>
              </div>
            </div>
          </div>

          {/* File Input */}
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
            <div className="space-y-4">
              <div className="flex justify-center">
                <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                </svg>
              </div>
              <div>
                <label htmlFor="template-files" className="cursor-pointer">
                  <span className="mt-2 block text-sm font-medium text-gray-900">
                    Dosya seçmek için tıklayın veya sürükleyip bırakın
                  </span>
                  <span className="mt-1 block text-xs text-gray-500">
                    Word dosyaları (.docx, .doc)
                  </span>
                </label>
                <input
                  id="template-files"
                  type="file"
                  multiple
                  accept=".docx,.doc"
                  onChange={onFileSelect}
                  className="hidden"
                />
              </div>
            </div>
          </div>

          {/* Selected Files */}
          {selectedFiles.length > 0 && (
            <div className="space-y-2">
              <h3 className="text-sm font-medium text-gray-900">
                Seçilen Dosyalar ({selectedFiles.length})
              </h3>
              <div className="max-h-40 overflow-y-auto space-y-1">
                {selectedFiles.map((file, index) => (
                  <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <div className="flex items-center">
                      <svg className="w-4 h-4 text-blue-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                      </svg>
                      <span className="text-sm text-gray-700">{file.name}</span>
                    </div>
                    <span className="text-xs text-gray-500">
                      {(file.size / 1024).toFixed(1)} KB
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="px-6 py-4 border-t border-gray-200 flex justify-between">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
            disabled={uploading}
          >
            İptal
          </button>
          <div className="space-x-3">
            {selectedFiles.length === 1 && (
              <button
                onClick={onSingleUpload}
                disabled={uploading}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {uploading ? 'Yükleniyor...' : 'Tek Dosya Yükle'}
              </button>
            )}
            {selectedFiles.length > 1 && (
              <button
                onClick={onBulkUpload}
                disabled={uploading}
                className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
              >
                {uploading ? 'Yükleniyor...' : `Toplu Yükle (${selectedFiles.length} dosya)`}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

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

  // Template Management States
  const [showTemplateForm, setShowTemplateForm] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState(null);
  const [uploadingTemplate, setUploadingTemplate] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [showTemplateBuilder, setShowTemplateBuilder] = useState(false);

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

  // Rename the function to match the new code
  const initializeTemplates = initializeCaraskalTemplate;

  // Template Management Functions
  const handleTemplateSave = async (templateData) => {
    try {
      if (editingTemplate) {
        await api.put(`/equipment-templates/${editingTemplate.id}`, templateData);
        alert('Template başarıyla güncellendi');
      } else {
        await api.post('/equipment-templates', templateData);
        alert('Template başarıyla oluşturuldu');
      }
      setShowTemplateForm(false);
      setEditingTemplate(null);
      fetchTemplates();
    } catch (error) {
      console.error('Template save error:', error);
      alert('Template kaydetme hatası: ' + (error.response?.data?.detail || 'Bilinmeyen hata'));
    }
  };

  const handleTemplateBuilderSave = async (templateData) => {
    try {
      // Manuel template oluşturma
      const response = await api.post('/equipment-templates', templateData);
      alert(`✅ Template başarıyla oluşturuldu! ${templateData.total_items} kontrol kriteri eklendi.`);
      setShowTemplateBuilder(false);
      fetchTemplates();
    } catch (error) {
      console.error('Template Builder save error:', error);
      alert('Template kaydetme hatası: ' + (error.response?.data?.detail || 'Bilinmeyen hata'));
    }
  };

  const handleTemplateView = (template) => {
    // TODO: Implement template view functionality
    console.log('View template:', template);
    alert(`${template.name} template'ini görüntüleme özelliği yakında eklenecek`);
  };

  const handleTemplateEdit = (template) => {
    setEditingTemplate(template);
    setShowTemplateForm(true);
  };

  const handleTemplateToggle = async (template) => {
    try {
      await api.put(`/equipment-templates/${template.id}`, {
        ...template,
        is_active: !template.is_active
      });
      alert(`Template ${!template.is_active ? 'aktif' : 'pasif'} duruma getirildi`);
      fetchTemplates();
    } catch (error) {
      console.error('Template toggle error:', error);
      alert('Template durumu değiştirme hatası: ' + (error.response?.data?.detail || 'Bilinmeyen hata'));
    }
  };

  const handleTemplateDelete = async (template) => {
    if (!window.confirm(`${template.name} template'ini silmek istediğinizden emin misiniz?`)) {
      return;
    }

    try {
      await api.delete(`/equipment-templates/${template.id}`);
      alert('Template başarıyla silindi');
      fetchTemplates();
    } catch (error) {
      console.error('Template deletion error:', error);
      alert('Template silme hatası: ' + (error.response?.data?.detail || 'Bilinmeyen hata'));
    }
  };

  // Template Upload Functions
  const handleFileSelect = (event) => {
    const files = Array.from(event.target.files);
    const validFiles = files.filter(file => {
      return file.name.endsWith('.docx') || file.name.endsWith('.doc');
    });
    
    if (validFiles.length !== files.length) {
      alert('Sadece Word dosyaları (.docx, .doc) desteklenmektedir!');
    }
    
    setSelectedFiles(validFiles);
  };

  const handleSingleTemplateUpload = async () => {
    if (selectedFiles.length !== 1) {
      alert('Lütfen tek bir dosya seçin');
      return;
    }

    setUploadingTemplate(true);
    
    try {
      const formData = new FormData();
      formData.append('file', selectedFiles[0]);

      const response = await api.post('/equipment-templates/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      alert('Template başarıyla yüklendi ve işlendi!');
      setShowUploadModal(false);
      setSelectedFiles([]);
      fetchTemplates();
    } catch (error) {
      console.error('Template upload error:', error);
      alert('Template yükleme hatası: ' + (error.response?.data?.detail || 'Bilinmeyen hata'));
    } finally {
      setUploadingTemplate(false);
    }
  };

  const handleBulkTemplateUpload = async () => {
    if (selectedFiles.length === 0) {
      alert('Lütfen en az bir dosya seçin');
      return;
    }

    if (selectedFiles.length > 50) {
      alert('Maksimum 50 dosya yükleyebilirsiniz');
      return;
    }

    setUploadingTemplate(true);
    
    try {
      const formData = new FormData();
      selectedFiles.forEach((file, index) => {
        formData.append('files', file);
      });

      const response = await api.post('/equipment-templates/bulk-upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      const { results } = response.data;
      
      let message = `Toplu yükleme tamamlandı!\n`;
      message += `✅ Başarılı: ${results.successful.length}\n`;
      message += `❌ Başarısız: ${results.failed.length}`;
      
      if (results.failed.length > 0) {
        message += `\n\nBaşarısız dosyalar:\n`;
        results.failed.forEach(failure => {
          message += `• ${failure.filename}: ${failure.error}\n`;
        });
      }

      alert(message);
      setShowUploadModal(false);
      setSelectedFiles([]);
      fetchTemplates();
    } catch (error) {
      console.error('Bulk template upload error:', error);
      alert('Toplu template yükleme hatası: ' + (error.response?.data?.detail || 'Bilinmeyen hata'));
    } finally {
      setUploadingTemplate(false);
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
        <div className="space-y-6">
          {/* User Form Modal */}
          {showUserForm && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-white rounded-xl shadow-xl max-w-md w-full mx-4">
                <div className="px-6 py-4 border-b border-gray-200">
                  <div className="flex justify-between items-center">
                    <h2 className="text-xl font-semibold text-gray-900">
                      {editingUser ? 'Kullanıcı Düzenle' : 'Yeni Kullanıcı Ekle'}
                    </h2>
                    <button
                      onClick={() => {
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
                      }}
                      className="text-gray-400 hover:text-gray-600"
                    >
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
                      </svg>
                    </button>
                  </div>
                </div>
                
                <form onSubmit={handleCreateUser} className="p-6 space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Ad Soyad *</label>
                    <input
                      type="text"
                      required
                      value={userFormData.full_name}
                      onChange={(e) => setUserFormData({...userFormData, full_name: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500 focus:border-transparent"
                      placeholder="Kullanıcının tam adı"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Kullanıcı Adı *</label>
                    <input
                      type="text"
                      required
                      value={userFormData.username}
                      onChange={(e) => setUserFormData({...userFormData, username: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500 focus:border-transparent"
                      placeholder="Giriş için kullanıcı adı"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">E-posta *</label>
                    <input
                      type="email"
                      required
                      value={userFormData.email}
                      onChange={(e) => setUserFormData({...userFormData, email: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500 focus:border-transparent"
                      placeholder="kullanici@royalcert.com"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Rol *</label>
                    <select
                      value={userFormData.role}
                      onChange={(e) => setUserFormData({...userFormData, role: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500 focus:border-transparent"
                    >
                      <option value="denetci">Denetçi</option>
                      <option value="planlama_uzmani">Planlama Uzmanı</option>
                      <option value="teknik_yonetici">Teknik Yönetici</option>
                      <option value="admin">Admin</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      {editingUser ? 'Yeni Şifre (Boş bırakılırsa değişmez)' : 'Şifre *'}
                    </label>
                    <input
                      type="password"
                      required={!editingUser}
                      value={userFormData.password}
                      onChange={(e) => setUserFormData({...userFormData, password: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500 focus:border-transparent"
                      placeholder="En az 6 karakter"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      {editingUser ? 'Şifre Tekrar' : 'Şifre Tekrar *'}
                    </label>
                    <input
                      type="password"
                      required={!editingUser && userFormData.password}
                      value={userFormData.confirm_password}
                      onChange={(e) => setUserFormData({...userFormData, confirm_password: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500 focus:border-transparent"
                      placeholder="Şifrenizi tekrar girin"
                    />
                  </div>
                  
                  <div className="flex justify-end space-x-3 pt-4">
                    <button
                      type="button"
                      onClick={() => {
                        setShowUserForm(false);
                        setEditingUser(null);
                      }}
                      className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
                    >
                      İptal
                    </button>
                    <button
                      type="submit"
                      className="px-6 py-2 bg-red-900 text-white rounded-md hover:bg-red-800"
                    >
                      {editingUser ? 'Güncelle' : 'Kullanıcı Oluştur'}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}

          {/* Password Change Modal */}
          {showPasswordModal && passwordModalUser && (
            <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
              <div className="bg-white rounded-xl shadow-xl max-w-md w-full mx-4">
                <div className="px-6 py-4 border-b border-gray-200">
                  <div className="flex justify-between items-center">
                    <h2 className="text-xl font-semibold text-gray-900">
                      Şifre Değiştir - {passwordModalUser.full_name}
                    </h2>
                    <button
                      onClick={() => {
                        setShowPasswordModal(false);
                        setPasswordModalUser(null);
                      }}
                      className="text-gray-400 hover:text-gray-600"
                    >
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
                      </svg>
                    </button>
                  </div>
                </div>
                
                <form onSubmit={handlePasswordChange} className="p-6 space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Yeni Şifre *</label>
                    <input
                      type="password"
                      name="new_password"
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500 focus:border-transparent"
                      placeholder="En az 6 karakter"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Şifre Tekrar *</label>
                    <input
                      type="password"
                      name="confirm_password"
                      required
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-500 focus:border-transparent"
                      placeholder="Yeni şifrenizi tekrar girin"
                    />
                  </div>
                  
                  <div className="flex justify-end space-x-3 pt-4">
                    <button
                      type="button"
                      onClick={() => {
                        setShowPasswordModal(false);
                        setPasswordModalUser(null);
                      }}
                      className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
                    >
                      İptal
                    </button>
                    <button
                      type="submit"
                      className="px-6 py-2 bg-red-900 text-white rounded-md hover:bg-red-800"
                    >
                      Şifreyi Değiştir
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}

          {/* User List */}
          <div className="bg-white rounded-xl shadow-sm">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-lg font-semibold text-gray-900">Kullanıcı Yönetimi</h2>
                <button
                  onClick={() => setShowUserForm(true)}
                  className="px-4 py-2 bg-red-900 text-white rounded-md hover:bg-red-800"
                >
                  + Yeni Kullanıcı Ekle
                </button>
              </div>
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
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">İşlemler</th>
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
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                        <button
                          onClick={() => handleEditUser(user)}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          Düzenle
                        </button>
                        <button
                          onClick={() => {
                            setPasswordModalUser(user);
                            setShowPasswordModal(true);
                          }}
                          className="text-indigo-600 hover:text-indigo-900"
                        >
                          Şifre
                        </button>
                        <button
                          onClick={() => handleToggleUserStatus(user)}
                          className={`${user.is_active ? 'text-red-600 hover:text-red-900' : 'text-green-600 hover:text-green-900'}`}
                        >
                          {user.is_active ? 'Pasifleştir' : 'Aktifleştir'}
                        </button>
                        <button
                          onClick={() => handleDeleteUser(user)}
                          className="text-red-600 hover:text-red-900"
                        >
                          Sil
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              
              {users.length === 0 && (
                <div className="text-center py-12">
                  <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                  </svg>
                  <h3 className="mt-2 text-sm font-medium text-gray-900">Kullanıcı bulunamadı</h3>
                  <p className="mt-1 text-sm text-gray-500">Yeni kullanıcı eklemek için yukarıdaki butona tıklayın.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'templates' && (
        <div className="space-y-6">
          {/* Template Management Header */}
          <div className="bg-white rounded-xl shadow-sm">
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex justify-between items-center">
                <h2 className="text-lg font-semibold text-gray-900">Ekipman Template'leri Yönetimi</h2>
                <div className="space-x-3">
                  <button
                    onClick={() => setShowTemplateBuilder(true)}
                    className="px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700"
                  >
                    🛠️ Template Builder
                  </button>
                  <button
                    onClick={() => setShowTemplateForm(true)}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                  >
                    + Yeni Template Ekle
                  </button>
                  <button
                    onClick={() => setShowUploadModal(true)}
                    className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                  >
                    📄 Template Yükle
                  </button>
                </div>
              </div>
            </div>

            {/* Template Stats */}
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                <StatCard
                  title="Toplam Template"
                  value={templates.length}
                  color="bg-blue-100"
                  icon={<svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>}
                />
                <StatCard
                  title="Aktif Template"
                  value={templates.filter(t => t.is_active).length}
                  color="bg-green-100"
                  icon={<svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>}
                />
                <StatCard
                  title="Kategori Sayısı"
                  value="8"
                  color="bg-purple-100"
                  icon={<svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>}
                />
              </div>
            </div>
          </div>

          {/* Template Form Modal */}
          {showTemplateForm && (
            <TemplateFormModal 
              onClose={() => {
                setShowTemplateForm(false);
                setEditingTemplate(null);
              }}
              onSave={handleTemplateSave}
              editingTemplate={editingTemplate}
            />
          )}

          {/* Template Upload Modal */}
          {showUploadModal && (
            <TemplateUploadModal
              onClose={() => {
                setShowUploadModal(false);
                setSelectedFiles([]);
              }}
              selectedFiles={selectedFiles}
              onFileSelect={handleFileSelect}
              onSingleUpload={handleSingleTemplateUpload}
              onBulkUpload={handleBulkTemplateUpload}
              uploading={uploadingTemplate}
            />
          )}

          {/* Template List */}
          <div className="bg-white rounded-xl shadow-sm">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Ekipman Template'leri</h3>
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
                            <div className="h-10 w-10 rounded-lg bg-red-100 flex items-center justify-center">
                              <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                              </svg>
                            </div>
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">{template.name}</div>
                            <div className="text-sm text-gray-500">{template.equipment_type}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {template.description || 'Açıklama yok'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {template.categories ? template.categories.length : 0} kategori
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {template.categories ? 
                          template.categories.reduce((total, cat) => total + (cat.items?.length || 0), 0) : 0
                        } madde
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {new Date(template.created_at).toLocaleDateString('tr-TR')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                          template.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {template.is_active ? 'Aktif' : 'Pasif'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                        <button
                          onClick={() => handleTemplateView(template)}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          Görüntüle
                        </button>
                        <button
                          onClick={() => handleTemplateEdit(template)}
                          className="text-indigo-600 hover:text-indigo-900"
                        >
                          Düzenle
                        </button>
                        <button
                          onClick={() => handleTemplateToggle(template)}
                          className={`${template.is_active ? 'text-red-600 hover:text-red-900' : 'text-green-600 hover:text-green-900'}`}
                        >
                          {template.is_active ? 'Pasifleştir' : 'Aktifleştir'}
                        </button>
                        <button
                          onClick={() => handleTemplateDelete(template)}
                          className="text-red-600 hover:text-red-900"
                        >
                          Sil
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              
              {templates.length === 0 && (
                <div className="text-center py-12">
                  <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                  </svg>
                  <h3 className="mt-2 text-sm font-medium text-gray-900">Template bulunamadı</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Yeni template eklemek için yukarıdaki butona tıklayın veya CARASKAL template'ini initialize edin.
                  </p>
                </div>
              )}
            </div>
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
      
      {/* Template Builder Modal */}
      {showTemplateBuilder && (
        <TemplateBuilderModal
          isOpen={showTemplateBuilder}
          onClose={() => setShowTemplateBuilder(false)}
          onSave={handleTemplateBuilderSave}
        />
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
              {/* Create unique equipment types list to avoid duplicates */}
              {Array.from(new Set(equipmentTemplates.map(t => t.equipment_type))).map((equipmentType) => {
                // Find the FORM template for this equipment type (preferred for selection)
                const formTemplate = equipmentTemplates.find(t => t.equipment_type === equipmentType && t.template_type === 'FORM');
                const template = formTemplate || equipmentTemplates.find(t => t.equipment_type === equipmentType);
                
                if (!template) return null;
                
                const isSelected = formData.equipments.some(eq => 
                  equipmentTemplates.some(t => t.id === eq.template_id && t.equipment_type === equipmentType)
                );
                const selectedEquipment = formData.equipments.find(eq => 
                  equipmentTemplates.some(t => t.id === eq.template_id && t.equipment_type === equipmentType)
                );
                
                const relatedTemplates = equipmentTemplates.filter(t => t.equipment_type === equipmentType);
                const formCount = relatedTemplates.filter(t => t.template_type === 'FORM').length;
                const reportCount = relatedTemplates.filter(t => t.template_type === 'REPORT').length;
                
                return (
                  <div key={equipmentType} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center mb-3">
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={(e) => handleEquipmentChange(template.id, e.target.checked)}
                        className="mr-3"
                      />
                      <div>
                        <h3 className="font-medium text-gray-900">{equipmentType}</h3>
                        <p className="text-sm text-gray-500">{equipmentType} ekipmanı için muayene sistemi</p>
                        <p className="text-xs text-gray-400">
                          {relatedTemplates.length > 1 
                            ? formCount + " kontrol formu + " + reportCount + " rapor template'i"
                            : "1 template"}
                        </p>
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
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchFormData();
  }, [inspectionId]);

  const fetchFormData = async () => {
    try {
      const response = await api.get(`/inspections/${inspectionId}/form`);
      setFormData(response.data);
      setFormResults(response.data.form_data || {});
      setGeneralInfo(response.data.general_info || {});
      setLoading(false);
    } catch (error) {
      console.error('Form data error:', error);
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (saving) return;
    setSaving(true);
    
    try {
      await api.put(`/inspections/${inspectionId}/form`, {
        form_data: formResults,
        general_info: generalInfo,
        is_draft: false
      });
      
      alert('Denetim raporu başarıyla kaydedildi!');
      onSave && onSave();
    } catch (error) {
      console.error('Save error:', error);
      alert('Kaydetme hatası: ' + (error.response?.data?.detail || 'Bilinmeyen hata'));
    } finally {
      setSaving(false);
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

  const getItemCategory = (itemId) => {
    if (itemId <= 6) return 'A';
    if (itemId <= 12) return 'B';  
    if (itemId <= 18) return 'C';
    if (itemId <= 24) return 'D';
    if (itemId <= 30) return 'E';
    if (itemId <= 36) return 'F';
    if (itemId <= 42) return 'G';
    return 'H';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-900 mx-auto mb-4"></div>
          <p className="text-gray-600">Denetim formu yükleniyor...</p>
        </div>
      </div>
    );
  }

  if (!formData) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Form verisi bulunamadı</p>
        <button onClick={onBack} className="mt-4 px-4 py-2 bg-gray-600 text-white rounded-md">
          Geri Dön
        </button>
      </div>
    );
  }

  // Group items by category
  const categorizedItems = {};
  if (formData.control_items) {
    formData.control_items.forEach((item, index) => {
      const category = getItemCategory(index + 1);
      if (!categorizedItems[category]) {
        categorizedItems[category] = [];
      }
      categorizedItems[category].push({...item, id: index + 1});
    });
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              {formData.equipment_type} Muayene Formu
            </h1>
            <p className="text-gray-600">
              {formData.customer_name} - {formData.equipment_serial || 'Seri No Belirtilmemiş'}
            </p>
          </div>
          <button onClick={onBack} className="px-4 py-2 text-gray-600 hover:text-gray-800">
            ← Geri Dön
          </button>
        </div>
      </div>

      {/* Control Items by Categories (A-H) */}
      {Object.keys(categorizedItems).sort().map((category) => (
        <div key={category} className="bg-white rounded-xl shadow-sm">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">
              KATEGORİ {category} ({categorizedItems[category].length} madde)
            </h3>
          </div>
          
          <div className="p-6 space-y-6">
            {categorizedItems[category].map((item) => (
              <div key={item.id} className="border border-gray-200 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-3">
                  {item.id}. {item.text}
                </h4>
                
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Sonuç:</label>
                    <select
                      value={formResults[item.id]?.result || ''}
                      onChange={(e) => handleResultChange(item.id, 'result', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-900"
                    >
                      <option value="">Seçin...</option>
                      <option value="U">U (Uygun)</option>
                      <option value="UD">UD (Uygun Değil)</option>
                      <option value="U.Y">U.Y (Uygulanamaz)</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Açıklama:</label>
                    <textarea
                      value={formResults[item.id]?.comment || ''}
                      onChange={(e) => handleResultChange(item.id, 'comment', e.target.value)}
                      rows="2"
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-900"
                      placeholder="Bu madde ile ilgili açıklama..."
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}

      {/* General Information */}
      <div className="bg-white rounded-xl shadow-sm">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Genel Bilgiler ve Sonuç</h3>
        </div>
        
        <div className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tespit Edilen Eksiklik/Kusurlar
            </label>
            <textarea
              value={generalInfo.defects || ''}
              onChange={(e) => setGeneralInfo(prev => ({...prev, defects: e.target.value}))}
              rows="3"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-900"
              placeholder="Tespit edilen kusurları açıklayın..."
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Sonuç</label>
            <select
              value={generalInfo.conclusion || ''}
              onChange={(e) => setGeneralInfo(prev => ({...prev, conclusion: e.target.value}))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-red-900"
            >
              <option value="">Sonuç seçin...</option>
              <option value="UYGUN">Ekipmanın kullanılması UYGUNDUR</option>
              <option value="SAKINCALI">Ekipmanın kullanılması SAKINCALIDIR</option>
              <option value="KOSULLU">Belirtilen koşullarda kullanılması uygundur</option>
            </select>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="bg-white rounded-xl shadow-sm p-6">
        <div className="flex justify-end space-x-4">
          <button
            onClick={onBack}
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
          >
            Geri Dön
          </button>
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-6 py-2 bg-red-900 text-white rounded-md hover:bg-red-800 disabled:opacity-50"
          >
            {saving ? 'Kaydediliyor...' : 'Formu Tamamla'}
          </button>
        </div>
      </div>
    </div>
  );
};

const InspectorTodayInspections = ({ inspections, onInspectionSelect }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'beklemede': return 'bg-yellow-100 text-yellow-800';
      case 'devam_ediyor': return 'bg-blue-100 text-blue-800';
      case 'rapor_yazildi': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'beklemede': return 'Beklemede';
      case 'devam_ediyor': return 'Devam Ediyor';
      case 'rapor_yazildi': return 'Rapor Yazıldı';
      default: return 'Bilinmeyen';
    }
  };

  const getActionButton = (inspection) => {
    switch (inspection.status) {
      case 'beklemede':
        return (
          <button
            onClick={() => onInspectionSelect(inspection)}
            className="px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
          >
            Denetimi Başlat
          </button>
        );
      case 'devam_ediyor':
        return (
          <button
            onClick={() => onInspectionSelect(inspection)}
            className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700"
          >
            Devam Et
          </button>
        );
      case 'rapor_yazildi':
        return (
          <button
            onClick={() => onInspectionSelect(inspection)}
            className="px-3 py-1 bg-gray-600 text-white text-sm rounded hover:bg-gray-700"
          >
            Görüntüle
          </button>
        );
      default:
        return null;
    }
  };

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-gray-900">Bugünkü Denetimler ({inspections.length})</h2>
      
      {inspections.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm p-12 text-center">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3a4 4 0 118 0v4m-4 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2"></path>
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">Bugün denetim yok</h3>
          <p className="mt-1 text-sm text-gray-500">Bugün için planlanmış denetim bulunmuyor.</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {inspections.map((inspection) => (
            <div key={inspection.id} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-lg font-medium text-gray-900">
                      {inspection.equipment_info?.equipment_type || 'Genel Denetim'}
                    </h3>
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(inspection.status)}`}>
                      {getStatusText(inspection.status)}
                    </span>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center text-sm text-gray-600">
                      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-4m-5 0H9m11 0a2 2 0 01-2 2H7a2 2 0 01-2-2m2-10h2m-2 4h2m-2 4h2m-2-8h2m-2 4h2"></path>
                      </svg>
                      <span>Müşteri ID: {inspection.customer_id}</span>
                    </div>
                    {inspection.equipment_info?.serial_number && (
                      <div className="flex items-center text-sm text-gray-600">
                        <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 20l4-16m2 16l4-16M6 9h14M4 15h14"></path>
                        </svg>
                        <span>Seri No: {inspection.equipment_info.serial_number}</span>
                      </div>
                    )}
                    <div className="flex items-center text-sm text-gray-600">
                      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                      </svg>
                      <span>Planlanan: {new Date(inspection.planned_date).toLocaleDateString('tr-TR')} {new Date(inspection.planned_date).toLocaleTimeString('tr-TR', {hour: '2-digit', minute: '2-digit'})}</span>
                    </div>
                  </div>
                </div>
                
                <div className="ml-6">
                  {getActionButton(inspection)}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const InspectorAssignedInspections = ({ inspections, onInspectionSelect }) => {
  const sortedInspections = inspections.sort((a, b) => new Date(a.planned_date) - new Date(b.planned_date));

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-gray-900">
        Atanan Denetimler ({inspections.length})
      </h2>
      
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ekipman</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Müşteri</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Planlanan Tarih</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Durum</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">İşlemler</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {sortedInspections.map((inspection) => (
              <tr key={inspection.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {inspection.equipment_info?.equipment_type || 'Genel Ekipman'}
                  {inspection.equipment_info?.serial_number && (
                    <div className="text-sm text-gray-500">SN: {inspection.equipment_info.serial_number}</div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {inspection.customer_id}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {new Date(inspection.planned_date).toLocaleDateString('tr-TR')}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                    inspection.status === 'beklemede' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-blue-100 text-blue-800'
                  }`}>
                    {inspection.status === 'beklemede' ? 'Beklemede' : 'Devam Ediyor'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    onClick={() => onInspectionSelect(inspection)}
                    className="text-blue-600 hover:text-blue-900"
                  >
                    {inspection.status === 'beklemede' ? 'Başlat' : 'Devam Et'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {inspections.length === 0 && (
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">Atanan denetim yok</h3>
            <p className="mt-1 text-sm text-gray-500">Size henüz bir denetim atanmamış.</p>
          </div>
        )}
      </div>
    </div>
  );
};

const InspectorInspectionHistory = ({ inspections, onInspectionSelect }) => {
  const sortedInspections = inspections.sort((a, b) => new Date(b.completed_at || b.created_at) - new Date(a.completed_at || a.created_at));

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-gray-900">
        Denetim Geçmişi ({inspections.length})
      </h2>
      
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ekipman</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Müşteri</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Tamamlanan Tarih</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Durum</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">İşlemler</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {sortedInspections.map((inspection) => (
              <tr key={inspection.id}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {inspection.equipment_info?.equipment_type || 'Genel Ekipman'}
                  {inspection.equipment_info?.serial_number && (
                    <div className="text-sm text-gray-500">SN: {inspection.equipment_info.serial_number}</div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {inspection.customer_id}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {new Date(inspection.completed_at || inspection.created_at).toLocaleDateString('tr-TR')}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                    inspection.status === 'onaylandi' ? 'bg-green-100 text-green-800' :
                    inspection.status === 'rapor_yazildi' ? 'bg-blue-100 text-blue-800' :
                    'bg-red-100 text-red-800'
                  }`}>
                    {inspection.status === 'onaylandi' ? 'Onaylandı' :
                     inspection.status === 'rapor_yazildi' ? 'Rapor Yazıldı' :
                     inspection.status === 'reddedildi' ? 'Reddedildi' : 'Bilinmeyen'}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <button
                    onClick={() => onInspectionSelect(inspection)}
                    className="text-blue-600 hover:text-blue-900 mr-3"
                  >
                    Görüntüle
                  </button>
                  {inspection.status === 'reddedildi' && (
                    <button
                      onClick={() => onInspectionSelect(inspection)}
                      className="text-green-600 hover:text-green-900"
                    >
                      Düzenle
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        
        {inspections.length === 0 && (
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900">Geçmiş denetim yok</h3>
            <p className="mt-1 text-sm text-gray-500">Henüz tamamlanmış denetiminiz bulunmuyor.</p>
          </div>
        )}
      </div>
    </div>
  );
};

const DenetciDashboard = () => {
  const [stats, setStats] = useState({});
  const [inspections, setInspections] = useState([]);
  const [selectedInspection, setSelectedInspection] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [activeTab, setActiveTab] = useState('today');

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
      
      // Get current user from localStorage with better error handling
      const currentUser = JSON.parse(localStorage.getItem('user') || '{}');
      const currentUserId = currentUser.id;
      
      console.log('DEBUG: Current user:', currentUser);
      console.log('DEBUG: Current user ID:', currentUserId);
      console.log('DEBUG: All inspections:', response.data);
      
      // Filter only inspections assigned to current user
      const userInspections = response.data.filter(inspection => {
        console.log(`DEBUG: Inspection ${inspection.id} - inspector_id: ${inspection.inspector_id}, current user: ${currentUserId}`);
        return inspection.inspector_id === currentUserId;
      });
      
      console.log('DEBUG: Filtered user inspections:', userInspections);
      
      setInspections(userInspections);
    } catch (error) {
      console.error('Inspections error:', error);
    }
  };

  const openInspectionForm = (inspection) => {
    setSelectedInspection(inspection);
    setShowForm(true);
  };

  const handleStatusUpdate = async (inspectionId, newStatus) => {
    try {
      await api.put(`/inspections/${inspectionId}`, { status: newStatus });
      fetchInspections();
      alert('Denetim durumu güncellendi');
    } catch (error) {
      console.error('Status update error:', error);
      alert('Durum güncelleme hatası: ' + (error.response?.data?.detail || 'Bilinmeyen hata'));
    }
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
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">Denetçi Dashboard</h1>
        <div className="text-sm text-gray-500">
          Hoş geldin, {JSON.parse(localStorage.getItem('user') || '{}').full_name}
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard
          title="Toplam Denetimlerim"
          value={inspections.length}
          color="bg-blue-100"
          icon={<svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path></svg>}
        />
        <StatCard
          title="Bekleyen"
          value={inspections.filter(i => i.status === 'beklemede').length}
          color="bg-yellow-100"
          icon={<svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>}
        />
        <StatCard
          title="Devam Eden"
          value={inspections.filter(i => i.status === 'devam_ediyor').length}
          color="bg-blue-100"
          icon={<svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>}
        />
        <StatCard
          title="Tamamlanan"
          value={inspections.filter(i => ['rapor_yazildi', 'onaylandi'].includes(i.status)).length}
          color="bg-green-100"
          icon={<svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>}
        />
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('today')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'today'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Bugünkü Denetimler
          </button>
          <button
            onClick={() => setActiveTab('assigned')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'assigned'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Atanan Denetimler
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'history'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Denetim Geçmişi
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'today' && (
        <InspectorTodayInspections 
          inspections={inspections.filter(inspection => {
            const plannedDate = new Date(inspection.planned_date);
            const today = new Date();
            return plannedDate.toDateString() === today.toDateString();
          })}
          onInspectionSelect={openInspectionForm}
        />
      )}

      {activeTab === 'assigned' && (
        <InspectorAssignedInspections 
          inspections={inspections.filter(i => ['beklemede', 'devam_ediyor'].includes(i.status))}
          onInspectionSelect={openInspectionForm}
        />
      )}

      {activeTab === 'history' && (
        <InspectorInspectionHistory 
          inspections={inspections.filter(i => ['rapor_yazildi', 'onaylandi', 'reddedildi'].includes(i.status))}
          onInspectionSelect={openInspectionForm}
        />
      )}
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