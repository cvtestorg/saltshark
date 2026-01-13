/**
 * Minion types
 */
export interface MinionStatus {
  id: string;
  os: string | null;
  osrelease: string | null;
  status: string | null;
}

export interface MinionDetail extends MinionStatus {
  grains?: Record<string, any> | null;
  pillars?: Record<string, any> | null;
}

export interface MinionList {
  minions: MinionStatus[];
  total: number;
}

/**
 * Job types
 */
export interface JobStatus {
  jid: string;
  function: string;
  minions: string[];
  start_time: string | null;
  status: string;
}

export interface JobResult extends JobStatus {
  result?: Record<string, any> | null;
  end_time?: string | null;
}

export interface JobList {
  jobs: JobStatus[];
  total: number;
}

export interface JobExecuteRequest {
  target: string;
  function: string;
  args?: string[];
}

/**
 * Grains and Pillars types
 */
export interface GrainsData {
  minion_id: string;
  grains: Record<string, any>;
}

export interface PillarsData {
  minion_id: string;
  pillars: Record<string, any>;
}
