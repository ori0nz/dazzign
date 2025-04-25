import React, { useState, useRef, useEffect } from 'react';
import Tag from '../ui/Tag';
import { SpecCategory } from '../../models/types';

interface TagInputProps {
  category: SpecCategory;
  values?: string[];
  onChange: (values: string[]) => void;
  placeholder?: string;
}

const TagInput: React.FC<TagInputProps> = ({
  category,
  values = [], // Provide default empty array
  onChange,
  placeholder = 'Type and press Enter...',
}) => {
  const [inputValue, setInputValue] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(e.target.value);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && inputValue.trim()) {
      e.preventDefault();
      if (!values.includes(inputValue.trim())) {
        onChange([...values, inputValue.trim()]);
      }
      setInputValue('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    onChange(values.filter(tag => tag !== tagToRemove));
  };

  const focusInput = () => {
    inputRef.current?.focus();
  };

  // Auto-focus the input when clicking anywhere in the container
  useEffect(() => {
    const handleContainerClick = () => {
      inputRef.current?.focus();
    };
    
    const container = inputRef.current?.parentElement;
    container?.addEventListener('click', handleContainerClick);
    
    return () => {
      container?.removeEventListener('click', handleContainerClick);
    };
  }, []);

  return (
    <div className="mb-6">
      <label 
        htmlFor={`tag-input-${category.id}`} 
        className="mb-2 flex items-center text-lg font-medium text-gray-900"
      >
        <span className="mr-2">{category.icon}</span> {category.name}:
      </label>
      <div 
        className="flex flex-wrap items-center gap-2 rounded-lg border border-gray-300 bg-white p-2 focus-within:border-indigo-500 focus-within:ring-1 focus-within:ring-indigo-500"
        onClick={focusInput}
      >
        {values.map((tag, index) => (
          <Tag
            key={`${tag}-${index}`}
            label={tag}
            color={category.color}
            onRemove={() => removeTag(tag)}
          />
        ))}
        <input
          id={`tag-input-${category.id}`}
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          className="flex-grow border-0 bg-transparent p-1 text-gray-900 focus:outline-none focus:ring-0"
          placeholder={values.length ? `Type and press Enter to add multiple values` : placeholder}
        />
      </div>
    </div>
  );
};

export default TagInput;