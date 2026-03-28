export type NavSection =
  | "dashboard"
  | "products"
  | "reviews"
  | "content-ai"
  | "inventory"
  | "settings";

export interface HealthResponse {
  status: string;
  database?: string;
  redis?: string;
  version?: string;
}

export interface WorkflowListResponse {
  total: number;
  category: string | null;
  workflows: Record<string, unknown>;
}
