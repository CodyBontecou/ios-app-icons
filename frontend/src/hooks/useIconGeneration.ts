import { useMutation, useQuery } from '@tanstack/react-query';
import { useState, useEffect, useCallback } from 'react';
import api from '../api/client';
import type { GenerateRequest } from '../api/types';

export function useConfig() {
  return useQuery({
    queryKey: ['config'],
    queryFn: api.getConfig,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

export function useGenerateIcons() {
  const [jobId, setJobId] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: api.generate,
    onSuccess: (data) => {
      setJobId(data.job_id);
    },
  });

  const reset = useCallback(() => {
    setJobId(null);
    mutation.reset();
  }, [mutation]);

  return {
    ...mutation,
    jobId,
    reset,
  };
}

export function useJobStatus(jobId: string | null) {
  const [pollInterval, setPollInterval] = useState<number | false>(false);

  const query = useQuery({
    queryKey: ['jobStatus', jobId],
    queryFn: () => (jobId ? api.getJobStatus(jobId) : Promise.reject('No job ID')),
    enabled: !!jobId,
    refetchInterval: pollInterval,
  });

  // Manage polling based on job status
  useEffect(() => {
    if (!jobId) {
      setPollInterval(false);
      return;
    }

    const status = query.data?.status;

    if (status === 'pending' || status === 'processing') {
      setPollInterval(1000); // Poll every second while in progress
    } else {
      setPollInterval(false); // Stop polling when complete or failed
    }
  }, [jobId, query.data?.status]);

  return query;
}

export function useIconGenerationFlow() {
  const config = useConfig();
  const generation = useGenerateIcons();
  const jobStatus = useJobStatus(generation.jobId);

  const startGeneration = useCallback(
    (request: GenerateRequest) => {
      generation.reset();
      generation.mutate(request);
    },
    [generation]
  );

  const isGenerating =
    generation.isPending ||
    jobStatus.data?.status === 'pending' ||
    jobStatus.data?.status === 'processing';

  const isComplete = jobStatus.data?.status === 'completed';
  const isFailed = jobStatus.data?.status === 'failed';

  return {
    config,
    startGeneration,
    isGenerating,
    isComplete,
    isFailed,
    jobStatus: jobStatus.data,
    error: generation.error || (isFailed ? new Error(jobStatus.data?.error || 'Generation failed') : null),
    reset: generation.reset,
  };
}
