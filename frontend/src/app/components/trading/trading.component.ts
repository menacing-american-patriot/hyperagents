import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-trading',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="trading-page">
      <h1>Trading Interface</h1>
      <p>Advanced trading controls and market analysis interface coming soon...</p>
    </div>
  `,
  styles: [`
    .trading-page {
      padding: 2rem;
      max-width: 1400px;
      margin: 0 auto;
      
      h1 {
        color: #1f2937;
        margin-bottom: 1rem;
      }
    }
  `]
})
export class TradingComponent {}
