import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="settings-page">
      <h1>System Settings</h1>
      <p>Configuration interface for OpenAI API, trading parameters, and risk management coming soon...</p>
    </div>
  `,
  styles: [`
    .settings-page {
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
export class SettingsComponent {}
