import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';
import { Subscription, interval } from 'rxjs';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent implements OnInit, OnDestroy {
  agentsStatus: any = null;
  tradingSignals: any = null;
  positions: any = null;
  riskStatus: any = null;
  loading = true;
  error: string | null = null;
  
  private subscriptions: Subscription[] = [];

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.loadDashboardData();
    
    // Refresh data every 10 seconds
    const refreshSub = interval(10000).subscribe(() => {
      this.loadDashboardData();
    });
    this.subscriptions.push(refreshSub);

    // Listen to WebSocket updates
    const wsSub = this.apiService.getWebSocketMessages().subscribe(message => {
      if (message) {
        this.handleWebSocketMessage(message);
      }
    });
    this.subscriptions.push(wsSub);
  }

  ngOnDestroy() {
    this.subscriptions.forEach(sub => sub.unsubscribe());
  }

  loadDashboardData() {
    this.loading = true;
    this.error = null;

    // Load all dashboard data in parallel
    Promise.all([
      this.apiService.getAgentsStatus().toPromise(),
      this.apiService.getTradingSignals().toPromise(),
      this.apiService.getPositions().toPromise(),
      this.apiService.getRiskStatus().toPromise()
    ]).then(([agents, signals, positions, risk]) => {
      this.agentsStatus = agents;
      this.tradingSignals = signals;
      this.positions = positions;
      this.riskStatus = risk;
      this.loading = false;
    }).catch(error => {
      this.error = 'Failed to load dashboard data';
      this.loading = false;
      console.error('Dashboard error:', error);
    });
  }

  handleWebSocketMessage(message: any) {
    switch (message.type) {
      case 'trading_session':
        this.loadDashboardData(); // Refresh all data
        break;
      case 'market_update':
        // Update market data
        break;
      case 'agent_status':
        // Update specific agent status
        break;
    }
  }

  startTrading() {
    this.apiService.startTrading().subscribe({
      next: (response) => {
        console.log('Trading started:', response);
        this.loadDashboardData();
      },
      error: (error) => {
        console.error('Error starting trading:', error);
        this.error = 'Failed to start trading session';
      }
    });
  }

  stopTrading() {
    this.apiService.stopTrading().subscribe({
      next: (response) => {
        console.log('Trading stopped:', response);
        this.loadDashboardData();
      },
      error: (error) => {
        console.error('Error stopping trading:', error);
        this.error = 'Failed to stop trading session';
      }
    });
  }

  developStrategy() {
    this.apiService.developStrategy().subscribe({
      next: (response) => {
        console.log('Strategy developed:', response);
        // Could show a modal or navigate to strategy details
      },
      error: (error) => {
        console.error('Error developing strategy:', error);
        this.error = 'Failed to develop strategy';
      }
    });
  }

  getAgentStatusClass(agent: any): string {
    if (!agent.last_action_at) return 'idle';
    
    const lastAction = new Date(agent.last_action_at);
    const now = new Date();
    const timeDiff = now.getTime() - lastAction.getTime();
    const minutesDiff = timeDiff / (1000 * 60);
    
    if (minutesDiff < 5) return 'active';
    if (minutesDiff < 30) return 'recent';
    return 'idle';
  }

  formatCurrency(value: number): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  }

  formatPercentage(value: number): string {
    return new Intl.NumberFormat('en-US', {
      style: 'percent',
      minimumFractionDigits: 2
    }).format(value);
  }
}
