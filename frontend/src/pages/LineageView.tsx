import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { ImageNode } from '../models/types';
import { imageService } from '../services/imageService';
import LineageTree from '../components/lineage/LineageTree';
import ImagePreview from '../components/image/ImagePreview';
import Button from '../components/ui/Button';

const LineageView: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [images, setImages] = useState<ImageNode[]>([]);
  const [rootId, setRootId] = useState<number | null>(null);
  const [selectedImage, setSelectedImage] = useState<ImageNode | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadLineage = async () => {
      if (!id) {
        setError(t('lineage.noImageId'));
        setLoading(false);
        return;
      }

      const imageId = parseInt(id, 10);
      if (isNaN(imageId)) {
        setError(t('lineage.invalidImageId'));
        setLoading(false);
        return;
      }
      
      try {
        const lineageImages = await imageService.getImageLineage(imageId);
        
        if (lineageImages.length === 0) {
          setError(t('lineage.noImagesFound', { id: imageId }));
          setLoading(false);
          return;
        }
        
        setImages(lineageImages);
        const root = lineageImages.find(img => img.isRoot) || lineageImages[0];
        setRootId(root.id);
        const selected = lineageImages.find(img => img.id === imageId);
        setSelectedImage(selected || root);
      } catch (error) {
        console.error("Failed to load lineage:", error);
        setError(t('lineage.loadError'));
      } finally {
        setLoading(false);
      }
    };
    
    loadLineage();
  }, [id, t]);

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

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-lg">{t('common.loading')}</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="mb-4 flex items-center">
          <Button variant="ghost" onClick={handleBack} className="mr-4">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-1">
              <path d="M19 12H5M12 19l-7-7 7-7"></path>
            </svg>
            {t('common.back')}
          </Button>
        </div>
        <div className="rounded-lg bg-red-50 p-4 text-red-800">
          <h2 className="text-lg font-medium">{t('common.error')}</h2>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (!rootId || !selectedImage) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="mb-4 flex items-center">
          <Button variant="ghost" onClick={handleBack} className="mr-4">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="mr-1">
              <path d="M19 12H5M12 19l-7-7 7-7"></path>
            </svg>
            {t('common.back')}
          </Button>
        </div>
        <div className="rounded-lg bg-yellow-50 p-4 text-yellow-800">
          <p>{t('lineage.noData')}</p>
        </div>
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
          {t('common.back')}
        </Button>
        <h1 className="text-3xl font-bold text-gray-900">{t('lineage.title')}</h1>
      </div>
      
      <div className="mb-8 rounded-xl bg-white p-4 shadow-md">
        <h2 className="mb-4 text-lg font-medium text-gray-700">{t('lineage.history')}</h2>
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
        // onRedo={handleRedo}
        // onDone={handleDone}
      />
    </div>
  );
};

export default LineageView;