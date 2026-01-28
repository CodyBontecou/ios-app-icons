import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { IconGeneratorForm, JobProgress, IconGallery } from './components';
import { useIconGenerationFlow } from './hooks/useIconGeneration';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function IconGeneratorApp() {
  const {
    config,
    startGeneration,
    isGenerating,
    isComplete,
    isFailed,
    jobStatus,
    error,
    reset,
  } = useIconGenerationFlow();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-4xl mx-auto px-4 py-6">
          <h1 className="text-2xl font-bold text-gray-900">iOS App Icon Generator</h1>
          <p className="text-gray-600 mt-1">AI-powered icon generation using Stable Diffusion</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="space-y-6">
          {/* Generation Form */}
          {!isGenerating && !isComplete && (
            <div className="bg-white rounded-lg shadow-md p-6">
              <IconGeneratorForm
                config={config.data}
                onSubmit={startGeneration}
                isLoading={isGenerating || config.isLoading}
              />
            </div>
          )}

          {/* Progress Indicator */}
          {(isGenerating || isFailed) && (
            <JobProgress jobStatus={jobStatus} isLoading={isGenerating} />
          )}

          {/* Error with retry */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-700">{error.message}</p>
              <button
                onClick={reset}
                className="mt-2 text-sm text-red-600 hover:text-red-800 underline"
              >
                Try again
              </button>
            </div>
          )}

          {/* Results Gallery */}
          {isComplete && jobStatus && (
            <>
              <IconGallery
                variants={jobStatus.variants}
                subject={jobStatus.subject}
              />

              {/* Generate More Button */}
              <div className="text-center">
                <button
                  onClick={reset}
                  className="inline-flex items-center gap-2 px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  Generate More Icons
                </button>
              </div>
            </>
          )}

          {/* API Status */}
          {config.isError && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <p className="text-yellow-700">
                Unable to connect to the API server. Make sure the backend is running on{' '}
                <code className="bg-yellow-100 px-1 rounded">http://localhost:8000</code>
              </p>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="max-w-4xl mx-auto px-4 py-8 text-center text-gray-500 text-sm">
        <p>Powered by Replicate SDXL</p>
      </footer>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <IconGeneratorApp />
    </QueryClientProvider>
  );
}

export default App;
