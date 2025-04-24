import React, { useState } from 'react';
import Button from '../ui/Button';
import TagInput from './TagInput';
import { SPEC_CATEGORIES } from '../../data/mockData';
import { Tag } from '../../models/types';

interface PromptFormProps {
  initialPrompt?: string;
  initialNegativePrompt?: string;
  initialSpecs?: Record<string, string[]>;
  parentId?: number | null;
  onSubmit: (data: {
    prompt: string;
    negativePrompt: string;
    specs: Record<string, string[]>;
    parentId: number | null;
  }) => void;
}

const PromptForm: React.FC<PromptFormProps> = ({
  initialPrompt = '',
  initialNegativePrompt = '',
  initialSpecs = {},
  parentId = null,
  onSubmit,
}) => {
  const [prompt, setPrompt] = useState(initialPrompt);
  const [negativePrompt, setNegativePrompt] = useState(initialNegativePrompt);
  const [specs, setSpecs] = useState<Record<string, string[]>>(
    SPEC_CATEGORIES.reduce((acc, category) => {
      acc[category.id] = initialSpecs[category.id] || [];
      return acc;
    }, {} as Record<string, string[]>)
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      prompt,
      negativePrompt,
      specs,
      parentId,
    });
  };

  const handleSpecChange = (categoryId: string, values: string[]) => {
    setSpecs(prev => ({
      ...prev,
      [categoryId]: values,
    }));
  };

  // Generate a preview prompt with all the specs
  const generatePreviewPrompt = () => {
    const allTags: Tag[] = [];
    
    Object.entries(specs).forEach(([categoryId, values]) => {
      values.forEach(value => {
        allTags.push({ category: categoryId, value });
      });
    });
    
    if (allTags.length === 0) return prompt;
    
    const specsText = Object.entries(specs)
      .filter(([_, values]) => values.length > 0)
      .map(([categoryId, values]) => {
        const category = SPEC_CATEGORIES.find(c => c.id === categoryId);
        return `${values.join(', ')} ${category?.name.toLowerCase()}`;
      })
      .join('; ');
    
    return `A high-resolution render of ${prompt}${prompt ? '; ' : ''}${specsText}.`;
  };

  return (
    <form onSubmit={handleSubmit} className="mx-auto max-w-3xl">
      <div className="mb-6">
        <label htmlFor="prompt" className="mb-2 block text-lg font-medium text-gray-900">
          Main Prompt:
        </label>
        <textarea
          id="prompt"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          className="block w-full rounded-lg border border-gray-300 bg-white p-2.5 text-gray-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
          placeholder="Describe what you want to generate..."
          rows={3}
        />
      </div>

      {SPEC_CATEGORIES.map((category) => (
        <TagInput
          key={category.id}
          category={category}
          values={specs[category.id]}
          onChange={(values) => handleSpecChange(category.id, values)}
        />
      ))}

      <div className="mb-6">
        <label htmlFor="preview" className="mb-2 block text-lg font-medium text-gray-900">
          Preview:
        </label>
        <div className="rounded-lg border border-gray-300 bg-gray-50 p-4 text-gray-700">
          {generatePreviewPrompt()}
        </div>
      </div>

      <div className="mb-6">
        <label htmlFor="negative-prompt" className="mb-2 flex items-center text-lg font-medium text-gray-900">
          <span className="mr-2">⛔</span> Negative Prompt:
        </label>
        <textarea
          id="negative-prompt"
          value={negativePrompt}
          onChange={(e) => setNegativePrompt(e.target.value)}
          className="block w-full rounded-lg border border-gray-300 bg-white p-2.5 text-gray-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
          placeholder="What to avoid in the generation..."
          rows={2}
        />
      </div>

      <div className="flex justify-end">
        <Button 
          type="submit" 
          variant="primary" 
          size="lg"
          className="transition-transform hover:scale-105"
        >
          Generate Image
        </Button>
      </div>
    </form>
  );
};

export default PromptForm;