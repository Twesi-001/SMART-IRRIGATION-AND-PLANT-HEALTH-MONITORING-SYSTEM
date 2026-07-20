/* eslint-disable @typescript-eslint/no-unused-vars */
import React, { useState, useEffect } from 'react';
import { SensorNode } from '../types';
import { nodeService } from '../services/api';
import toast from 'react-hot-toast';

interface NodeSelectorProps {
  selectedNodeId: number | null;
  onSelectNode: (nodeId: number) => void;
  favorites: number[];
  onToggleFavorite: (nodeId: number) => void;
}

const NodeSelector: React.FC<NodeSelectorProps> = ({
  selectedNodeId,
  onSelectNode,
  favorites,
  onToggleFavorite,
}) => {
  const [nodes, setNodes] = useState<SensorNode[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchNodes = async () => {
      try {
        const response = await nodeService.getAll();
        setNodes(response.data);
      } catch (error) {
        toast.error('Failed to load nodes');
      } finally {
        setLoading(false);
      }
    };
    fetchNodes();
  }, []);

  const cropIcons: { [key: string]: string } = {
    'Maize': '🌽',
    'Tomato': '🍅',
    'Cabbage': '🥬',
    'Onion': '🧅',
    'Mango': '🥭',
    'Banana': '🍌',
    'Pineapple': '🍍',
    'Carrot': '🥕',
    'Capsicum': '🫑',
    'Eggplant': '🍆',
    'Sukuma Wiki': '🥬',
    'Spinach': '🌿',
    'Beans': '🫘',
    'Garlic': '🧄',
    'Strawberry': '🍓',
    'Lettuce': '🥗',
    'Cucumber': '🥒',
    'Watermelon': '🍉',
    'Pumpkin': '🎃',
    'Passion Fruit': '🍈',
  };

  const getCropIcon = (cropType: string | null) => {
    if (!cropType) return '🌱';
    return cropIcons[cropType] || '🌱';
  };

  const selectedNode = nodes.find(n => n.id === selectedNodeId);

  return (
    <div className="relative">
      {/* Dropdown Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full md:w-auto px-4 py-2 bg-white border border-gray-300 rounded-lg shadow-sm hover:border-green-500 focus:outline-none focus:ring-2 focus:ring-green-500 flex items-center justify-between min-w-[200px]"
      >
        <span className="flex items-center gap-2">
          {selectedNode ? (
            <>
              {getCropIcon(selectedNode.crop_type)}
              <span>{selectedNode.node_name}</span>
            </>
          ) : (
            <span className="text-gray-500">Select a garden...</span>
          )}
        </span>
        <svg
          className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-50 max-h-60 overflow-y-auto">
          {loading ? (
            <div className="p-4 text-center text-gray-500">Loading...</div>
          ) : nodes.length === 0 ? (
            <div className="p-4 text-center text-gray-500">No gardens found</div>
          ) : (
            nodes.map((node) => {
              const isFavorite = favorites.includes(node.id);
              const isSelected = selectedNodeId === node.id;

              return (
                <div
                  key={node.id}
                  className={`flex items-center justify-between px-4 py-2 hover:bg-gray-50 cursor-pointer ${
                    isSelected ? 'bg-green-50' : ''
                  }`}
                  onClick={() => {
                    onSelectNode(node.id);
                    setIsOpen(false);
                  }}
                >
                  <div className="flex items-center gap-2 flex-1">
                    <span>{getCropIcon(node.crop_type)}</span>
                    <span className="font-medium">{node.node_name}</span>
                    <span className="text-xs text-gray-500">
                      ({node.crop_type || 'Unknown'})
                    </span>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onToggleFavorite(node.id);
                    }}
                    className={`text-xl transition-colors ${
                      isFavorite ? 'text-yellow-500' : 'text-gray-300 hover:text-yellow-400'
                    }`}
                  >
                    {isFavorite ? '★' : '☆'}
                  </button>
                </div>
              );
            })
          )}
        </div>
      )}
    </div>
  );
};

export default NodeSelector;