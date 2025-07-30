#!/bin/bash
set -e

# Show branding
curl -fsSL https://raw.githubusercontent.com/aloshy-ai/branding/main/ascii.sh | bash 2>/dev/null || true

echo "🚀 Starting Deep Job Seek..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if docker-compose is available
if command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
elif docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    echo "❌ Docker Compose is not available. Please install Docker Compose."
    exit 1
fi

# Validate OpenAI API credentials using the Python validator
echo "🔑 Validating OpenAI API credentials..."
python3 src/resume_generator/utils/openai_validator.py
if [ $? -ne 0 ]; then
    echo "❌ OpenAI API validation failed. Please fix the issues above."
    exit 1
fi

# Download docker-compose.yml if it doesn't exist
if [ ! -f "docker-compose.yml" ]; then
    echo "📥 Downloading Docker Compose configuration..."
    curl -sSL -o docker-compose.yml https://raw.githubusercontent.com/aloshy-ai/deep-job-seek/main/docker-compose.dist.yml
fi

# Start services
echo "🔄 Starting services..."
$COMPOSE_CMD up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
timeout=60
while [ $timeout -gt 0 ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Deep Job Seek is ready!"
        echo ""
        echo "🌟 API available at: http://localhost:8000"
        echo "📊 Qdrant dashboard: http://localhost:6333/dashboard"
        echo ""
        echo "🚀 Example usage:"
        echo 'curl -X POST http://localhost:8000/generate \'
        echo '  -H "Content-Type: application/json" \'
        echo '  -d '"'"'{"job_description": "Senior Python Developer with Flask experience"}'"'"''
        echo ""
        echo "🛑 To stop: $COMPOSE_CMD down"
        exit 0
    fi
    sleep 2
    timeout=$((timeout - 2))
done

echo "❌ Services failed to start within 60 seconds"
echo "Check logs with: $COMPOSE_CMD logs"
exit 1