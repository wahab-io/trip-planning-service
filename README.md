# Trip Planning Service

A comprehensive AI-powered trip planning application that provides personalized recommendations for lodging, food, and travel arrangements. Built with a modern microservices architecture using AWS CDK, FastAPI, Next.js, and integrated with AI agents for intelligent recommendations.

## 🏗️ Architecture

The application follows a microservices architecture with the following components:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │  Flights MCP    │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│    Server       │
│   Port: 3000    │    │   Port: 8080    │    │   Port: 6000    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       │
         │              ┌─────────────────┐              │
         │              │   DynamoDB      │              │
         │              │   (Local)       │              │
         │              │   Port: 8000    │              │
         │              └─────────────────┘              │
         │                       │                       │
         │                       ▼                       │
         │              ┌─────────────────┐              │
         │              │  DynamoDB       │              │
         │              │  Dashboard      │              │
         │              │  Port: 4567     │              │
         │              └─────────────────┘              │
         │                                               │
         └───────────────────────────────────────────────┘
                    AI Agents Integration
                 (AWS Bedrock Models)
```

### Components Overview

- **Frontend**: Next.js 15 application with React 19, TypeScript, and Tailwind CSS
- **Backend**: FastAPI application with AI agent integration using Strands SDK
- **Flights MCP Server**: Model Context Protocol server for flight search using Duffel API
- **Database**: DynamoDB (local development) for storing trip plans and recommendations
- **AI Integration**: AWS Bedrock models (Claude, DeepSeek) for generating recommendations
- **Infrastructure**: AWS CDK for cloud deployment with ECS Fargate services

## 🚀 Features

### Core Functionality

- **Trip Planning**: Create and manage trip plans with origin, destination, dates, and budget
- **AI-Powered Recommendations**:
  - **Lodging**: Hotel and accommodation suggestions
  - **Food**: Restaurant and dining recommendations
  - **Travel**: Flight search and local transportation advice
- **Real-time Streaming**: Live AI-generated recommendations with streaming responses
- **Trip History**: Persistent storage of trip plans and generated recommendations

### AI Capabilities

- **Multi-Model Support**: Integration with Claude 3.7 Sonnet and DeepSeek R1 models
- **Context-Aware Recommendations**: AI agents consider budget, dates, and destination
- **Flight Search Integration**: Real-time flight data through Duffel API
- **Streaming Responses**: Real-time recommendation generation with progress feedback

## 📋 Prerequisites

### Required Software

- **Node.js** (v18 or higher)
- **Python** (v3.12 or higher)
- **Finch**
- **AWS CLI** (configured with appropriate credentials)
- **uv** (Python package manager)

### Required API Keys

- **AWS Bedrock Access**: Bearer token for AWS Bedrock models
- **Duffel API Key**: For flight search functionality (live or test key)

### Environment Setup

Create the following environment files:

#### Root `.env` file:

```bash
AWS_BEARER_TOKEN_BEDROCK=your_bedrock_token_here
DUFFEL_API_KEY_LIVE=your_duffel_api_key_here
```

#### Backend `.env` file:

```bash
AWS_BEARER_TOKEN_BEDROCK=your_bedrock_token_here
DYNAMODB_ENDPOINT=http://localhost:8000
MCP_ENDPOINT=localhost:6000
```

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd trip-planning-service
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env
cp backend/.env.example backend/.env

# Edit the .env files with your API keys
```

### 3. Install Dependencies

#### Root Dependencies (CDK)

```bash
npm install
pip install -r requirements.txt
```

#### Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

#### Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
cd ..
```

#### Flights MCP Server Dependencies

```bash
cd flights-mcp
uv sync
cd ..
```

## 🚀 Running the Application

### Development Mode (Recommended)

#### Option 1: Docker Compose (Full Stack)

```bash
# Start all services
finch compose up --build

# With file watching for development
finch compose up --build --watch
```

#### Option 2: Individual Services

```bash
# Terminal 1: Start DynamoDB
finch run -p 8000:8000 amazon/dynamodb-local -jar DynamoDBLocal.jar -sharedDb -inMemory

# Terminal 2: Start Flights MCP Server
cd flights-mcp
uv run flights-mcp

# Terminal 3: Start Backend
cd backend
python -m uvicorn main:app --reload --port 8080

# Terminal 4: Start Frontend
cd frontend
npm run dev
```

### Production Mode

```bash
# Build and start all services
finch compose -f docker-compose.yml up --build -d
```

## 🌐 Service Endpoints

| Service            | URL                   | Description              |
| ------------------ | --------------------- | ------------------------ |
| Frontend           | http://localhost:3000 | Next.js web application  |
| Backend API        | http://localhost:8080 | FastAPI REST API         |
| DynamoDB           | http://localhost:8000 | Local DynamoDB instance  |
| DynamoDB Dashboard | http://localhost:4567 | Web UI for DynamoDB      |
| Flights MCP        | http://localhost:6000 | Flight search MCP server |

## 📚 API Documentation

### Backend API Endpoints

#### Trip Management

- `POST /plan` - Create a new trip plan
- `GET /plan/{id}` - Retrieve trip plan by ID

#### AI Recommendations (Streaming)

- `GET /plan/{id}/recommendation/lodging` - Get lodging recommendations
- `GET /plan/{id}/recommendation/food` - Get food recommendations
- `GET /plan/{id}/recommendation/travel` - Get travel recommendations

### Request/Response Examples

#### Create Trip Plan

```bash
curl -X POST http://localhost:8080/plan \
  -H "Content-Type: application/json" \
  -d '{
    "id": "trip-123",
    "origin": "SFO",
    "destination": "NYC",
    "from_date": "2024-12-01",
    "to_date": "2024-12-07",
    "budget": 2000
  }'
```

#### Get Streaming Recommendations

```bash
curl -N http://localhost:8080/plan/trip-123/recommendation/lodging
```

## 🏗️ Infrastructure Deployment

### AWS CDK Deployment

#### Prerequisites

- AWS CLI configured with appropriate permissions
- CDK bootstrapped in your AWS account

#### Deploy to AWS

```bash
# Install CDK globally
npm install

# Bootstrap CDK (first time only)
npx cdk bootstrap

# Deploy backend stack
npx cdk deploy Backend

# Deploy frontend stack
npx cdk deploy Frontend

# Deploy both stacks
npx cdk deploy --all
```

#### CDK Stacks

- **Backend Stack**: ECS Fargate service for FastAPI backend
- **Frontend Stack**: ECS Fargate service for Next.js frontend

## 🧪 Testing

### Backend Tests

```bash
cd backend
python -m pytest tests/
```

### Frontend Tests

```bash
cd frontend
npm test
```

## 🔧 Development

### Project Structure

```
trip-planning-service/
├── backend/                 # FastAPI backend service
│   ├── main.py             # FastAPI application entry point
│   ├── service.py          # Trip planning service logic
│   ├── component.py        # CDK backend stack definition
│   ├── Dockerfile          # Backend container configuration
│   └── requirements.txt    # Python dependencies
├── frontend/               # Next.js frontend application
│   ├── src/                # Source code
│   │   ├── app/           # Next.js app router pages
│   │   ├── components/    # React components
│   │   ├── hooks/         # Custom React hooks
│   │   └── lib/           # Utility libraries
│   ├── component.py       # CDK frontend stack definition
│   ├── Dockerfile         # Frontend container configuration
│   └── package.json       # Node.js dependencies
├── flights-mcp/           # MCP server for flight search
│   ├── src/               # MCP server source code
│   ├── Dockerfile         # MCP server container
│   └── pyproject.toml     # Python project configuration
├── app.py                 # CDK application entry point
├── docker-compose.yml     # Multi-service container orchestration
├── cdk.json              # CDK configuration
└── requirements.txt      # CDK Python dependencies
```

### Adding New Features

#### Backend API Endpoints

1. Add new routes in `backend/main.py`
2. Implement business logic in `backend/service.py`
3. Update API documentation

#### Frontend Components

1. Create components in `frontend/src/components/`
2. Add pages in `frontend/src/app/`
3. Update routing as needed

#### AI Agents

1. Configure new models in agent initialization
2. Update system prompts for specific use cases
3. Add new recommendation types

## 🔍 Monitoring & Debugging

### Logs

```bash
# View all service logs
finch compose logs -f

# View specific service logs
finch compose logs -f backend
finch compose logs -f frontend
finch compose logs -f flights-mcp
```

### Health Checks

- Backend: http://localhost:8080/docs (FastAPI auto-docs)
- Frontend: http://localhost:3000 (Next.js app)
- DynamoDB: http://localhost:4567 (Dashboard)

### MCP Inspector (for Flights MCP)

```bash
npx @modelcontextprotocol/inspector uv --directory ./flights-mcp run flights-mcp
```

## 🚨 Troubleshooting

### Common Issues

#### Port Conflicts

```bash
# Check port usage
lsof -i :3000  # Frontend
lsof -i :8080  # Backend
lsof -i :8000  # DynamoDB
lsof -i :6000  # Flights MCP
```

#### Environment Variables

- Ensure all required environment variables are set
- Check `.env` files are properly configured
- Verify API keys are valid and have necessary permissions

#### Docker Issues

```bash
# Clean up containers and images
docker-compose down -v
docker system prune -a

# Rebuild from scratch
docker-compose up --build --force-recreate
```

#### DynamoDB Connection

- Ensure DynamoDB container is running
- Check endpoint configuration in backend service
- Verify table creation permissions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **AWS Bedrock** for AI model access
- **Duffel API** for flight search capabilities
- **Strands SDK** for AI agent integration
- **Next.js** and **FastAPI** for the application framework
- **AWS CDK** for infrastructure as code

## 📞 Support

For support and questions:

- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation at http://localhost:8080/docs

---

**Happy Trip Planning! ✈️🏨🍽️**
