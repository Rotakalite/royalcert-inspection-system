import React, { useState } from 'react';

const SimpleTemplateBuilder = ({ isOpen, onClose, onSave }) => {
  const [templateData, setTemplateData] = useState({
    name: '',
    equipment_type: '',
    template_type: 'FORM',
    description: '',
    categories: [
      { code: 'A', name: 'A', items: [] },
      { code: 'B', name: 'B', items: [] },  
      { code: 'C', name: 'C', items: [] },
      { code: 'D', name: 'D', items: [] },
      { code: 'E', name: 'E', items: [] },
      { code: 'F', name: 'F', items: [] },
      { code: 'G', name: 'G', items: [] },
      { code: 'H', name: 'H', items: [] }
    ]
  });

  const [currentCategory, setCurrentCategory] = useState('A');
  const [newItemText, setNewItemText] = useState('');

  // FORKLIFT template preset
  const forkliftPreset = [
    { category: 'A', items: [
      'Yönlendirme kumandaları ve işaretleri',
      'Sürme ve frenleme kumandaları ve işaretleri', 
      'Kaldirma ve indirme kumandaları ve işaretleri',
      'Yan kayma kumandaları ve işaretleri',
      'Çatal pozisyon kumandaları ve işaretleri',
      'Acil durdurma donanımı',
      'Sesli uyarı cihazları (korna)',
      'Çalışma lambaları ve işaretleri'
    ]},
    { category: 'B', items: [
      'Hareket, direksiyon ve fren sistemlerinin genel durumu',
      'Tahrik tekerleri',
      'Yük tekerleri',
      'Destek tekerleri',
      'Diferansiyel kilit sistemi',
      'Park freni',
      'Servis freni',
      'Direksiyon sistemi'
    ]},
    { category: 'C', items: [
      'Kombine gösterge paneli',
      'Yakıt göstergesi',
      'Sıcaklık göstergesi', 
      'Çalışma saati göstergesi',
      'Batarya şarj göstergesi',
      'Çalışır durumda ikaz lambaları',
      'Geri vites uyarı sistemi',  
      'Yük merkezi işaretlemesi'
    ]},
    { category: 'D', items: [
      'Fren balata ve disklerinin durumu',
      'Fren sisteminin genel çalışması',
      'Park freni ayar ve çalışması',
      'Fren hidrolik sisteminin durumu',
      'Fren boruları ve bağlantılarının durumu',
      'Fren pedalının çalışması',
      'Acil fren sistemi',
      'Fren yağı seviyesi'
    ]},
    { category: 'E', items: [
      'Kaldırma zincirlerinin durumu',
      'Zincir gergiliği ve ayarları',
      'Kaldırma silindirlerinin durumu',
      'Hidrolik hortumlar ve bağlantılar',
      'Mast ray ve kayar parçalar',
      'Kaldırma kapasitesi etiketlemesi', 
      'Yükseklik sınırlayıcı sistemler',
      'Eğim silindirleri'
    ]},
    { category: 'F', items: [
      'Çatal kollarının genel durumu',
      'Çatal kol uzunluk ve kalınlığı',
      'Çatal ayarlama sistemleri',
      'Ek ataşmanların durumu',
      'Çatal poziyon kilitleme sistemi',
      'Yan kayma sistemi',
      'Çatal uçlarının durumu',
      'Yük baskı sistemi'
    ]},
    { category: 'G', items: [
      'Genel güvenlik kontrolleri',
      'Operatör kabini durumu',
      'Emniyet kemeri ve sabitleme',
      'Ek koruyucu donanımlar',
      'Çalışma alanı sınırlayıcıları'
    ]}
  ];

  const addControlItem = () => {
    if (!newItemText.trim()) return;

    const categoryIndex = templateData.categories.findIndex(cat => cat.code === currentCategory);
    if (categoryIndex === -1) return;

    const newItem = {
      id: Date.now(),
      text: newItemText.trim(),
      category: currentCategory,
      input_type: 'dropdown',
      has_comment: true,
      required: true
    };

    const updatedCategories = [...templateData.categories];
    updatedCategories[categoryIndex].items.push(newItem);

    setTemplateData({
      ...templateData,
      categories: updatedCategories
    });

    setNewItemText('');
  };

  const removeControlItem = (categoryCode, itemId) => {
    const categoryIndex = templateData.categories.findIndex(cat => cat.code === categoryCode);
    if (categoryIndex === -1) return;

    const updatedCategories = [...templateData.categories];
    updatedCategories[categoryIndex].items = updatedCategories[categoryIndex].items.filter(
      item => item.id !== itemId
    );

    setTemplateData({
      ...templateData,
      categories: updatedCategories
    });
  };

  const loadForkliftPreset = () => {
    const updatedCategories = templateData.categories.map(category => {
      const preset = forkliftPreset.find(p => p.category === category.code);
      if (preset) {
        return {
          ...category,
          items: preset.items.map((text, index) => ({
            id: Date.now() + index,
            text,
            category: category.code,
            input_type: 'dropdown',
            has_comment: true,
            required: true
          }))
        };
      }
      return category;
    });

    setTemplateData({
      ...templateData,
      name: 'FORKLIFT MUAYENE FORMU',
      equipment_type: 'FORKLIFT',
      description: 'Forklift periyodik muayene formu - 53 kontrol kriteri',
      categories: updatedCategories
    });
  };

  const getTotalItems = () => {
    return templateData.categories.reduce((total, cat) => total + cat.items.length, 0);
  };

  const handleSave = () => {
    let itemId = 1;
    const updatedCategories = templateData.categories.map(category => ({
      ...category,
      items: category.items.map(item => ({
        ...item,
        id: itemId++
      }))
    }));

    // FORM BÖLÜMLERINI EKLE - BU ÖNEMLİ!
    const finalTemplate = {
      ...templateData,
      categories: updatedCategories,
      total_items: getTotalItems(),
      
      // Universal Template Structure - Form bölümleri
      general_info: {
        company_name: { label: 'Firma Adı', required: true },
        inspection_address: { label: 'Muayene adresi', required: true },
        phone: { label: 'Telefon', required: false },
        email: { label: 'E-posta', required: false },
        periodic_control_date: { label: 'Periyodik Kontrol Tarihi', required: true },
        team_control_date: { label: 'Takım Kontrol Tarihi', required: false },
        next_periodic_date: { label: 'Bir Sonraki Periyodik Kontrol Tarihi', required: true },
        report_date: { label: 'Rapor Tarihi', required: true },
        report_no: { label: 'Rapor No', required: true },
        control_start_time: { label: 'Kontrol Başlangıç Saati', required: false },
        control_end_time: { label: 'Kontrol Bitiş Saati', required: false },
        isg_agreement_id: { label: 'İSG-Kâtip sözleşme ID', required: false },
        work_permit_no: { label: 'İşyeri SGK Sicil No', required: false },
        control_method: { label: 'Periyodik Kontrol Metodu', required: false }
      },
      
      measurement_devices: [
        { label: 'Cihaz Adı', required: true },
        { label: 'Cihaz Markası', required: true },
        { label: 'Cihaz Kodu/Seri No', required: true },
        { label: 'Kalibrasyon Tarihi', required: true }
      ],
      
      equipment_info: {
        brand: { label: 'Markası', required: true },
        type_model: { label: 'Tipi/Modeli', required: true },
        serial_no: { label: 'Seri no', required: true },
        manufacturing_year: { label: 'İmal yılı', required: true },
        forklift_type: { label: 'Forklift Tipi', options: ['İçten Yanmalı', 'Akülü'], required: true },
        usage_location: { label: 'Kullanım yeri / amacı', required: false },
        fuel_type: { label: 'Yakıt türü', required: false },
        fork_length: { label: 'Çatal kollarının uzunluğu (mm)', required: false },
        fork_width: { label: 'Çatal kollarının genişliği (mm)', required: false },
        lifting_capacity: { label: 'Kaldırma Kapasitesi (kg)', required: true },
        lifting_height: { label: 'Kaldırma yüksekliği (mm)', required: false },
        load_center_distance: { label: 'Yük merkezi mesafesi (mm)', required: false },
        wheel_type: { label: 'Tekerlek tipi', required: false }
      },
      
      test_values: {
        min_annual_test_date: { label: 'Azami Yılda Bir Yapılan Son Test Tarihi', required: false },
        max_three_year_test_date: { label: 'Azami Üç Yılda Bir Yapılan Son Test Tarihi', required: false },
        static_test_load: { label: 'Statik Test Yükü (Kg)', required: false },
        dynamic_test_load: { label: 'Dinamik Test Yükü (Kg)', required: false },
        test_load: { label: 'Test Yükü (Kg)', required: false }
      },
      
      test_experiments: [
        { id: 51, text: 'Forkliftin yüksüz durumda mekanik dayanımı', required: true },
        { id: 52, text: 'Forkliftin ... nin yük merkezinde, ... nin yükselikte, ... kg nominal yükte mekanik dayanımı (kaldırma silindirleri için)', required: true },  
        { id: 53, text: 'Forkliftin 2500 mm yükselikte ... nin yük merkezinde ... kg yükte mekanik dayanımı (eğim tipi silindirleri için)', required: true }
      ],
      
      defect_explanations: 'Tespit edilen kusurların detaylı açıklaması',
      notes: 'Ek notlar ve açıklamalar',
      result_opinion: 'Yukarıda teknik özellikleri belirtilen ekipmanın kullanılması UYGUNDIR/SAKINCALIDIR.',
      
      inspector_info: {
        name: { label: 'Adı Soyadı', required: true },
        title: { label: 'Unvanı', required: true },
        signature: { label: 'İmza', required: true, type: 'signature' }
      },
      
      company_official: {
        name: { label: 'Adı Soyadı', required: true },  
        title: { label: 'Görevi', required: true },
        signature: { label: 'İmza', required: true, type: 'signature' }
      }
    };

    onSave(finalTemplate);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <h2 className="text-xl font-semibold text-gray-900">
            🛠️ Template Builder - Manuel Oluştur
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          {/* Template Basic Info */}
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Template Adı
              </label>
              <input
                type="text"
                value={templateData.name}
                onChange={(e) => setTemplateData({ ...templateData, name: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="ör: FORKLIFT MUAYENE FORMU"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Ekipman Türü
              </label>
              <select
                value={templateData.equipment_type}
                onChange={(e) => setTemplateData({ ...templateData, equipment_type: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Seçin...</option>
                <option value="FORKLIFT">FORKLIFT</option>
                <option value="CARASKAL">CARASKAL</option>
                <option value="ISKELE">İSKELE</option>
                <option value="VINC">VİNÇ</option>
                <option value="ASANSÖR">ASANSÖR</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Template Türü
              </label>
              <select
                value={templateData.template_type}
                onChange={(e) => setTemplateData({ ...templateData, template_type: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="FORM">FORM (Muayene Formu)</option>
                <option value="REPORT">REPORT (Rapor Template)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Toplam Kontrol Kriteri: <span className="font-bold text-blue-600">{getTotalItems()}</span>
              </label>
              <input
                type="text"
                value={templateData.description}
                onChange={(e) => setTemplateData({ ...templateData, description: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Template açıklaması"
              />
            </div>
          </div>

          {/* Forklift Preset Button */}
          <div className="mb-6">
            <button
              onClick={loadForkliftPreset}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
            >
              🚛 FORKLIFT Template Yükle (53 Kriter)
            </button>
          </div>

          {/* Control Item Builder */}
          <div className="border border-gray-200 rounded-lg p-4 mb-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">
              📝 Kontrol Kriteri Ekle
            </h3>
            <div className="flex gap-4 mb-4">
              <select
                value={currentCategory}
                onChange={(e) => setCurrentCategory(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {templateData.categories.map(cat => (
                  <option key={cat.code} value={cat.code}>
                    Kategori {cat.code}
                  </option>
                ))}
              </select>
              <input
                type="text"
                value={newItemText}
                onChange={(e) => setNewItemText(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && addControlItem()}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Kontrol kriteri metnini girin..."
              />
              <button
                onClick={addControlItem}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Ekle
              </button>
            </div>
          </div>

          {/* Categories and Items Display */}
          <div className="grid grid-cols-2 gap-6">
            {templateData.categories.map(category => (
              <div key={category.code} className="border border-gray-200 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-3 flex justify-between">
                  <span>Kategori {category.code}</span>
                  <span className="text-sm text-gray-500">({category.items.length} item)</span>
                </h4>
                <div className="space-y-2 max-h-40 overflow-y-auto">
                  {category.items.length === 0 ? (
                    <p className="text-gray-400 text-sm italic">Henüz item eklenmemiş</p>
                  ) : (
                    category.items.map(item => (
                      <div key={item.id} className="flex justify-between items-start p-2 bg-gray-50 rounded text-sm">
                        <span className="flex-1">{item.text}</span>
                        <button
                          onClick={() => removeControlItem(category.code, item.id)}
                          className="ml-2 text-red-500 hover:text-red-700"
                        >
                          ×
                        </button>
                      </div>
                    ))
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="px-6 py-4 border-t border-gray-200 flex justify-between items-center">
          <div className="text-sm text-gray-600">
            Toplam: <span className="font-bold text-lg">{getTotalItems()}</span> kontrol kriteri
          </div>
          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
            >
              İptal
            </button>
            <button
              onClick={handleSave}
              disabled={!templateData.name || !templateData.equipment_type || getTotalItems() === 0}
              className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
            >
              Template Kaydet
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SimpleTemplateBuilder;