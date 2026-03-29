import { useState, useEffect, useCallback } from "react";
import { useAuth } from "../context/AuthContext";
import api from "../api";
import PhotoCard from "../components/PhotoCard";
import PhotoDetail from "../components/PhotoDetail";
import UploadModal from "../components/UploadModal";
import EditModal from "../components/EditModal";

export default function Gallery() {
  const { user, logout } = useAuth();
  const [photos, setPhotos] = useState([]);
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState(null);
  const [editing, setEditing] = useState(null);
  const [showUpload, setShowUpload] = useState(false);

  const fetchPhotos = useCallback(async () => {
    const res = await api.get("/photos", { params: { search: search || undefined } });
    setPhotos(res.data);
  }, [search]);

  useEffect(() => { fetchPhotos(); }, [fetchPhotos]);

  const handleDelete = async (id) => {
    if (!confirm("Delete this photo?")) return;
    await api.delete(`/photos/${id}`);
    setSelected(null);
    fetchPhotos();
  };

  return (
    <div className="gallery-page">
      <header className="gallery-header">
        <h1>📷 My Gallery</h1>
        <div className="header-right">
          <span>Hello, {user.username}</span>
          <button className="btn-upload" onClick={() => setShowUpload(true)}>+ Upload</button>
          <button className="btn-logout" onClick={logout}>Logout</button>
        </div>
      </header>

      <div className="search-bar">
        <input placeholder="🔍 Search by title..." value={search}
          onChange={e => setSearch(e.target.value)} />
      </div>

      {photos.length === 0 ? (
        <div className="empty-state">
          <p>No photos yet. Upload your first photo!</p>
        </div>
      ) : (
        <div className="photo-grid">
          {photos.map(p => (
            <PhotoCard key={p.id} photo={p} onClick={() => setSelected(p)} />
          ))}
        </div>
      )}

      {selected && (
        <PhotoDetail photo={selected} onClose={() => setSelected(null)}
          onEdit={() => { setEditing(selected); setSelected(null); }}
          onDelete={() => handleDelete(selected.id)} />
      )}

      {editing && (
        <EditModal photo={editing} onClose={() => setEditing(null)}
          onSave={async (data) => {
            await api.put(`/photos/${editing.id}`, data);
            setEditing(null); fetchPhotos();
          }} />
      )}

      {showUpload && (
        <UploadModal onClose={() => setShowUpload(false)}
          onUploaded={() => { setShowUpload(false); fetchPhotos(); }} />
      )}
    </div>
  );
}