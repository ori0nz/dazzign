import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import PromptForm from '../components/prompt/PromptForm';
import { imageService } from '../services/imageService';
import { ImageNode } from '../models/types';

const PromptInput: React.FC = () => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { parentId } = useParams<{ parentId?: string }>();
  const parsedParentId = parentId ? parseInt(parentId, 10) : null;
  const [isLoading, setIsLoading] = useState(false);
  const [parentImage, setParentImage] = useState<ImageNode | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadParentImage = async () => {
      if (!parsedParentId) return;
      
      try {
        const image = await imageService.getImageById(parsedParentId);
        if (!image) {
          setError(t('prompt.parentNotFound'));
          return;
        }
        setParentImage(image);
      } catch (error) {
        console.error("Failed to load parent image:", error);
        setError(t('prompt.loadError'));
      }
    };
    
    loadParentImage();
  }, [parsedParentId, t]);

  const handleSubmit = async (data: {
    prompt: string;
    negativePrompt: string;
    specs: Record<string, string[]>;
    parentId: number | null;
  }) => {
    setIsLoading(true);
    try {
      const newImage = await imageService.generateImage({
        ...data,
        parentId: parsedParentId,
      });
      
      // Navigate to the preview page for the new image
      navigate(`/preview/${newImage.id}`);
    } catch (error) {
      console.error("Failed to generate image:", error);
      setError(t('prompt.generateError'));
    } finally {
      setIsLoading(false);
    }
  };

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="rounded-lg bg-red-50 p-4 text-red-800">
          <h2 className="text-lg font-medium">{t('common.error')}</h2>
          <p>{error}</p>
          <button
            onClick={() => navigate('/')}
            className="mt-4 rounded-md bg-red-100 px-4 py-2 text-red-700 hover:bg-red-200"
          >
            {t('common.returnHome')}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="mb-2 text-3xl font-bold text-gray-900">
          {parsedParentId ? t('prompt.editTitle') : t('prompt.createTitle')}
        </h1>
        <p className="text-gray-600">
          {parsedParentId ? t('prompt.editDesc') : t('prompt.createDesc')}
        </p>
      </div>

      {parentImage && (
        <div className="mb-8 overflow-hidden rounded-lg bg-white p-4 shadow-md">
          <h2 className="mb-4 text-lg font-medium text-gray-700">{t('prompt.parentImage')}</h2>
          <div className="flex gap-6">
            <div className="h-48 w-48 flex-shrink-0 overflow-hidden rounded-lg">
              <img 
                src={parentImage.imagePath} 
                alt={parentImage.prompt}
                className="h-full w-full object-cover"
              />
            </div>
            <div className="flex-grow">
              <h3 className="mb-2 font-medium text-gray-900">{t('prompt.originalPrompt')}</h3>
              <p className="mb-4 text-gray-700">{parentImage.prompt}</p>
              {parentImage.negativePrompt && (
                <>
                  <h3 className="mb-2 font-medium text-gray-900">{t('prompt.negativePrompt')}</h3>
                  <p className="mb-4 text-gray-700">{parentImage.negativePrompt}</p>
                </>
              )}
              <div className="flex flex-wrap gap-2">
                {Object.entries(parentImage.specJson).map(([category, values]) =>
                  values.map((value, index) => (
                    <span 
                      key={`${category}-${value}-${index}`}
                      className="rounded-full bg-gray-100 px-3 py-1 text-sm text-gray-700"
                    >
                      {value}
                    </span>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      )}
      
      <PromptForm 
        parentId={parsedParentId}
        initialPrompt={parentImage?.prompt || ''}
        initialNegativePrompt={parentImage?.negativePrompt || ''}
        initialSpecs={parentImage?.specJson || {}}
        onSubmit={handleSubmit}
      />

      {isLoading && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
          <div className="rounded-lg bg-white p-6 text-center">
            <div className="mb-4 text-lg font-medium">{t('prompt.generatingImage')}</div>
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent"></div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PromptInput;