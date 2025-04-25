import { ImageNode } from '../models/types';
import { MOCK_IMAGES } from '../data/mockData';

const API_BASE = 'http://localhost:8000';

class ImageService {
  // Get all root images (those with no parent)
  async getRootImages(): Promise<ImageNode[]> {
    try {
      const response = await fetch(`${API_BASE}/node/root`);
      if (!response.ok) {
        throw new Error('Failed to fetch root images');
      }
      const data = await response.json();
      const images = data.nodes;
      return images;
    } catch (error) {
      console.warn('Failed to fetch from API, using mock data:', error);
      // Filter mock images to only return root images (those with no parent)
      return MOCK_IMAGES.filter(img => !img.parentId);
    }
  }

  // Get a single image by ID
  async getImageById(id: number): Promise<ImageNode | null> {
    try {
      const response = await fetch(`${API_BASE}/node/${id}`);
      if (!response.ok) {
        if (response.status === 404) {
          return null;
        }
        throw new Error('Failed to fetch image');
      }
      return response.json();
    } catch (error) {
      console.warn('Failed to fetch from API, using mock data:', error);
      return MOCK_IMAGES.find(img => img.id === id) || null;
    }
  }

  // Get image lineage (all descendants)
  async getImageLineage(id: number): Promise<ImageNode[]> {
    try {
      const response = await fetch(`${API_BASE}/node/${id}/tree`);
      if (!response.ok) {
        throw new Error('Failed to fetch image lineage');
      }
      const data = await response.json();
      // console.log("data", data);
      return data;
    } catch (error) {
      console.warn('Failed to fetch from API, using mock data:', error);
      // Get all descendants recursively from mock data
      const getDescendants = (parentId: number): ImageNode[] => {
        const children = MOCK_IMAGES.filter(img => img.parentId === parentId);
        return children.reduce((acc, child) => [...acc, child, ...getDescendants(child.id)], [] as ImageNode[]);
      };
      return getDescendants(id);
    }
  }

    // Generate specifications from prompt
    async generateSpecs(prompt: string): Promise<Record<string, string[]>> {
      try {
        const response = await fetch(`${API_BASE}/text-gen/to-spec`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ prompt }),
        });
        
        if (!response.ok) {
          throw new Error('Failed to generate specifications');
        }
        const data = await response.json();
        console.log("Generated specs response:", data.attributes);
        return data.attributes;
      } catch (error) {
        console.warn('Failed to fetch from API, using mock data:', error);
        // Return some mock specifications based on the prompt
        return {
          style: ['mock-Modern', 'mock-Minimalist'],
          material: ['mock-Metal', 'mock-Glass'],
          lighting: ['mock-Natural', 'mock-Ambient'],
          features: ['mock-Clean lines', 'mock-Simple geometry'],
        };
      }
    }

  // Create a new image
  async generateImage(data: {
    prompt: string;
    negativePrompt: string;
    specs: Record<string, string[]>;
    parentId: number | null;
  }): Promise<ImageNode> {
    try {
      const response = await fetch(`${API_BASE}/images/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: data.prompt,
          negative_prompt: data.negativePrompt,
          spec_json: data.specs,
          parent_id: data.parentId,
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to generate image');
      }
      
      return response.json();
    } catch (error) {
      console.warn('Failed to fetch from API, using mock data:', error);
      // Create a new mock image
      const newImage: ImageNode = {
        id: Math.max(...MOCK_IMAGES.map(img => img.id)) + 1,
        isRoot: !data.parentId,
        parentId: data.parentId,
        prompt: data.prompt,
        negativePrompt: data.negativePrompt,
        specJson: data.specs,
        requestParams: { width: 1024, height: 1024 },
        imagePath: MOCK_IMAGES[Math.floor(Math.random() * MOCK_IMAGES.length)].imagePath,
        imageBase64: '',
        actionType: data.parentId ? 'edit' : 'generate',
        createdAt: new Date().toISOString(),
      };
      MOCK_IMAGES.push(newImage);
      return newImage;
    }
  }
}

// Export a singleton instance
export const imageService = new ImageService();