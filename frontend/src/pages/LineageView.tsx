import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ImageNode } from '../models/types';
import { imageService } from '../services/imageService';
import LineageTree from '../components/lineage/LineageTree';
import ImagePreview from '../components/image/ImagePreview';
import Button from '../components/ui/Button';

const LineageView: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [images, setImages] = useState<ImageNode[]>([]);
  const [rootId, setRootId] = useState<number | null>(null);
  const [selectedImage, setSelectedImage] = useState<ImageNode | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadLineage = async () => {
      if (!id) return;
      const imageId = parseInt(id, 10);
      
      try {
        // Get all images in this lineage
        const lineageImages = await imageService.getImageLineage(imageId);
        
        if (lineageImages.length === 0) {
          throw new Error(`No images found for lineage with ID ${imageId}`);
        }
        console.log("lineageImages", lineageImages);
        setImages(lineageImages);
        
        // Find the root image
        const root = lineageImages.find(img => img.isRoot) || lineageImages[0];
        setRootId(root.id);
        
        // Set selected image to the one with the given ID
        const selected = lineageImages.find(img => img.id === imageId);
        setSelectedImage(selected || root);
      } catch (error) {
        console.error("Failed to load lineage:", error);
      } finally {
        setLoading(false);
      }
    };
    
    loadLineage();
  }, [id]);

  const handleNodeClick = async (nodeId: number) => {
    try {
      const image = await imageService.getImageById(nodeId);
      if (image) {
        setSelectedImage(image);
      }
    } catch (error) {
      console.error("Failed to load image:", error);
    }
  };

  const handleEdit = () => {
    if (selectedImage) {
      navigate(`/edit/${selectedImage.id}`);
    }
  };

  const handleRedo = () => {
    if (selectedImage) {
      // For redo, we create a new branch from the image's parent
      const parentId = selectedImage.parentId || selectedImage.id;
      navigate(`/edit/${parentId}`);
    }
  };

  const handleDone = () => {
    navigate('/');
  };

  const handleBack = () => {
    navigate('/');
  };

  if (loading || !rootId || !selectedImage) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-4 flex items-center">
        <Button variant="ghost" onClick={handleBack} className="mr-4">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-1">
            <path d="M19 12H5M12 19l-7-7 7-7"></path>
          </svg>
          Back
        </Button>
        <h1 className="text-3xl font-bold text-gray-900">Image Lineage</h1>
      </div>
      
      <div className="mb-8 rounded-xl bg-white p-4 shadow-md">
        <h2 className="mb-4 text-lg font-medium text-gray-700">Generation History</h2>
        <LineageTree 
          images={images}
          rootId={rootId}
          activeNodeId={selectedImage.id}
          onNodeClick={handleNodeClick}
        />
      </div>
      
      <ImagePreview 
        image={selectedImage}
        onEdit={handleEdit}
        onRedo={handleRedo}
        onDone={handleDone}
      />
    </div>
  );
};

export default LineageView;