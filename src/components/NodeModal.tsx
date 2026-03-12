import { Building2, Trash2, X } from 'lucide-react';
import { NodeType } from '../types';

interface NodeModalProps {
  onSelect: (type: NodeType) => void;
  onClose: () => void;
}

export default function NodeModal({ onSelect, onClose }: NodeModalProps) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl p-6 max-w-sm w-full mx-4">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Select Node Type</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        <div className="space-y-3">
          <button
            onClick={() => onSelect('hospital')}
            className="w-full flex items-center gap-3 p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-all"
          >
            <Building2 className="text-blue-600" size={24} />
            <div className="text-left">
              <div className="font-medium text-gray-900">Hospital</div>
              <div className="text-sm text-gray-500">Waste collection point</div>
            </div>
          </button>

          <button
            onClick={() => onSelect('disposal')}
            className="w-full flex items-center gap-3 p-4 border-2 border-gray-200 rounded-lg hover:border-green-500 hover:bg-green-50 transition-all"
          >
            <Trash2 className="text-green-600" size={24} />
            <div className="text-left">
              <div className="font-medium text-gray-900">Disposal Center</div>
              <div className="text-sm text-gray-500">Waste disposal point</div>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
}
