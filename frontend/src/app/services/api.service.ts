import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { environment } from '../../environments/environment';

export interface AgentStatus {
  name: string;
  description: string;
  created_at: string;
  last_action_at: string | null;
  message_count: number;
}

export interface TradingSignal {
  symbol: string;
  action: string;
  confidence: number;
  timestamp: string;
}

export interface Position {
  symbol: string;
  size: number;
  entry_price: number;
  unrealized_pnl: number;
  position_value: number;
}

export interface MarketAnalysis {
  symbol: string;
  current_price: number;
  timestamp: string;
  technical_analysis: any;
  sentiment_analysis: any;
  recommendation: any;
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = environment.apiUrl || 'http://localhost:8000';
  private websocket: WebSocket | null = null;
  private websocketSubject = new BehaviorSubject<any>(null);

  constructor(private http: HttpClient) {
    this.connectWebSocket();
  }

  // WebSocket connection
  connectWebSocket(): void {
    const wsUrl = this.baseUrl.replace('http', 'ws') + '/ws';
    this.websocket = new WebSocket(wsUrl);

    this.websocket.onopen = () => {
      console.log('WebSocket connected');
    };

    this.websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.websocketSubject.next(data);
    };

    this.websocket.onclose = () => {
      console.log('WebSocket disconnected, attempting to reconnect...');
      setTimeout(() => this.connectWebSocket(), 5000);
    };

    this.websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }

  getWebSocketMessages(): Observable<any> {
    return this.websocketSubject.asObservable();
  }

  // API endpoints
  getHealth(): Observable<any> {
    return this.http.get(`${this.baseUrl}/health`);
  }

  getAgentsStatus(): Observable<any> {
    return this.http.get(`${this.baseUrl}/agents/status`);
  }

  startTrading(): Observable<any> {
    return this.http.post(`${this.baseUrl}/trading/start`, {});
  }

  stopTrading(): Observable<any> {
    return this.http.post(`${this.baseUrl}/trading/stop`, {});
  }

  getMarketAnalysis(symbol: string): Observable<MarketAnalysis> {
    return this.http.get<MarketAnalysis>(`${this.baseUrl}/market/analysis/${symbol}`);
  }

  getTradingSignals(): Observable<any> {
    return this.http.get(`${this.baseUrl}/market/signals`);
  }

  getPositions(): Observable<any> {
    return this.http.get(`${this.baseUrl}/positions`);
  }

  getRiskStatus(): Observable<any> {
    return this.http.get(`${this.baseUrl}/risk/status`);
  }

  developStrategy(parameters?: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/strategies/develop`, parameters || {});
  }
}
