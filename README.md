# HyperAgents - AI Trading System

A sophisticated AI-powered trading system that uses multiple specialized agents to coordinate, strategize, and execute trades on the Hyperliquid exchange. Built with LangChain, OpenAI, and Angular.

## 🚀 Features

- **Multi-Agent Architecture**: Specialized AI agents for market analysis, risk management, strategy development, and execution
- **Real-time Dashboard**: Angular-based web interface with live updates and system monitoring
- **Hyperliquid Integration**: Direct integration with Hyperliquid exchange for trading
- **Configurable AI Models**: Support for OpenAI and compatible providers with custom base URLs
- **Risk Management**: Comprehensive risk controls and position management
- **Strategy Development**: AI-powered strategy creation and adaptation
- **WebSocket Communication**: Real-time updates between backend and frontend

## 🏗️ Architecture

### Backend (Python)

- **Coordination Agent**: Master orchestrator managing all other agents
- **Market Analysis Agent**: Technical analysis and sentiment evaluation
- **Risk Management Agent**: Position sizing and risk assessment
- **Strategy Agent**: AI-powered strategy development and execution
- **Execution Agent**: Order management and trade execution
- **FastAPI Server**: REST API and WebSocket endpoints

### Frontend (Angular)

- **Dashboard**: Real-time system overview and controls
- **Agent Monitoring**: Individual agent status and performance
- **Trading Interface**: Market data and trading controls
- **Settings**: Configuration management

## 📋 Prerequisites

- Python 3.12+
- Node.js 18+
- OpenAI API key (or compatible provider)
- Hyperliquid account (testnet supported)

## 🛠️ Installation

### 1. Clone the Repository

```bash
gh repo clone menacing-american-patriot/hyperagents
cd hyperagents
```

### 2. Backend Setup

```bash
# Install Python dependencies
pip install -e .

# Or using uv (recommended)
uv sync
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

### 4. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env
```

Required environment variables:

- `OPENAI_API_KEY`: Your OpenAI API key
- `HYPERLIQUID_PRIVATE_KEY`: Your Hyperliquid private key (optional for read-only mode)
- `INITIAL_CAPITAL`: Starting capital amount
- Other trading and risk parameters

## 🚀 Running the System

### Start Backend

```bash
# Option 1: Using the run script
python run_backend.py

# Option 2: Using uvicorn directly
uvicorn backend.api.main:app --host localhost --port 8000 --reload
```

### Start Frontend

```bash
# Option 1: Using the run script
./run_frontend.sh

# Option 2: Using npm directly
cd frontend
npm start
```

The system will be available at:

- Frontend: <http://localhost:4200>
- Backend API: <http://localhost:8000>
- API Documentation: <http://localhost:8000/docs>

## 🎯 Usage

### 1. System Startup

1. Start the backend server
2. Start the frontend application
3. Navigate to the dashboard at <http://localhost:4200>

### 2. Configuration

1. Go to Settings to configure:
   - OpenAI API settings
   - Trading parameters
   - Risk management limits
   - Hyperliquid connection

### 3. Trading Operations

1. **Start Trading Session**: Activates all agents and begins monitoring
2. **Develop Strategy**: AI creates new trading strategies based on market conditions
3. **Monitor Agents**: View real-time status of all AI agents
4. **Risk Management**: Monitor exposure and risk metrics

### 4. Dashboard Features

- **System Status**: Trading session state and performance metrics
- **AI Agents**: Real-time status of all specialized agents
- **Trading Signals**: Current market analysis and recommendations
- **Positions**: Active trading positions and P&L
- **Risk Metrics**: Exposure levels and risk compliance

## 🔧 Configuration

### OpenAI Settings

```env
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.openai.com/v1  # Or custom provider
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.1
```

### Trading Parameters

```env
INITIAL_CAPITAL=1000.0
MAX_POSITION_SIZE=0.1          # 10% of capital per position
MAX_DAILY_LOSS=0.05           # 5% daily loss limit
STOP_LOSS_PERCENTAGE=0.02     # 2% stop loss
TAKE_PROFIT_PERCENTAGE=0.04   # 4% take profit
```

### Hyperliquid Settings

```env
HYPERLIQUID_PRIVATE_KEY=your_private_key
HYPERLIQUID_TESTNET=true      # Use testnet for development
```

## 🧪 Testing

### Backend Tests

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/agents/
pytest tests/api/
pytest tests/integration/
```

### Frontend Tests

```bash
cd frontend
npm test
```

## 📊 Agent Details

### Coordination Agent

- Orchestrates all other agents
- Manages trading sessions
- Handles inter-agent communication
- Makes final trading decisions

### Market Analysis Agent

- Technical analysis (RSI, moving averages, support/resistance)
- AI-powered sentiment analysis
- Real-time market data processing
- Trading signal generation

### Risk Management Agent

- Position sizing calculations
- Risk limit monitoring
- Stop-loss and take-profit management
- Portfolio exposure tracking

### Strategy Agent

- AI-powered strategy development
- Market regime adaptation
- Strategy performance tracking
- Backtesting capabilities

### Execution Agent

- Order placement and management
- Position monitoring
- Trade execution reporting
- Risk alert handling

## 🔒 Security Considerations

- Store API keys securely in environment variables
- Use testnet for development and testing
- Implement proper position sizing and risk limits
- Monitor system performance continuously
- Regular backup of configuration and logs

## 🐛 Troubleshooting

### Common Issues

1. **Backend won't start**
   - Check Python dependencies: `pip install -e .`
   - Verify environment variables in `.env`
   - Check port availability (8000)

2. **Frontend connection issues**
   - Ensure backend is running on port 8000
   - Check CORS settings in backend
   - Verify API_URL in frontend environment

3. **Trading not working**
   - Verify Hyperliquid private key
   - Check account balance and permissions
   - Review risk management settings

4. **AI agents not responding**
   - Verify OpenAI API key and quota
   - Check base URL for custom providers
   - Review agent logs for errors

### Logs and Debugging

- Backend logs: Check console output or configure file logging
- Frontend logs: Browser developer console
- Agent actions: Logged with timestamps and details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

Intellisol LLC, all rights reserved.

## ⚠️ Disclaimer

This software is for gambling and fun purposes. Trading cryptocurrencies involves substantial risk of lots of fun. Use at your own risk, don't be a pussy and never trade with money you wanna buy gay dildos or something with bc thats probably what the ai that wrote the framework was thinking when it wrote this NGMI rant. Always test thoroughly on production before using test funds.

## 🆘 Support

For issues and questions:

1. Check the troubleshooting section
2. Review existing GitHub issues
3. Create a new issue with detailed information
4. Include logs and configuration (without sensitive data)
