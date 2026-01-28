import { useState, type FormEvent } from 'react';
import type { GenerateRequest, IconStyle, ConfigResponse } from '../api/types';

interface IconGeneratorFormProps {
  config: ConfigResponse | undefined;
  onSubmit: (request: GenerateRequest) => void;
  isLoading: boolean;
}

export function IconGeneratorForm({ config, onSubmit, isLoading }: IconGeneratorFormProps) {
  const [subject, setSubject] = useState('');
  const [style, setStyle] = useState<IconStyle>('ios');
  const [customStyle, setCustomStyle] = useState('');
  const [variations, setVariations] = useState(config?.default_variations || 4);
  const [steps, setSteps] = useState(config?.default_steps || 30);
  const [guidanceScale, setGuidanceScale] = useState(config?.default_guidance_scale || 7.0);
  const [removeBg, setRemoveBg] = useState(false);
  const [applyMask, setApplyMask] = useState(true);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();

    const request: GenerateRequest = {
      subject,
      style,
      variations,
      steps,
      guidance_scale: guidanceScale,
      remove_bg: removeBg,
      apply_mask: applyMask,
    };

    if (style === 'custom' && customStyle) {
      request.custom_style = customStyle;
    }

    onSubmit(request);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Subject Input */}
      <div>
        <label htmlFor="subject" className="block text-sm font-medium text-gray-700 mb-1">
          What should the icon show?
        </label>
        <input
          type="text"
          id="subject"
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
          placeholder="e.g., happy cat, mountain landscape, health app"
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          required
          disabled={isLoading}
        />
      </div>

      {/* Style Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Style</label>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {(['ios', 'flat', 'vector', 'custom'] as IconStyle[]).map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => setStyle(s)}
              disabled={isLoading}
              className={`px-4 py-2 rounded-lg font-medium capitalize transition-all ${
                style === s
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              } disabled:opacity-50`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {/* Custom Style Input */}
      {style === 'custom' && (
        <div>
          <label htmlFor="customStyle" className="block text-sm font-medium text-gray-700 mb-1">
            Custom Style Prompt
          </label>
          <textarea
            id="customStyle"
            value={customStyle}
            onChange={(e) => setCustomStyle(e.target.value)}
            placeholder="Describe the artistic style in detail..."
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent min-h-[100px]"
            required={style === 'custom'}
            disabled={isLoading}
          />
        </div>
      )}

      {/* Variations Slider */}
      <div>
        <label htmlFor="variations" className="block text-sm font-medium text-gray-700 mb-1">
          Variations: {variations}
        </label>
        <input
          type="range"
          id="variations"
          min="1"
          max={config?.max_variations || 8}
          value={variations}
          onChange={(e) => setVariations(parseInt(e.target.value))}
          className="w-full"
          disabled={isLoading}
        />
      </div>

      {/* Advanced Options Toggle */}
      <button
        type="button"
        onClick={() => setShowAdvanced(!showAdvanced)}
        className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
      >
        {showAdvanced ? '▼' : '▶'} Advanced Options
      </button>

      {/* Advanced Options */}
      {showAdvanced && (
        <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
          {/* Steps */}
          <div>
            <label htmlFor="steps" className="block text-sm font-medium text-gray-700 mb-1">
              Inference Steps: {steps}
            </label>
            <input
              type="range"
              id="steps"
              min="10"
              max="100"
              value={steps}
              onChange={(e) => setSteps(parseInt(e.target.value))}
              className="w-full"
              disabled={isLoading}
            />
            <p className="text-xs text-gray-500 mt-1">Higher = better quality, slower generation</p>
          </div>

          {/* Guidance Scale */}
          <div>
            <label htmlFor="guidanceScale" className="block text-sm font-medium text-gray-700 mb-1">
              Guidance Scale: {guidanceScale.toFixed(1)}
            </label>
            <input
              type="range"
              id="guidanceScale"
              min="1"
              max="20"
              step="0.5"
              value={guidanceScale}
              onChange={(e) => setGuidanceScale(parseFloat(e.target.value))}
              className="w-full"
              disabled={isLoading}
            />
            <p className="text-xs text-gray-500 mt-1">Higher = follows prompt more closely</p>
          </div>

          {/* Processing Options */}
          <div className="flex flex-col gap-2">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={applyMask}
                onChange={(e) => setApplyMask(e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded"
                disabled={isLoading}
              />
              <span className="text-sm text-gray-700">Apply iOS rounded corners</span>
            </label>

            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={removeBg}
                onChange={(e) => setRemoveBg(e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded"
                disabled={isLoading}
              />
              <span className="text-sm text-gray-700">Remove background</span>
            </label>
          </div>
        </div>
      )}

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isLoading || !subject.trim() || (style === 'custom' && !customStyle.trim())}
        className="w-full py-3 px-4 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
      >
        {isLoading ? 'Generating...' : 'Generate Icons'}
      </button>
    </form>
  );
}
