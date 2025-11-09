import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', redirectTo: '/dashboard', pathMatch: 'full' },
  {
    path: 'dashboard',
    loadComponent: () => import('./components/dashboard/dashboard.component').then(m => m.DashboardComponent)
  },
  {
    path: 'agents',
    loadComponent: () => import('./components/agents/agents.component').then(m => m.AgentsComponent)
  },
  {
    path: 'trading',
    loadComponent: () => import('./components/trading/trading.component').then(m => m.TradingComponent)
  },
  {
    path: 'settings',
    loadComponent: () => import('./components/settings/settings.component').then(m => m.SettingsComponent)
  }
];
