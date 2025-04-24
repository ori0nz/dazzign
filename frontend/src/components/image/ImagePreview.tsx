import React from 'react';
import Button from '../ui/Button';
import Tag from '../ui/Tag';
import { ImageNode, SpecCategory } from '../../models/types';
import { SPEC_CATEGORIES } from '../../data/mockData';

interface ImagePreviewProps {
  image: ImageNode;
  onEdit: () => void;
  onRedo: () => void;
  onDone: () => void;
}

const ImagePreview: React.FC<ImagePreviewProps> = ({
  image,
  onEdit,
  onRedo,
  onDone,
}) => {
  // Find the category object for a given category ID
  const getCategoryById = (id: string): SpecCategory | undefined => {
    return SPEC_CATEGORIES.find(category => category.id === id);
  };

  // Format the date to a more readable format
  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: 'numeric',
      hour12: true,
    }).format(date);
  };

  return (
    <div className="mx-auto max-w-4xl p-4">
      <div className="overflow-hidden rounded-2xl bg-white shadow-xl">
        <div className="relative">
          {/* Image */}
          <div className="aspect-square w-full overflow-hidden bg-gray-100">
            <img
              src={image.imagePath}
              alt={image.prompt}
              className="h-full w-full object-cover object-center"
            />
          </div>
          
          {/* Action buttons overlaid on the image */}
          <div className="absolute bottom-4 right-4 flex space-x-2">
            <Button 
              variant="outline" 
              onClick={onEdit}
              className="bg-white/80 backdrop-blur-sm"
            >
              Edit
            </Button>
            <Button 
              variant="outline" 
              onClick={onRedo}
              className="bg-white/80 backdrop-blur-sm"
            >
              Redo
            </Button>
            <Button 
              variant="primary" 
              onClick={onDone}
              className="bg-indigo-600/90 backdrop-blur-sm"
            >
              Done
            </Button>
          </div>
        </div>
        
        {/* Image metadata */}
        <div className="p-6">
          <div className="mb-6">
            <h2 className="mb-1 text-sm font-medium text-gray-500">PROMPT</h2>
            <p className="text-lg text-gray-900">{image.prompt}</p>
          </div>
          
          {image.negativePrompt && (
            <div className="mb-6">
              <h2 className="mb-1 text-sm font-medium text-gray-500">NEGATIVE PROMPT</h2>
              <p className="text-lg text-gray-900">{image.negativePrompt}</p>
            </div>
          )}
          
          <div className="mb-6">
            <h2 className="mb-2 text-sm font-medium text-gray-500">SPECIFICATIONS</h2>
            <div className="flex flex-wrap gap-2">
              {Object.entries(image.specJson).flatMap(([categoryId, values]) =>
                values.map((value, index) => {
                  const category = getCategoryById(categoryId);
                  return (
                    <Tag
                      key={`${categoryId}-${value}-${index}`}
                      label={value}
                      category={category?.name}
                      color={category?.color}
                      icon={category?.icon ? <span>{category.icon}</span> : undefined}
                    />
                  );
                })
              )}
            </div>
          </div>
          
          <div className="flex items-center justify-between border-t border-gray-200 pt-4 text-sm text-gray-500">
            <div>
              <span className="font-medium">
                {image.actionType === 'generate' ? 'Generated' : 'Edited'}
              </span>{' '}
              on {formatDate(image.createdAt)}
            </div>
            <div>
              ID: {image.id}
              {image.parentId && <span> • Parent: {image.parentId}</span>}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ImagePreview;