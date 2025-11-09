import { Component, OnInit, signal } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { CommonModule } from '@angular/common';
import { ApiService } from './services/api.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RouterLinkActive, CommonModule],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App implements OnInit {
  protected readonly title = signal('HyperAgents');
  isSystemOnline = false;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.checkSystemHealth();

    // Check health every 30 seconds
    setInterval(() => {
      this.checkSystemHealth();
    }, 30000);
  }

  private checkSystemHealth() {
    this.apiService.getHealth().subscribe({
      next: (response) => {
        this.isSystemOnline = response.status === 'healthy';
      },
      error: () => {
        this.isSystemOnline = false;
      }
    });
  }
}
