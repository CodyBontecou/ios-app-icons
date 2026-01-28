import { useState } from 'react';
import type { VariantInfo } from '../api/types';

interface IconGalleryProps {
  variants: VariantInfo[];
  subject: string;
}

export function IconGallery({ variants, subject }: IconGalleryProps) {
  const [selectedVariant, setSelectedVariant] = useState<number>(0);
  const [selectedSize, setSelectedSize] = useState<number | null>(null);

  if (variants.length === 0) {
    return null;
  }

  const currentVariant = variants[selectedVariant];
  const processedIcons = currentVariant?.processed_icons || [];

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Generated Icons</h3>

      {/* Subject */}
      <p className="text-sm text-gray-500 mb-4">
        Subject: <span className="font-medium text-gray-700">{subject}</span>
      </p>

      {/* Variant Selector */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select Variant ({variants.length} available)
        </label>
        <div className="flex gap-2 overflow-x-auto pb-2">
          {variants.map((variant, index) => (
            <button
              key={variant.variant_number}
              onClick={() => {
                setSelectedVariant(index);
                setSelectedSize(null);
              }}
              className={`flex-shrink-0 w-20 h-20 rounded-xl overflow-hidden border-2 transition-all ${
                selectedVariant === index
                  ? 'border-blue-500 ring-2 ring-blue-200'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <img
                src={variant.original_url}
                alt={`Variant ${variant.variant_number}`}
                className="w-full h-full object-cover"
              />
            </button>
          ))}
        </div>
      </div>

      {/* Main Preview */}
      <div className="mb-6">
        <div className="aspect-square max-w-md mx-auto rounded-2xl overflow-hidden bg-gray-100 shadow-lg">
          <img
            src={
              selectedSize
                ? processedIcons.find((i) => i.size === selectedSize)?.url || currentVariant.original_url
                : currentVariant.original_url
            }
            alt={`${subject} icon`}
            className="w-full h-full object-contain"
          />
        </div>
        <p className="text-center text-sm text-gray-500 mt-2">
          {selectedSize ? `${selectedSize}x${selectedSize}` : 'Original (1024x1024)'}
        </p>
      </div>

      {/* Processed Sizes */}
      {processedIcons.length > 0 && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            iOS App Icon Sizes
          </label>
          <div className="grid grid-cols-5 sm:grid-cols-10 gap-2">
            <button
              onClick={() => setSelectedSize(null)}
              className={`flex flex-col items-center p-2 rounded-lg transition-all ${
                selectedSize === null
                  ? 'bg-blue-100 border-2 border-blue-500'
                  : 'bg-gray-50 border-2 border-transparent hover:bg-gray-100'
              }`}
            >
              <span className="text-xs font-medium">1024</span>
              <span className="text-[10px] text-gray-500">Original</span>
            </button>
            {processedIcons.map((icon) => (
              <button
                key={icon.size}
                onClick={() => setSelectedSize(icon.size)}
                className={`flex flex-col items-center p-2 rounded-lg transition-all ${
                  selectedSize === icon.size
                    ? 'bg-blue-100 border-2 border-blue-500'
                    : 'bg-gray-50 border-2 border-transparent hover:bg-gray-100'
                }`}
              >
                <span className="text-xs font-medium">{icon.size}</span>
                <span className="text-[10px] text-gray-500">px</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Download Section */}
      <div className="mt-6 pt-6 border-t border-gray-100">
        <div className="flex flex-wrap gap-2">
          <a
            href={currentVariant.original_url}
            download={`${subject}-variant-${currentVariant.variant_number}-original.png`}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <DownloadIcon />
            Download Original
          </a>
          {selectedSize && (
            <a
              href={processedIcons.find((i) => i.size === selectedSize)?.url}
              download={`${subject}-variant-${currentVariant.variant_number}-${selectedSize}px.png`}
              className="inline-flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              <DownloadIcon />
              Download {selectedSize}px
            </a>
          )}
        </div>
      </div>
    </div>
  );
}

function DownloadIcon() {
  return (
    <svg
      className="w-4 h-4"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth={2}
        d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
      />
    </svg>
  );
}
