const defaultApiUrl = typeof window !== 'undefined' && window.location.hostname === '127.0.0.1'
  ? 'http://127.0.0.1:8000'
  : 'http://localhost:8000';

const BASE_URL = import.meta.env.VITE_API_URL || defaultApiUrl;

class ApiService {
  constructor() {
    this.token = localStorage.getItem('traceguard_token') || null;
    this.activeWorkspaceId = localStorage.getItem('traceguard_workspace_id') || 'default-workspace';
  }

  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('traceguard_token', token);
    } else {
      localStorage.removeItem('traceguard_token');
    }
  }

  getToken() {
    return this.token || localStorage.getItem('traceguard_token');
  }

  setWorkspace(workspaceId) {
    this.activeWorkspaceId = workspaceId;
    if (workspaceId) {
      localStorage.setItem('traceguard_workspace_id', workspaceId);
    } else {
      localStorage.removeItem('traceguard_workspace_id');
    }
  }

  getWorkspace() {
    return this.activeWorkspaceId || localStorage.getItem('traceguard_workspace_id') || 'default-workspace';
  }

  async request(endpoint, options = {}) {
    const url = `${BASE_URL}${endpoint}`;
    const headers = {
      ...options.headers,
    };

    if (!(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }

    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const wsId = this.getWorkspace();
    if (wsId) {
      headers['X-Workspace-ID'] = wsId;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (!response.ok) {
        let errorMsg = `HTTP error! Status: ${response.status}`;
        try {
          const errData = await response.json();
          errorMsg = errData.detail || errData.message || errorMsg;
        } catch {
          // ignore json parse error
        }
        const error = new Error(errorMsg);
        error.status = response.status;
        throw error;
      }

      // Check if response has content
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }
      return null;
    } catch (error) {
      console.error(`API Error on ${options.method || 'GET'} ${endpoint}:`, error);
      throw error;
    }
  }

  // Auth & Profile
  async login(username, password) {
    const data = await this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
    if (data.access_token) {
      this.setToken(data.access_token);
      if (data.active_workspace_id) {
        this.setWorkspace(data.active_workspace_id);
      }
    }
    return data;
  }

  async signup(payload) {
    return this.request('/api/auth/signup', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async getMe() {
    return this.request('/api/auth/me');
  }

  async updateMe(payload) {
    return this.request('/api/auth/me', {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
  }

  async changePassword(old_password, new_password) {
    return this.request('/api/auth/change-password', {
      method: 'POST',
      body: JSON.stringify({ old_password, new_password }),
    });
  }

  logout() {
    this.setToken(null);
    this.setWorkspace(null);
    localStorage.removeItem('traceguard_user');
  }

  // Workspaces
  async getWorkspaces() {
    return this.request('/api/auth/workspaces');
  }

  async createWorkspace(name) {
    return this.request('/api/auth/workspaces', {
      method: 'POST',
      body: JSON.stringify({ name }),
    });
  }

  async getWorkspaceDetails(workspace_id) {
    return this.request(`/api/auth/workspaces/${workspace_id}`);
  }

  async addWorkspaceMember(workspace_id, username, role) {
    return this.request(`/api/auth/workspaces/${workspace_id}/members`, {
      method: 'POST',
      body: JSON.stringify({ username, role }),
    });
  }

  // Dashboard
  async getDashboardSummary(timeRange = null) {
    const query = timeRange && timeRange !== 'all' ? `?time_range=${encodeURIComponent(timeRange)}` : '';
    return this.request(`/api/dashboard/summary${query}`);
  }

  // Health
  async getHealth() {
    return this.request('/api/health');
  }

  // Simulation
  async startSimulation(config) {
    return this.request('/api/simulation/start', {
      method: 'POST',
      body: JSON.stringify(config),
    });
  }

  async stopSimulation(simulation_id) {
    return this.request('/api/simulation/stop', {
      method: 'POST',
      body: JSON.stringify({ simulation_id }),
    });
  }

  _cleanParams(params = {}) {
    const cleaned = {};
    for (const [key, value] of Object.entries(params)) {
      if (value !== undefined && value !== null && value !== '' && value !== 'all') {
        cleaned[key] = value;
      }
    }
    return cleaned;
  }

  // Events
  async getEvents(params = {}) {
    const query = new URLSearchParams(this._cleanParams(params)).toString();
    return this.request(`/api/events${query ? `?${query}` : ''}`);
  }

  // Alerts
  async getAlerts(params = {}) {
    const query = new URLSearchParams(this._cleanParams(params)).toString();
    return this.request(`/api/alerts${query ? `?${query}` : ''}`);
  }

  async getAlertDetail(alert_id) {
    return this.request(`/api/alerts/${alert_id}`);
  }

  async getAlertAnalytics(params = {}) {
    const query = new URLSearchParams(this._cleanParams(params)).toString();
    return this.request(`/api/alerts/analytics${query ? `?${query}` : ''}`);
  }

  async updateAlert(alert_id, updateData) {
    return this.request(`/api/alerts/${alert_id}`, {
      method: 'PATCH',
      body: JSON.stringify(updateData),
    });
  }

  // Detection
  async runDetection(payload) {
    return this.request('/api/detection/run', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async getDetectionComparison(dataset_id) {
    return this.request(`/api/detection/compare?dataset_id=${encodeURIComponent(dataset_id)}`);
  }

  // Protocols & Automata Lab
  async getHttpFsm() {
    return this.request('/api/protocols/http/fsm');
  }

  async getFormalAutomaton() {
    return this.request('/api/protocols/http/formal-automaton');
  }

  async stepExecuteAutomaton(events, initialState = null) {
    return this.request('/api/protocols/http/step-execute', {
      method: 'POST',
      body: JSON.stringify({
        events,
        initial_state: initialState,
      }),
    });
  }

  // Datasets
  async getDatasets() {
    return this.request('/api/datasets');
  }

  async uploadDataset(formData) {
    return this.request('/api/datasets/upload', {
      method: 'POST',
      body: formData,
    });
  }

  getDatasetDownloadUrl(dataset_id) {
    return `${BASE_URL}/api/datasets/${dataset_id}/download`;
  }

  // Engine Activity & Attribution
  async getEngineActivity(timeRange = 'all', includeDemo = true) {
    const params = new URLSearchParams();
    if (timeRange) params.append('time_range', timeRange);
    params.append('include_demo', includeDemo ? 'true' : 'false');
    return this.request(`/api/alerts/engine-activity?${params.toString()}`);
  }

  // Live Network Intelligence & PCAP Diagnostics
  async getNetworkStatus() {
    return this.request('/api/network/status');
  }

  async getNetworkInterfaces() {
    return this.request('/api/network/interfaces');
  }

  async runNetworkDiagnostics() {
    return this.request('/api/network/diagnose', {
      method: 'POST',
    });
  }

  async startLiveCapture(interfaceName = 'default') {
    return this.request('/api/network/capture/start', {
      method: 'POST',
      body: JSON.stringify({ interface: interfaceName }),
    });
  }

  async stopLiveCapture() {
    return this.request('/api/network/capture/stop', {
      method: 'POST',
    });
  }

  async clearCaptureSession() {
    return this.request('/api/network/clear', {
      method: 'POST',
    });
  }

  async uploadPcap(file, streamLive = false) {
    const formData = new FormData();
    formData.append('file', file);
    return this.request(`/api/network/pcap/upload?stream_live=${streamLive ? 'true' : 'false'}`, {
      method: 'POST',
      body: formData,
    });
  }

  // Academic Detection Engine Showcase
  async getShowcaseScenarios() {
    return this.request('/api/detection/showcase/scenarios');
  }

  async runShowcaseScenario(scenario, customNotes = null) {
    return this.request('/api/detection/showcase/run', {
      method: 'POST',
      body: JSON.stringify({ scenario, custom_notes: customNotes }),
    });
  }

  async resetShowcaseData() {
    return this.request('/api/detection/showcase/reset', {
      method: 'POST',
    });
  }

  // Academic Detection Benchmark (Targeting 25-35% FSM, 10-20% ML, 45-65% Hybrid)
  async generateBenchmark(seed = 42) {
    return this.request(`/api/detection/benchmark/generate?seed=${seed}`, {
      method: 'POST',
    });
  }

  async getBenchmarkStatus() {
    return this.request('/api/detection/benchmark/status');
  }

  async resetBenchmark() {
    return this.request('/api/detection/benchmark/reset', {
      method: 'POST',
    });
  }
}

export const api = new ApiService();
export default api;
