/**
 * Centralized Application Configuration
 * Extracts environment-driven URLs with fallback defaults.
 */
export const config = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080',
  jaegerUrl: import.meta.env.VITE_JAEGER_URL || 'http://localhost:16686',
  langfuseUrl: import.meta.env.VITE_LANGFUSE_URL || 'http://localhost:3100',
  prometheusUrl: import.meta.env.VITE_PROMETHEUS_URL || 'http://localhost:9090',
  grafanaUrl: import.meta.env.VITE_GRAFANA_URL || 'http://localhost:3000',
};

