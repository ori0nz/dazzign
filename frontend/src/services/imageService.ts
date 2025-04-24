import { ImageNode } from '../models/types';
import { MOCK_IMAGES } from '../data/mockData';

const API_BASE = 'http://localhost:8000/node';

class ImageService {
  // Get all root images (those with no parent)
  async getRootImages(): Promise<ImageNode[]> {
    try {
      const response = await fetch(`${API_BASE}/root`);
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
      const response = await fetch(`${API_BASE}/${id}`);
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
      const response = await fetch(`${API_BASE}/${id}/tree`);
      if (!response.ok) {
        throw new Error('Failed to fetch image lineage');
      }
      const data = await response.json();
      console.log("data", datass);
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
        id: MOCK_IMAGES.length + 1,
        url: 'https://picsum.photos/400/400', // Placeholder image
        prompt: data.prompt,
        negativePrompt: data.negativePrompt,
        specs: data.specs,
        parentId: data.parentId,
        createdAt: new Date().toISOString(),
      };
      MOCK_IMAGES.push(newImage);
      return newImage;
    }
  }
}

// Export a singleton instance
export const imageService = new ImageService();