import React, { useEffect, useState } from 'react';

const initialState = { name: '', sku: '', quantity: '', location: '' };

function InventoryForm({ onAdd, onUpdate, editingItem, setEditingItem }) {
  const [form, setForm] = useState(initialState);

  useEffect(() => {
    if (editingItem) {
      setForm({
        name: editingItem.name,
        sku: editingItem.sku,
        quantity: editingItem.quantity,
        location: editingItem.location,
      });
    } else {
      setForm(initialState);
    }
  }, [editingItem]);

  const handleChange = e => {
    const { name, value } = e.target;
    setForm(f => ({ ...f, [name]: value }));
  };

  const handleSubmit = e => {
    e.preventDefault();
    if (!form.name || !form.sku || !form.quantity || !form.location) return;
    if (editingItem) {
      onUpdate(editingItem.id, { ...form, quantity: Number(form.quantity) });
    } else {
      onAdd({ ...form, quantity: Number(form.quantity) });
    }
    setForm(initialState);
    setEditingItem(null);
  };

  const handleCancel = () => {
    setForm(initialState);
    setEditingItem(null);
  };

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: 24 }}>
      <h2>{editingItem ? 'Edit Item' : 'Add Item'}</h2>
      <input name="name" placeholder="Name" value={form.name} onChange={handleChange} required />{' '}
      <input name="sku" placeholder="SKU" value={form.sku} onChange={handleChange} required />{' '}
      <input name="quantity" type="number" placeholder="Quantity" value={form.quantity} onChange={handleChange} required min="0" />{' '}
      <input name="location" placeholder="Location" value={form.location} onChange={handleChange} required />{' '}
      <button type="submit">{editingItem ? 'Update' : 'Add'}</button>
      {editingItem && <button type="button" onClick={handleCancel} style={{ marginLeft: 8 }}>Cancel</button>}
    </form>
  );
}

export default InventoryForm;
