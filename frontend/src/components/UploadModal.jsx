import { useState } from "react";
import api from "../api";

export default function UploadModal({ onClose, onUploaded }) {
  const [form, setForm] = useState({ title: "", description: "" });
  // const [file, setFile] = useState(null);
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  // const [preview, setPreview] = useState(null);
  const [preview, setPreview] = useState([]);
  // const handleFile = (e) => {
  //   const f = e.target.files[0];
  //   setFile(f);
  //   if (f) setPreview(URL.createObjectURL(f));
  // };



  const handleFile = (e) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles(selectedFiles);

    const previews = selectedFiles.map(f => URL.createObjectURL(f));
    setPreview(previews);
  };

  // const handleSubmit = async (e) => {
  //   e.preventDefault();
  //   if (!file) return;
  //   setLoading(true);
  //   const fd = new FormData();
  //   fd.append("title", form.title);
  //   fd.append("description", form.description);
  //   fd.append("file", file);
  //   try {
  //     await api.post("/photos", fd);
  //     onUploaded();
  //   } catch (err) {
  //     alert(err.response?.data?.detail || "Upload failed");
  //   } finally {
  //     setLoading(false);
  //   }
  // };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const fd = new FormData();

    files.forEach(file => {
      fd.append("files", file);
    });

    fd.append("title", form.title);
    fd.append("description", form.description);

    await api.post("/photos/multiple", fd);

    onUploaded();
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <button className="close-btn" onClick={onClose}>✕</button>
        <h2>Upload Photo</h2>
        <form onSubmit={handleSubmit}>
          <input placeholder="Title" value={form.title}
            onChange={e => setForm({ ...form, title: e.target.value })} required />
          <textarea placeholder="Description (optional)" value={form.description}
            onChange={e => setForm({ ...form, description: e.target.value })} />
          {/* <input type="file" accept="image/*" onChange={handleFile} required /> */}
          <input type="file" multiple accept="image/*" onChange={handleFile} required />
          {/* {preview && <img src={preview} alt="preview" className="preview-img" />} */}
          {preview.map((img, i) => (
            <img key={i} src={img} className="preview-img" />
          ))}
          <button type="submit" disabled={loading}>{loading ? "Uploading..." : "Upload"}</button>
        </form>
      </div>
    </div>
  );
}