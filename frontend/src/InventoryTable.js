import React from 'react';

function InventoryTable({ items, onEdit, onDelete }) {
  return (
    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
      <thead>
        <tr>
          <th>Name</th>
          <th>SKU</th>
          <th>Quantity</th>
          <th>Location</th>
          <th>Updated At</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {items.map(item => (
          <tr key={item.id} style={{ background: item.quantity < 5 ? '#ffe5e5' : 'white' }}>
            <td>{item.name}</td>
            <td>{item.sku}</td>
            <td>{item.quantity}</td>
            <td>{item.location}</td>
            <td>{item.updatedAt ? new Date(item.updatedAt).toLocaleString() : ''}</td>
            <td>
              <button onClick={() => onEdit(item)}>Edit</button>
              <button onClick={() => onDelete(item.id)} style={{ marginLeft: 8, color: 'red' }}>Delete</button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default InventoryTable;
