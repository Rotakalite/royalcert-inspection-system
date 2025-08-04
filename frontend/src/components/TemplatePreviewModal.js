import React from 'react';

const TemplatePreviewModal = ({ template, isOpen, onClose }) => {
  if (!isOpen || !template) return null;

  const getTotalItems = () => {
    if (!template.categories) return 0;
    return template.categories.reduce((total, cat) => total + (cat.items?.length || 0), 0);
  };

  const renderFormSection = (title, data, icon) => {
    if (!data || (typeof data === 'object' && Object.keys(data).length === 0)) return null;

    return (
      <div className="bg-gray-50 rounded-lg p-4 mb-4">
        <h4 className="font-medium text-gray-900 mb-3 flex items-center">
          <span className="mr-2">{icon}</span>
          {title}
        </h4>
        <div className="text-sm text-gray-700">
          {typeof data === 'string' ? (
            <p>{data}</p>
          ) : Array.isArray(data) ? (
            <ul className="list-disc list-inside space-y-1">
              {data.map((item, index) => (
                <li key={index}>
                  {typeof item === 'string' ? item : item.label || JSON.stringify(item)}
                </li>
              ))}
            </ul>
          ) : (
            <div className="grid grid-cols-2 gap-2">
              {Object.entries(data).map(([key, value]) => (
                <div key={key} className="flex justify-between">
                  <span className="font-medium">{key}:</span>
                  <span>{typeof value === 'object' ? value.label || JSON.stringify(value) : value}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              📄 Template Önizleme
            </h2>
            <p className="text-sm text-gray-600 mt-1">
              {template.name} - {template.equipment_type}
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6">
          {/* Template Bilgileri */}
          <div className="grid grid-cols-2 gap-6 mb-6">
            <div className="bg-blue-50 rounded-lg p-4">
              <h3 className="font-semibold text-blue-900 mb-3">📋 Template Bilgileri</h3>
              <div className="space-y-2 text-sm">
                <div><span className="font-medium">Ad:</span> {template.name}</div>
                <div><span className="font-medium">Ekipman:</span> {template.equipment_type}</div>
                <div><span className="font-medium">Tür:</span> {template.template_type}</div>
                <div><span className="font-medium">Açıklama:</span> {template.description}</div>
                <div><span className="font-medium">Toplam Madde:</span> {getTotalItems()}</div>
                <div><span className="font-medium">Kategori:</span> {template.categories?.length || 0}</div>
                <div><span className="font-medium">Oluşturulma:</span> {new Date(template.created_at).toLocaleDateString('tr-TR')}</div>
                {template.parsed_from && (
                  <div><span className="font-medium">Kaynak:</span> {template.parsed_from}</div>
                )}
              </div>
            </div>

            <div className="bg-green-50 rounded-lg p-4">
              <h3 className="font-semibold text-green-900 mb-3">📊 İstatistikler</h3>
              <div className="space-y-2 text-sm">
                {template.categories?.map(cat => (
                  <div key={cat.code} className="flex justify-between">
                    <span>Kategori {cat.code}:</span>
                    <span className="font-medium">{cat.items?.length || 0} madde</span>
                  </div>
                ))}
                <div className="border-t pt-2 mt-2 flex justify-between font-semibold">
                  <span>Toplam:</span>
                  <span>{getTotalItems()} madde</span>
                </div>
              </div>
            </div>
          </div>

          {/* Form Bölümleri */}
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">📝 Form Bölümleri</h3>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {renderFormSection("Genel Bilgiler", template.general_info, "🏢")}
              {renderFormSection("Ölçüm Aletleri", template.measurement_devices, "🔧")}
              {renderFormSection("Ekipman Bilgileri", template.equipment_info, "🚛")}
              {renderFormSection("Test Değerleri", template.test_values, "⚖️")}
              {renderFormSection("Test/Deney", template.test_experiments, "🧪")}
              {renderFormSection("Kusur Açıklamaları", template.defect_explanations, "⚠️")}
              {renderFormSection("Notlar", template.notes, "📝")}
              {renderFormSection("Sonuç/Kanaat", template.result_opinion, "✅")}
              {renderFormSection("Muayene Personeli", template.inspector_info, "👨‍🔧")}
              {renderFormSection("Firma Yetkilisi", template.company_official, "👤")}
            </div>
          </div>

          {/* Kontrol Maddeleri */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              ✅ Kontrol Maddeleri ({getTotalItems()} madde)
            </h3>
            <div className="space-y-4">
              {template.categories?.map(category => (
                <div key={category.code} className="border border-gray-200 rounded-lg">
                  <div className="px-4 py-3 bg-gray-50 border-b border-gray-200">
                    <h4 className="font-medium text-gray-900">
                      Kategori {category.code} ({category.items?.length || 0} madde)
                    </h4>
                  </div>
                  <div className="p-4">
                    {category.items && category.items.length > 0 ? (
                      <div className="space-y-2">
                        {category.items.slice(0, 10).map(item => (
                          <div key={item.id} className="flex items-start p-2 bg-gray-50 rounded text-sm">
                            <span className="font-medium text-blue-600 mr-3 min-w-[30px]">
                              {item.id}.
                            </span>
                            <span className="flex-1">{item.text}</span>
                            <div className="flex space-x-2 ml-2">
                              {item.has_comment && (
                                <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">💬 Yorum</span>
                              )}
                              {item.has_photo && (
                                <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">📷 Fotoğraf</span>
                              )}
                            </div>
                          </div>
                        ))}
                        {category.items.length > 10 && (
                          <div className="text-center text-sm text-gray-500 py-2">
                            ... ve {category.items.length - 10} madde daha
                          </div>
                        )}
                      </div>
                    ) : (
                      <p className="text-gray-500 text-sm italic">Bu kategoride madde bulunmuyor</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Debug Bilgileri */}
          {template.raw_text && (
            <div className="mt-6 bg-gray-100 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-2">🔍 Debug Bilgileri</h4>
              <div className="text-sm text-gray-700">
                <p><span className="font-medium">Metin Uzunluğu:</span> {template.text_length || 'Bilinmiyor'} karakter</p>
                <details className="mt-2">
                  <summary className="cursor-pointer font-medium">Ham Metin (İlk 500 karakter)</summary>
                  <pre className="mt-2 text-xs bg-white p-2 rounded border overflow-x-auto">
                    {template.raw_text}
                  </pre>
                </details>
              </div>
            </div>
          )}
        </div>

        <div className="px-6 py-4 border-t border-gray-200 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600 transition-colors"
          >
            Kapat
          </button>
        </div>
      </div>
    </div>
  );
};

export default TemplatePreviewModal;