import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-agents',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="agents-page">
      <h1>AI Agents Management</h1>
      <p>Detailed agent monitoring and control interface coming soon...</p>
    </div>
  `,
  styles: [`
    .agents-page {
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
export class AgentsComponent {}
