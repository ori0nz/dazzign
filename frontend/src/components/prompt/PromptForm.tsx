import React, { useState, useEffect } from 'react';
import Button from '../ui/Button';
import TagInput from './TagInput';
import { SPEC_CATEGORIES } from '../../data/mockData';
import { imageService } from '../../services/imageService';

interface PromptFormProps {
  initialPrompt?: string;
  initialStructuredPrompt?: string;
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
  initialStructuredPrompt = '',
  initialSpecs = {},
  parentId = null,
  onSubmit,
}) => {
  const [prompt, setPrompt] = useState(initialPrompt);
  const [structuredPrompt, setStructuredPrompt] = useState(initialStructuredPrompt);
  const [specs, setSpecs] = useState<Record<string, string[]>>(
    SPEC_CATEGORIES.reduce((acc, category) => {
      acc[category.id] = initialSpecs[category.id] || [];
      return acc;
    }, {} as Record<string, string[]>)
  );
  const [isGeneratingSpecs, setIsGeneratingSpecs] = useState(false);

  // Update form values when props change (e.g., when parentImage loads)
  useEffect(() => {
    setPrompt(initialPrompt);
    setStructuredPrompt(initialStructuredPrompt);
    setSpecs(
      SPEC_CATEGORIES.reduce((acc, category) => {
        acc[category.id] = initialSpecs[category.id] || [];
        return acc;
      }, {} as Record<string, string[]>)
    );
  }, [initialPrompt, initialStructuredPrompt, initialSpecs]);

  const generateSpecsFromPrompt = async () => {
    if (!prompt.trim()) return;
    
    setIsGeneratingSpecs(true);
    try {
      const generatedSpecs = await imageService.generateSpecs(prompt);
      const structuredPrompt = generatedSpecs.structuredPrompt;
      console.log("Generated specs:", generatedSpecs);
      // Ensure all values are arrays
      const sanitizedSpecs = Object.entries(generatedSpecs.attributes).reduce((acc, [key, value]) => {
        acc[key] = Array.isArray(value) ? value : (value ? [value] : []);
        return acc;
      }, {} as Record<string, string[]>);
      setStructuredPrompt(typeof structuredPrompt === 'string' ? structuredPrompt : Array.isArray(structuredPrompt) ? structuredPrompt.join(' ') : '');
      setSpecs(sanitizedSpecs);
    } catch (error) {
      console.error('Failed to generate specifications:', error);
    } finally {
      setIsGeneratingSpecs(false);
    }
  };

  const handlePromptChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setPrompt(e.target.value);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      prompt,
      negativePrompt: structuredPrompt,
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
  // const generatePreviewPrompt = () => {
  //   const allTags: Tag[] = [];
    
  //   Object.entries(specs).forEach(([categoryId, values]) => {
  //     // Ensure values is an array before calling forEach
  //     if (Array.isArray(values)) {
  //       values.forEach(value => {
  //         allTags.push({ category: categoryId, value });
  //       });
  //     }
  //   });
  //   console.log("All tags:", allTags);
  //   if (allTags.length === 0) return prompt;
    
  //   const specsText = Object.entries(specs)
  //     .filter(([, values]) => Array.isArray(values) && values.length > 0)
  //     .map(([categoryId, values]) => {
  //       const category = SPEC_CATEGORIES.find(c => c.id === categoryId);
  //       return `${values.join(', ')} ${category?.name.toLowerCase()}`;
  //     })
  //     .join('; ');
    
  //   return `A high-resolution render of ${prompt}${prompt ? '; ' : ''}${specsText}.`;
  // };

  return (
    <form onSubmit={handleSubmit} className="mx-auto max-w-3xl">
      <div className="mb-6">
        <label htmlFor="prompt" className="mb-2 block text-lg font-medium text-gray-900">
          Main Prompt:
        </label>
        <div className="space-y-2">
          <textarea
            id="prompt"
            value={prompt}
            onChange={handlePromptChange}
            className="block w-full rounded-lg border border-gray-300 bg-white p-2.5 text-gray-900 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
            placeholder="Describe what you want to generate..."
            rows={3}
          />
          <Button
            type="button"
            variant="outline"
            onClick={generateSpecsFromPrompt}
            disabled={!prompt.trim() || isGeneratingSpecs}
            className="w-full sm:w-auto"
          >
            {isGeneratingSpecs ? 'Generating...' : 'Generate Specifications'}
          </Button>
        </div>
      </div>

      {SPEC_CATEGORIES.map((category) => (
        <TagInput
          key={category.id}
          category={category}
          values={specs[category.id] || []}
          onChange={(values) => handleSpecChange(category.id, values)}
        />
      ))}
      
      {/* <div className="mb-6">
        <label htmlFor="preview" className="mb-2 block text-lg font-medium text-gray-900">
          Preview:
        </label>
        <div className="rounded-lg border border-gray-300 bg-gray-50 p-4 text-gray-700">
          {generatePreviewPrompt()}
        </div>
      </div> */}

      <div className="mb-6">
        <label htmlFor="structured-prompt" className="mb-2 flex items-center text-lg font-medium text-gray-900">
          <span className="mr-2">🪄</span> Structured Prompt:
        </label>
        <textarea
          id="structured-prompt"
          value={structuredPrompt}
          onChange={(e) => setStructuredPrompt(e.target.value)}
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