// Define types for our application

export interface ImageNode {
  id: number;
  isRoot: boolean;
  parentId: number | null;
  prompt: string;
  negativePrompt: string | null;
  specJson: Record<string, string[]>;
  requestParams: Record<string, any>;
  imageBase64: string;
  imagePath: string;
  actionType: 'generate' | 'edit';
  createdAt: string;
}

export interface SpecCategory {
  id: string;
  name: string;
  icon: string;
  color: string;
}

export interface Tag {
  category: string;
  value: string;
}

export interface LineageNode {
  node: ImageNode;
  children: LineageNode[];
}