
import api from "../api";
import { useState } from "react";
import { useEffect } from "react";
export default function PhotoCard({ photo, onClick }) {
  // const [liked, setLiked] = useState(false);
  // 
  const [liked, setLiked] = useState(false);

  useEffect(() => {
  setLiked(photo.liked);
  }, [photo]);
  const handleLike = async (e) => {
  e.stopPropagation();

  try {
    if (liked) {
      await api.delete(`/photos/${photo.id}/like`);
      setLiked(false);
    } else {
      await api.post(`/photos/${photo.id}/like`);
      setLiked(true);
    }
  } catch (err) {
    console.log(err);
  }
};

  return (
    <div className="photo-card" onClick={onClick}>
      <img src={`http://localhost:8000${photo.image_url}`} />

      <div className="photo-info">
        <h3>{photo.title}</h3>

        <button onClick={handleLike}>
          {liked ? "❤️" : "🤍"}
        </button>
      </div>
    </div>
  );
}