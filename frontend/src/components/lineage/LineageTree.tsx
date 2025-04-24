import React, { useState, useEffect } from 'react';
import { ImageNode, LineageNode } from '../../models/types';
import TreeNode from './TreeNode';

interface LineageTreeProps {
  images: ImageNode[];
  rootId: number;
  activeNodeId?: number;
  onNodeClick: (nodeId: number) => void;
}

const LineageTree: React.FC<LineageTreeProps> = ({ 
  images, 
  rootId,
  activeNodeId,
  onNodeClick
}) => {
  const [lineageTree, setLineageTree] = useState<LineageNode | null>(null);

  // Build the tree from flat image list
  useEffect(() => {
    const buildLineageTree = (images: ImageNode[], rootId: number): LineageNode => {
      const rootNode = images.find(img => img.id === rootId);
      
      if (!rootNode) {
        throw new Error(`Root node with ID ${rootId} not found`);
      }
      
      const findChildren = (parentId: number): LineageNode[] => {
        const children = images
          .filter(img => img.parentId === parentId)
          .map(childImg => ({
            node: childImg,
            children: findChildren(childImg.id)
          }));
        
        return children;
      };
      
      return {
        node: rootNode,
        children: findChildren(rootId)
      };
    };
    
    try {
      const tree = buildLineageTree(images, rootId);
      setLineageTree(tree);
    } catch (error) {
      console.error("Failed to build lineage tree:", error);
    }
  }, [images, rootId]);

  if (!lineageTree) {
    return <div className="flex h-40 items-center justify-center">Loading...</div>;
  }

  return (
    <div className="flex min-h-[200px] w-full overflow-x-auto p-4">
      <div className="mx-auto"> {/* Center the tree */}
        <TreeNode 
          node={lineageTree} 
          activeNodeId={activeNodeId}
          onNodeClick={onNodeClick} 
        />
      </div>
    </div>
  );
};

export default LineageTree;