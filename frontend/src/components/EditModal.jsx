import { useState } from "react";

export default function EditModal({ photo, onClose, onSave }) {
  const [form, setForm] = useState({ title: photo.title, description: photo.description });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(form);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <button className="close-btn" onClick={onClose}>✕</button>
        <h2>Edit Photo</h2>
        <form onSubmit={handleSubmit}>
          <input placeholder="Title" value={form.title}
            onChange={e => setForm({...form, title: e.target.value})} required />
          <textarea placeholder="Description" value={form.description}
            onChange={e => setForm({...form, description: e.target.value})} />
          <button type="submit">Save</button>
        </form>
      </div>
    </div>
  );
}