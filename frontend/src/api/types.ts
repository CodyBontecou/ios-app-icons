// API Types matching the FastAPI backend models

export type IconStyle = 'ios' | 'flat' | 'vector' | 'custom';

export type JobStatus = 'pending' | 'processing' | 'completed' | 'failed';

export interface GenerateRequest {
  subject: string;
  style?: IconStyle;
  custom_style?: string;
  variations?: number;
  color?: string;
  steps?: number;
  guidance_scale?: number;
  remove_bg?: boolean;
  apply_mask?: boolean;
}

export interface GenerateResponse {
  job_id: string;
  status: JobStatus;
  message: string;
}

export interface IconInfo {
  size: number;
  filename: string;
  url: string;
}

export interface VariantInfo {
  variant_number: number;
  original_url: string;
  processed_icons: IconInfo[];
}

export interface JobStatusResponse {
  job_id: string;
  status: JobStatus;
  progress: number;
  message: string;
  created_at: string;
  completed_at: string | null;
  subject: string;
  style: string;
  variants: VariantInfo[];
  error: string | null;
  metadata: Record<string, unknown> | null;
}

export interface ConfigResponse {
  styles: string[];
  ios_icon_sizes: number[];
  default_steps: number;
  default_guidance_scale: number;
  default_variations: number;
  max_variations: number;
}

export interface HealthResponse {
  status: string;
  api_configured: boolean;
}
