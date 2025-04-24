import React from 'react';

interface TagProps {
  label: string;
  category?: string;
  icon?: React.ReactNode;
  color?: string;
  onRemove?: () => void;
  className?: string;
}

const Tag: React.FC<TagProps> = ({ 
  label, 
  category, 
  icon, 
  color = 'bg-gray-100 text-gray-800',
  onRemove,
  className = '' 
}) => {
  return (
    <div className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-medium ${color} ${className}`}>
      {icon && <span className="mr-1">{icon}</span>}
      {category && <span className="mr-1 opacity-70">{category}:</span>}
      <span>{label}</span>
      {onRemove && (
        <button
          type="button"
          onClick={onRemove}
          className="ml-1 rounded-full p-0.5 hover:bg-gray-200 hover:bg-opacity-50 transition-colors"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      )}
    </div>
  );
};

export default Tag;