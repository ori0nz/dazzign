import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { ImageNode } from '../models/types';
import { imageService } from '../services/imageService';
import ImageCard from '../components/image/ImageCard';
import Button from '../components/ui/Button';

const Home: React.FC = () => {
  const [rootImages, setRootImages] = useState<ImageNode[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const { t } = useTranslation();

  useEffect(() => {
    const loadImages = async () => {
      try {
        const images = await imageService.getRootImages();
        // console.log("images", images);
        setRootImages(images);
      } catch (error) {
        console.error("Failed to load images:", error);
      } finally {
        setLoading(false);
      }
    };
    
    loadImages();
  }, []);

  const handleCardClick = (imageId: number) => {
    navigate(`/lineage/${imageId}`);
  };

  const handleNewImage = () => {
    navigate('/create');
  };

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-lg">{t('common.loading')}</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8 flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">{t('home.title')}</h1>
        <Button 
          variant="primary" 
          size="lg"
          onClick={handleNewImage}
          className="transition-transform hover:scale-105"
        >
          {t('home.newImage')}
        </Button>
      </div>

      {rootImages.length === 0 ? (
        <div className="mt-20 flex flex-col items-center justify-center">
          <div className="mb-6 text-xl text-gray-600">{t('home.noImages')}</div>
          <Button 
            variant="primary" 
            size="lg" 
            onClick={handleNewImage}
            className="transition-transform hover:scale-105"
          >
            {t('home.createFirst')}
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
          {rootImages.map((image) => (
            <ImageCard 
              key={image.id} 
              image={image} 
              onClick={() => handleCardClick(image.id)} 
            />
          ))}
          <div 
            className="flex h-full cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-gray-300 p-8 text-center hover:border-gray-400"
            onClick={handleNewImage}
          >
            <div className="mb-4 rounded-full bg-indigo-100 p-3 text-indigo-600">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
            </div>
            <p className="text-sm font-medium text-gray-900">{t('home.newImage')}</p>
            <p className="mt-1 text-xs text-gray-500">{t('home.startNew')}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default Home;