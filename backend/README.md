# Backend

## Setup

```bash
cp backend/.env.example backend/.env
```

#### Backend `.env` file:

```bash
AWS_BEARER_TOKEN_BEDROCK=your_bedrock_token_here
DYNAMODB_ENDPOINT=http://localhost:8000
MCP_ENDPOINT=localhost:6000
```

#### Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
cd ..
```

