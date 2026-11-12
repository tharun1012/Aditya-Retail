#!/usr/bin/env python3
import shutil

TARGET = "frontend/src/components/PORequestsTab.js"
with open(TARGET, "r") as f:
    content = f.read()
shutil.copy(TARGET, TARGET + ".bak_search1")

# --- Add Search icon import ---
old_import = '''import { 
  Plus, RefreshCw, Eye, Check, X, Clock, Package, 
  AlertTriangle, FileText, Calendar 
} from 'lucide-react';'''
new_import = '''import { 
  Plus, RefreshCw, Eye, Check, X, Clock, Package, 
  AlertTriangle, FileText, Calendar, Search 
} from 'lucide-react';'''
assert old_import in content, "IMPORT anchor not found"
content = content.replace(old_import, new_import, 1)

# --- Extend item shape + add product/HSN state, fetchers, and product-select/create-product logic ---
old_block = '''const CreatePORequestModal = ({ storeData, onClose, onSuccess }) => {
  const [items, setItems] = useState([{ model_number: '', quantity: 1, notes: '' }]);
  const [urgency, setUrgency] = useState('normal');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const addItem = () => {
    setItems([...items, { model_number: '', quantity: 1, notes: '' }]);
  };'''

new_block = '''const CreatePORequestModal = ({ storeData, onClose, onSuccess }) => {
  const [items, setItems] = useState([{ model_number: '', product_name: '', product_id: '', quantity: 1, notes: '' }]);
  const [urgency, setUrgency] = useState('normal');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [products, setProducts] = useState([]);
  const [hsnCodes, setHsnCodes] = useState([]);
  const [productSearch, setProductSearch] = useState({});
  const [showAddProductModal, setShowAddProductModal] = useState(false);
  const [addProductForIndex, setAddProductForIndex] = useState(null);
  const [newProduct, setNewProduct] = useState({
    name: '',
    brand: '',
    model_number: '',
    price: 0,
    hsn_code: '',
    category: '',
    description: '',
    current_stock: 0
  });
  const [addProductLoading, setAddProductLoading] = useState(false);
  const [newProductHsnSuggestions, setNewProductHsnSuggestions] = useState([]);
  const [manualHsnMode, setManualHsnMode] = useState(false);
  const [manualHsnGstRate, setManualHsnGstRate] = useState(18);

  useEffect(() => {
    fetchProducts();
    fetchHSNCodes();
  }, []);

  const fetchProducts = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/products?limit=1000`);
      const data = await response.json();
      if (data.status === 'success') {
        setProducts(data.products);
      }
    } catch (err) {
      console.error('Failed to fetch products');
    }
  };

  const fetchHSNCodes = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/hsn/?active_only=true`);
      const data = await response.json();
      setHsnCodes(data);
    } catch (err) {
      console.error('Failed to fetch HSN codes');
    }
  };

  const getFilteredProducts = (searchTerm) => {
    if (!searchTerm) return products;
    const term = searchTerm.toLowerCase();
    return products.filter(p =>
      p.name.toLowerCase().includes(term) ||
      p.brand?.toLowerCase().includes(term) ||
      p.model_number?.toLowerCase().includes(term)
    );
  };

  const handleProductSelect = (index, productId) => {
    const product = products.find(p => p.id === productId);
    if (product) {
      const newItems = [...items];
      newItems[index] = {
        ...newItems[index],
        product_id: product.id,
        product_name: product.name,
        model_number: product.model_number || product.sku || newItems[index].model_number
      };
      setItems(newItems);
    }
  };

  const fetchNewProductHsnSuggestion = async (productName) => {
    if (!productName || productName.length < 2) {
      setNewProductHsnSuggestions([]);
      return;
    }
    try {
      const response = await fetch(`${BACKEND_URL}/api/hsn/suggest?product_name=${encodeURIComponent(productName)}`);
      const data = await response.json();
      if (data.suggestions && data.suggestions.length > 0) {
        setNewProductHsnSuggestions(data.suggestions);
        if (!newProduct.hsn_code && data.suggestions[0].match_score >= 50) {
          setNewProduct(prev => ({ ...prev, hsn_code: data.suggestions[0].code }));
        }
      } else {
        setNewProductHsnSuggestions([]);
      }
    } catch (err) {
      console.error('Error fetching HSN suggestions:', err);
    }
  };

  const openAddProductModal = (index) => {
    setAddProductForIndex(index);
    setNewProduct({
      name: '',
      brand: '',
      model_number: '',
      price: 0,
      hsn_code: '',
      category: '',
      description: '',
      current_stock: 0
    });
    setManualHsnMode(false);
    setManualHsnGstRate(18);
    setNewProductHsnSuggestions([]);
    setShowAddProductModal(true);
  };

  const handleCreateProduct = async () => {
    if (!newProduct.name || !newProduct.price || !newProduct.hsn_code) {
      setError('Please fill in product name, price, and HSN code');
      return;
    }

    setAddProductLoading(true);
    try {
      let gstRate = 18.0;
      const existingHsn = hsnCodes.find(h => h.code === newProduct.hsn_code);

      if (manualHsnMode && !existingHsn) {
        try {
          const hsnResponse = await fetch(`${BACKEND_URL}/api/hsn/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              code: newProduct.hsn_code,
              description: `HSN ${newProduct.hsn_code} - ${newProduct.category || newProduct.name}`,
              gst_rate: manualHsnGstRate,
              category: newProduct.category || 'Uncategorized',
              is_active: true
            })
          });
          if (hsnResponse.ok) {
            await fetchHSNCodes();
            gstRate = manualHsnGstRate;
          }
        } catch (hsnError) {
          console.log('HSN code might already exist or failed to save:', hsnError);
        }
        gstRate = manualHsnGstRate;
      } else if (existingHsn) {
        gstRate = existingHsn.gst_rate || 18.0;
      }

      const response = await fetch(`${BACKEND_URL}/api/products`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...newProduct,
          id: `PROD-${Date.now()}`,
          price: parseFloat(newProduct.price),
          current_stock: parseInt(newProduct.current_stock) || 0
        })
      });

      const data = await response.json();

      if (response.ok) {
        await fetchProducts();

        if (addProductForIndex !== null) {
          const newItems = [...items];
          newItems[addProductForIndex] = {
            ...newItems[addProductForIndex],
            product_id: data.product?.id || data.id,
            product_name: newProduct.name,
            model_number: newProduct.model_number || newItems[addProductForIndex].model_number
          };
          setItems(newItems);
        }

        setShowAddProductModal(false);
        setManualHsnMode(false);
        setManualHsnGstRate(18);
      } else {
        setError(data.detail || 'Failed to create product');
      }
    } catch (err) {
      setError('Error creating product: ' + err.message);
    } finally {
      setAddProductLoading(false);
    }
  };

  const addItem = () => {
    setItems([...items, { model_number: '', product_name: '', product_id: '', quantity: 1, notes: '' }]);
  };'''

assert old_block in content, "ITEM-SHAPE / STATE block anchor not found"
content = content.replace(old_block, new_block, 1)

with open(TARGET, "w") as f:
    f.write(content)

print("Patched", TARGET, "- step 1 of 3 (imports + state + logic)")
