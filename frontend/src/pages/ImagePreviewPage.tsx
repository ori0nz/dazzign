import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ImageNode } from '../models/types';
import { imageService } from '../services/imageService';
import ImagePreview from '../components/image/ImagePreview';

const ImagePreviewPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [image, setImage] = useState<ImageNode | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadImage = async () => {
      if (!id) return;
      
      try {
        const fetchedImage = await imageService.getImageById(parseInt(id, 10));
        setImage(fetchedImage);
      } catch (error) {
        console.error("Failed to load image:", error);
      } finally {
        setLoading(false);
      }
    };
    
    loadImage();
  }, [id]);

  const handleEdit = () => {
    if (image) {
      navigate(`/edit/${image.id}`);
    }
  };

  const handleRedo = () => {
    if (image) {
      // For redo, we create a new branch from the image's parent
      const parentId = image.parentId || image.id;
      navigate(`/edit/${parentId}`);
    }
  };

  const handleDone = () => {
    if (image) {
      navigate(`/lineage/${image.id}`);
    }
  };

  if (loading || !image) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Image Preview</h1>
      </div>
      
      <ImagePreview 
        image={image}
        onEdit={handleEdit}
        onRedo={handleRedo}
        onDone={handleDone}
      />
    </div>
  );
};

export default ImagePreviewPage;