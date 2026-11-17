class WebSocketService {
  constructor() {
    this.ws = null;
    const defaultWsUrl = typeof window !== 'undefined' && window.location.hostname === '127.0.0.1'
      ? 'ws://127.0.0.1:8000/ws/events'
      : 'ws://localhost:8000/ws/events';
    this.url = import.meta.env.VITE_WS_URL || defaultWsUrl;
    this.listeners = new Map(); // type -> Set(callbacks)
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 20;
    this.reconnectDelay = 2000;
    this.isExplicitlyClosed = false;
    this.statusListeners = new Set();
  }

  connect() {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    this.isExplicitlyClosed = false;
    this._notifyStatus('connecting');

    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        this.reconnectAttempts = 0;
        this._notifyStatus('connected');
        // Automatically subscribe to core channels
        this.send({
          action: 'subscribe',
          channels: ['events', 'alerts', 'stats', 'simulation_status']
        });
      };

      this.ws.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          this._dispatch(parsed.type || 'message', parsed.data || parsed);
          // Also dispatch wildcard
          this._dispatch('*', parsed);
        } catch (err) {
          console.warn('[WS] Parse error:', err);
        }
      };

      this.ws.onerror = (err) => {
        this._notifyStatus('error');
      };

      this.ws.onclose = () => {
        this._notifyStatus('disconnected');
        if (!this.isExplicitlyClosed) {
          this._scheduleReconnect();
        }
      };
    } catch (err) {
      this._notifyStatus('error');
      this._scheduleReconnect();
    }
  }

  _scheduleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = Math.min(this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts - 1), 30000);
      setTimeout(() => {
        if (!this.isExplicitlyClosed) {
          this.connect();
        }
      }, delay);
    }
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(typeof data === 'string' ? data : JSON.stringify(data));
      return true;
    }
    return false;
  }

  on(type, callback) {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, new Set());
    }
    this.listeners.get(type).add(callback);
    return () => this.off(type, callback);
  }

  off(type, callback) {
    if (this.listeners.has(type)) {
      this.listeners.get(type).delete(callback);
    }
  }

  onStatusChange(callback) {
    this.statusListeners.add(callback);
    return () => this.statusListeners.delete(callback);
  }

  getStatus() {
    if (!this.ws) return 'disconnected';
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'connecting';
      case WebSocket.OPEN:
        return 'connected';
      case WebSocket.CLOSING:
      case WebSocket.CLOSED:
      default:
        return 'disconnected';
    }
  }

  _notifyStatus(status) {
    this.statusListeners.forEach((cb) => {
      try { cb(status); } catch (e) { console.error(e); }
    });
  }

  _dispatch(type, data) {
    if (this.listeners.has(type)) {
      this.listeners.get(type).forEach((cb) => {
        try { cb(data); } catch (e) { console.error(e); }
      });
    }
  }

  disconnect() {
    this.isExplicitlyClosed = true;
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this._notifyStatus('disconnected');
  }
}

export const wsService = new WebSocketService();
export default wsService;
