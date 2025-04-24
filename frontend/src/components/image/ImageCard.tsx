import React from 'react';
import { ImageNode } from '../../models/types';
import Tag from '../ui/Tag';
import { SPEC_CATEGORIES } from '../../data/mockData';

interface ImageCardProps {
  image: ImageNode;
  onClick: () => void;
}

const ImageCard: React.FC<ImageCardProps> = ({ image, onClick }) => {
  // Format relative time
  const getRelativeTime = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffSecs = Math.floor(diffMs / 1000);
    const diffMins = Math.floor(diffSecs / 60);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffDays > 0) {
      return `${diffDays}d ago`;
    } else if (diffHours > 0) {
      return `${diffHours}h ago`;
    } else if (diffMins > 0) {
      return `${diffMins}m ago`;
    } else {
      return 'Just now';
    }
  };

  // Get top 5 tags to display
  const getTopTags = () => {
    const allTags: { category: string; value: string }[] = [];
    
    Object.entries(image.specJson).forEach(([category, values]) => {
      values.forEach(value => {
        const categoryObj = SPEC_CATEGORIES.find(c => c.id === category);
        if (categoryObj) {
          allTags.push({
            category,
            value,
          });
        }
      });
    });
    
    return allTags.slice(0, 5);
  };

  const topTags = getTopTags();

  return (
    <div 
      className="group cursor-pointer overflow-hidden rounded-lg bg-white shadow-md transition-all hover:shadow-lg"
      onClick={onClick}
    >
      <div className="relative aspect-square">
        <img 
          // src={image.imagePath} 
          src={`data:image/png;base64,${image.imageBase64}`}
          alt={image.prompt}
          className="h-full w-full object-cover object-center transition-transform duration-300 group-hover:scale-105"
        />
        <div className="absolute top-2 right-2 rounded-full bg-gray-800 bg-opacity-75 px-2 py-1 text-xs font-medium text-white">
          {image.actionType === 'generate' ? 'Generated' : 'Edited'}
        </div>
      </div>
      
      <div className="p-4">
        <div className="mb-2 flex flex-wrap gap-1">
          {topTags.map((tag, index) => {
            const categoryObj = SPEC_CATEGORIES.find(c => c.id === tag.category);
            return (
              <Tag
                key={`${tag.category}-${tag.value}-${index}`}
                label={tag.value}
                color={categoryObj?.color}
                className="text-xs"
              />
            );
          })}
        </div>
        
        <h3 className="mb-1 line-clamp-2 text-sm font-medium text-gray-800">
          {image.prompt}
        </h3>
        
        <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
          <span>{getRelativeTime(image.createdAt)}</span>
          <span>ID: {image.id}</span>
        </div>
      </div>
    </div>
  );
};

export default ImageCard;