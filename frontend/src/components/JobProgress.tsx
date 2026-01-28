import type { JobStatusResponse } from '../api/types';

interface JobProgressProps {
  jobStatus: JobStatusResponse | undefined;
  isLoading: boolean;
}

export function JobProgress({ jobStatus, isLoading }: JobProgressProps) {
  if (!jobStatus && !isLoading) {
    return null;
  }

  const status = jobStatus?.status || 'pending';
  const progress = jobStatus?.progress || 0;
  const message = jobStatus?.message || 'Initializing...';

  const getStatusColor = () => {
    switch (status) {
      case 'completed':
        return 'bg-green-500';
      case 'failed':
        return 'bg-red-500';
      case 'processing':
        return 'bg-blue-500';
      default:
        return 'bg-yellow-500';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'completed':
        return '✓';
      case 'failed':
        return '✕';
      case 'processing':
        return '◌';
      default:
        return '◦';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-lg font-medium text-gray-900">Generation Progress</h3>
        <span
          className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium text-white ${getStatusColor()}`}
        >
          {getStatusIcon()} {status}
        </span>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-gray-200 rounded-full h-3 mb-3">
        <div
          className={`h-3 rounded-full transition-all duration-300 ${getStatusColor()}`}
          style={{ width: `${progress}%` }}
        />
      </div>

      {/* Progress Details */}
      <div className="flex items-center justify-between text-sm">
        <span className="text-gray-600">{message}</span>
        <span className="text-gray-500 font-medium">{progress}%</span>
      </div>

      {/* Error Message */}
      {status === 'failed' && jobStatus?.error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-700">{jobStatus.error}</p>
        </div>
      )}

      {/* Subject being generated */}
      {jobStatus?.subject && (
        <div className="mt-4 pt-4 border-t border-gray-100">
          <p className="text-sm text-gray-500">
            Generating: <span className="font-medium text-gray-700">{jobStatus.subject}</span>
          </p>
        </div>
      )}
    </div>
  );
}
