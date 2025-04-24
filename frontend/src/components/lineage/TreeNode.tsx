import React from 'react';
import { LineageNode } from '../../models/types';

interface TreeNodeProps {
  node: LineageNode;
  activeNodeId?: number;
  onNodeClick: (nodeId: number) => void;
}

const TreeNode: React.FC<TreeNodeProps> = ({ 
  node, 
  activeNodeId,
  onNodeClick 
}) => {
  const isActive = node.node.id === activeNodeId;
  
  return (
    <div className="flex flex-col items-center">
      {/* Node itself */}
      <div 
        className={`
          relative mb-2 cursor-pointer rounded-lg border-2 p-1 transition-all
          ${isActive 
            ? 'border-indigo-500 ring-2 ring-indigo-300' 
            : 'border-gray-200 hover:border-indigo-300'}
        `}
        onClick={() => onNodeClick(node.node.id)}
      >
        <div className="relative h-16 w-16 overflow-hidden rounded">
          <img 
            src={node.node.imagePath} 
            alt={node.node.prompt} 
            className="h-full w-full object-cover"
          />
          <div className="absolute bottom-0 left-0 right-0 bg-black bg-opacity-60 px-1 py-0.5 text-center text-xs text-white">
            {node.node.actionType === 'generate' ? 'Gen' : 'Edit'}
          </div>
        </div>
      </div>
      
      {/* Children */}
      {node.children.length > 0 && (
        <div className="relative mt-6 flex items-start gap-6">
          {/* Vertical line from parent to children connector */}
          <div className="absolute top-[-24px] left-1/2 h-6 w-0.5 -translate-x-1/2 bg-gray-300"></div>
          
          {/* Horizontal line connecting all children */}
          {node.children.length > 1 && (
            <div className="absolute top-[-6px] left-0 right-0 h-0.5 bg-gray-300"></div>
          )}
          
          {node.children.map((child) => (
            <div key={child.node.id} className="relative flex flex-col items-center">
              {/* Vertical line to each child */}
              <div className="absolute top-[-6px] left-1/2 h-6 w-0.5 -translate-x-1/2 bg-gray-300"></div>
              
              <TreeNode 
                node={child} 
                activeNodeId={activeNodeId}
                onNodeClick={onNodeClick} 
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default TreeNode;