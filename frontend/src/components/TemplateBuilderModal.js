import React, { useState } from 'react';

const TemplateBuilderModal = ({ isOpen, onClose, onSave }) => {
  const [templateData, setTemplateData] = useState({
    name: '',
    equipment_type: '',
    template_type: 'FORM',
    description: '',
    categories: [
      { code: 'A', name: 'KATEGORI A - Kontrol Sistemleri', items: [] },
      { code: 'B', name: 'KATEGORI B - Hareket Sistemleri', items: [] },
      { code: 'C', name: 'KATEGORI C - Göstergeler/Uyarılar', items: [] },
      { code: 'D', name: 'KATEGORI D - Fren Sistemleri', items: [] },
      { code: 'E', name: 'KATEGORI E - Kaldırma/Zincir', items: [] },
      { code: 'F', name: 'KATEGORI F - Çatal/Aparatlar', items: [] },
      { code: 'G', name: 'KATEGORI G - Final Kontroller', items: [] },
      { code: 'H', name: 'KATEGORI H - Diğer Kontroller', items: [] }
    ]
  });

  const [currentCategory, setCurrentCategory] = useState('A');
  const [newItemText, setNewItemText] = useState('');

  const addControlItem = () => {
    if (!newItemText.trim()) return;

    const categoryIndex = templateData.categories.findIndex(cat => cat.code === currentCategory);
    if (categoryIndex === -1) return;

    const newItem = {
      id: Date.now(), // Temporary ID
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

  const getTotalItems = () => {
    return templateData.categories.reduce((total, cat) => total + cat.items.length, 0);
  };

  const handleSave = () => {
    // Assign sequential IDs to all items
    let itemId = 1;
    const updatedCategories = templateData.categories.map(category => ({
      ...category,
      items: category.items.map(item => ({
        ...item,
        id: itemId++
      }))
    }));

    const finalTemplate = {
      ...templateData,
      categories: updatedCategories,
      total_items: getTotalItems()
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
                    {cat.code} - {cat.name}
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
                  <span>{category.name}</span>
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

export default TemplateBuilderModal;