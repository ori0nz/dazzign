import React, { useState, useEffect } from 'react';
import Button from '../ui/Button';
import TagInput from './TagInput';
import { SPEC_CATEGORIES } from '../../data/mockData';
import { imageService } from '../../services/imageService';
import { useTranslation } from 'react-i18next';

interface PromptFormProps {
  initialPrompt?: string;
  initialSpecs?: Record<string, string[]>;
  parentId?: number | null;
  onSubmit: (data: {
    prompt: string;
    // negativePrompt: string;
    specs: Record<string, string[]>;
    parentId: number | null;
  }) => void;
}

const PromptForm: React.FC<PromptFormProps> = ({
  initialPrompt = '',
  initialSpecs = {},
  parentId = null,
  onSubmit,
}) => {
  const { t } = useTranslation();
  const [prompt, setPrompt] = useState(initialPrompt);
  const [specs, setSpecs] = useState<Record<string, string[]>>(
    SPEC_CATEGORIES.reduce((acc, category) => {
      acc[category.id] = initialSpecs[category.id] || [];
      return acc;
    }, {} as Record<string, string[]>)
  );
  const [isGeneratingSpecs, setIsGeneratingSpecs] = useState(false);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [showErrorModal, setShowErrorModal] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  // Update form values when props change (e.g., when parentImage loads)
  useEffect(() => {
    setPrompt(initialPrompt);
    setSpecs(
      SPEC_CATEGORIES.reduce((acc, category) => {
        acc[category.id] = initialSpecs[category.id] || [];
        return acc;
      }, {} as Record<string, string[]>)
    );
  }, [initialPrompt, initialSpecs]);

  const generateSpecsFromPrompt = async () => {
    if (!prompt.trim()) return;
    
    setIsGeneratingSpecs(true);
    try {
      const generatedSpecs = await imageService.generateSpecs(prompt);
      console.log("Generated specs:", generatedSpecs);
      // Ensure all values are arrays
      const sanitizedSpecs = Object.entries(generatedSpecs.attributes).reduce((acc, [key, value]) => {
        acc[key] = Array.isArray(value) ? value : (value ? [value] : []);
        return acc;
      }, {} as Record<string, string[]>);
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

  // Add a function to check if specs are valid
  const hasValidSpecs = () => {
    return Object.values(specs).some(values => values.length > 0);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Check if specs are empty
    if (!hasValidSpecs()) {
      setErrorMessage(t('prompt.errorNoSpecs'));
      setShowErrorModal(true);
      return;
    }
    
    // Show custom confirmation modal
    setShowConfirmModal(true);
  };
  
  const handleConfirm = () => {
    setShowConfirmModal(false);
    onSubmit({
      prompt,
      // negativePrompt: structuredPrompt,
      specs,
      parentId,
    });
  };
  
  const handleCancel = () => {
    setShowConfirmModal(false);
  };

  const closeErrorModal = () => {
    setShowErrorModal(false);
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

      <div className="flex justify-end">
        <Button 
          type="submit" 
          variant="primary" 
          size="lg"
          disabled={!hasValidSpecs() || !prompt.trim()}
          className="transition-transform hover:scale-105"
        >
          Generate Image
        </Button>
      </div>
      
      {/* Confirmation Modal */}
      {showConfirmModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="w-full max-w-md overflow-hidden rounded-lg bg-white p-6 shadow-xl">
            <div className="mb-4 text-center">
              <h3 className="text-lg font-medium text-gray-900">{t('prompt.confirmGeneration')}</h3>
              <p className="mt-2 text-sm text-gray-500">
                {t('prompt.confirmGenerationDesc')}
              </p>
            </div>
            
            <div className="mt-6 flex justify-end space-x-3">
              <button
                type="button"
                onClick={handleCancel}
                className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
              >
                {t('common.cancel')}
              </button>
              <button
                type="button"
                onClick={handleConfirm}
                className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
              >
                {t('common.confirm')}
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Error Modal */}
      {showErrorModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="w-full max-w-md overflow-hidden rounded-lg bg-white p-6 shadow-xl">
            <div className="mb-4 text-center">
              <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-red-100">
                <svg className="h-6 w-6 text-red-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900">{t('common.error')}</h3>
              <p className="mt-2 text-sm text-gray-500">
                {errorMessage}
              </p>
            </div>
            
            <div className="mt-6 flex justify-center">
              <button
                type="button"
                onClick={closeErrorModal}
                className="rounded-md bg-red-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
              >
                {t('common.ok')}
              </button>
            </div>
          </div>
        </div>
      )}
    </form>
  );
};

export default PromptForm;