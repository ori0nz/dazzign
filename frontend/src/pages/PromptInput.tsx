import React from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import PromptForm from '../components/prompt/PromptForm';
import { imageService } from '../services/imageService';

const PromptInput: React.FC = () => {
  const navigate = useNavigate();
  const { parentId } = useParams<{ parentId?: string }>();
  const parsedParentId = parentId ? parseInt(parentId, 10) : null;

  const handleSubmit = async (data: {
    prompt: string;
    negativePrompt: string;
    specs: Record<string, string[]>;
    parentId: number | null;
  }) => {
    try {
      const newImage = await imageService.generateImage({
        ...data,
        parentId: parsedParentId,
      });
      
      // Navigate to the preview page for the new image
      navigate(`/preview/${newImage.id}`);
    } catch (error) {
      console.error("Failed to generate image:", error);
      // In a real app, you'd show a proper error message to the user
      alert("Failed to generate image. Please try again.");
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="mb-2 text-3xl font-bold text-gray-900">
          {parsedParentId ? 'Edit Image' : 'Create New Image'}
        </h1>
        <p className="text-gray-600">
          {parsedParentId 
            ? 'Modify the prompt and specifications to create a variation of the selected image.' 
            : 'Enter a prompt and specifications to generate a new image.'}
        </p>
      </div>
      
      <PromptForm 
        parentId={parsedParentId}
        onSubmit={handleSubmit}
      />
    </div>
  );
};

export default PromptInput;