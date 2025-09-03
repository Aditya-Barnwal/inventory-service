import React, { useEffect, useState } from 'react';
import axios from 'axios';
import InventoryTable from './InventoryTable';
import InventoryForm from './InventoryForm';

// Read the API base from .env (baked at build time)
const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8080/api/v1';
const api = axios.create({ baseURL: API_BASE });

function App() {
  const [items, setItems] = useState([]);
  const [editingItem, setEditingItem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState(null);

  const fetchItems = async () => {
    try {
      setLoading(true);
      setErr(null);
      const res = await api.get('/inventory');
      setItems(res.data);
    } catch (e) {
      console.error(e);
      setErr('Failed to load items');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItems();
  }, []);

  const handleAdd = async (item) => {
    await api.post('/inventory', item);
    fetchItems();
  };

  const handleEdit = (item) => setEditingItem(item);

  const handleUpdate = async (id, item) => {
    await api.put(`/inventory/${id}`, item);
    setEditingItem(null);
    fetchItems();
  };

  const handleDelete = async (id) => {
    await api.delete(`/inventory/${id}`);
    fetchItems();
  };

  return (
    <div style={{ maxWidth: 800, margin: '40px auto', fontFamily: 'sans-serif' }}>
      <h1>Inventory Dashboard</h1>
      <p style={{ opacity: 0.7, marginTop: -10, fontSize: 12 }}>
        API: <code>{API_BASE}</code>
      </p>

      <InventoryForm
        onAdd={handleAdd}
        onUpdate={handleUpdate}
        editingItem={editingItem}
        setEditingItem={setEditingItem}
      />
      <hr />
      {loading ? <p>Loading...</p> : err ? <p style={{ color: 'crimson' }}>{err}</p> :
        <InventoryTable items={items} onEdit={handleEdit} onDelete={handleDelete} />
      }
    </div>
  );
}

export default App;
