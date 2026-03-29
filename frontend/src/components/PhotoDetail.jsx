export default function PhotoDetail({ photo, onClose, onEdit, onDelete }) {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content detail-modal" onClick={e => e.stopPropagation()}>
        <button className="close-btn" onClick={onClose}>✕</button>
        <img src={`http://localhost:8000${photo.image_url}`} alt={photo.title} />
        <h2>{photo.title}</h2>
        {photo.description && <p>{photo.description}</p>}
        <small>Uploaded: {new Date(photo.uploaded_at).toLocaleString()}</small>
        <div className="modal-actions">
          <button className="btn-edit" onClick={onEdit}>✏️ Edit</button>
          <button className="btn-delete" onClick={onDelete}>🗑️ Delete</button>
        </div>
      </div>
    </div>
  );
}