# Deployment Guide

This document explains the CI/CD pipeline and deployment process for Deep Job Seek.

## 🚀 CI/CD Pipeline Overview

The project uses GitHub Actions for automated testing, building, and deployment:

### Workflows

1. **`ci-cd.yml`** - Main CI/CD pipeline
2. **`release.yml`** - Release automation
3. **`test-quickstart.yml`** - Quick Start method testing

## 📋 Pipeline Stages

### 1. Test Stage
- Runs on every push and PR
- Sets up Python 3.10 environment
- Starts Qdrant service for testing
- Installs dependencies and runs pytest
- Uploads coverage reports to Codecov

### 2. Build and Push Stage
- Runs after tests pass (except on PRs)
- Builds multi-platform Docker images (AMD64 + ARM64)
- Pushes to GitHub Container Registry (`ghcr.io`)
- Uses buildx cache for faster builds

### 3. Security Scan Stage
- Runs Trivy vulnerability scanner on built images
- Uploads results to GitHub Security tab
- Scans for OS and library vulnerabilities

### 4. Deployment Stages
- **Staging**: Deploys `develop` branch to staging environment
- **Production**: Deploys tagged releases to production

### 5. Distribution Update
- Updates `docker-compose.dist.yml` with latest image
- Commits changes back to repository

## 🏷️ Tagging Strategy

### Image Tags
- `latest` - Latest main branch build
- `develop` - Latest develop branch build  
- `v1.2.3` - Specific version releases
- `v1.2` - Major.minor version
- `v1` - Major version

### Git Tags
Use semantic versioning for releases:
```bash
git tag v1.0.0
git push origin v1.0.0
```

## 🐳 Docker Images

### Registry
Images are published to GitHub Container Registry:
- **Registry**: `ghcr.io`
- **Repository**: `ghcr.io/aloshy-ai/deep-job-seek`

### Platforms
Multi-platform support:
- `linux/amd64` (Intel/AMD)
- `linux/arm64` (Apple Silicon, ARM servers)

### Image Contents
- Python 3.10 runtime
- Pre-cached FastEmbed model
- Application source code
- All dependencies installed

## 🔧 Local Development

### Testing the Pipeline
```bash
# Test Quick Start script
make quickstart-test

# Test multi-platform build (requires buildx)
make release-test

# Run full test suite
make test
```

### Manual Image Building
```bash
# Build local image
docker build -t deep-job-seek:local .

# Build multi-platform (requires setup)
docker buildx build --platform linux/amd64,linux/arm64 -t deep-job-seek:multi .
```

## 🚀 Release Process

### Automatic Release (Recommended)
1. Create and push a git tag:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. Create a GitHub release:
   - Go to GitHub → Releases → Create Release
   - Select the tag you just pushed
   - Add release notes
   - Publish release

3. The `release.yml` workflow will automatically:
   - Update `docker-compose.dist.yml` with the release tag
   - Enable Quick Start in the README
   - Add Docker image info to release notes

### Manual Release
If needed, you can manually trigger deployments:

```bash
# Login to registry
make docker-login

# Build and push specific version
docker buildx build --platform linux/amd64,linux/arm64 \
  -t ghcr.io/aloshy-ai/deep-job-seek:v1.0.0 \
  --push .
```

## 🔒 Security

### Image Scanning
- Trivy scans for vulnerabilities
- Results uploaded to GitHub Security tab
- Scans both OS packages and dependencies

### Access Control
- GitHub Container Registry access via GITHUB_TOKEN
- Automatic cleanup of old images
- Only tagged releases are permanent

### Secrets Management
Required secrets:
- `GITHUB_TOKEN` - Automatically provided by GitHub
- No additional secrets needed for basic setup

## 🛠️ Environment Variables

### Build-time
- `EMBEDDING_MODEL` - FastEmbed model to cache (default: BAAI/bge-small-en-v1.5)

### Runtime
- `QDRANT_HOST` - Qdrant service host
- `QDRANT_PORT` - Qdrant service port  
- `OPENAI_API_BASE_URL` - AI API endpoint
- `API_PORT` - Application port
- `DEBUG` - Debug mode flag

## 📊 Monitoring

### GitHub Actions
- View workflow runs in Actions tab
- Check build logs and test results
- Monitor deployment status

### Docker Registry
- View images at `ghcr.io/aloshy-ai/deep-job-seek`
- Check image sizes and platforms
- Review vulnerability scan results

## 🐛 Troubleshooting

### Common Issues

**Build Failures**
- Check Dockerfile syntax
- Verify all dependencies in requirements.txt
- Ensure tests pass locally first

**Registry Push Failures**
- Verify GITHUB_TOKEN permissions
- Check registry authentication
- Ensure repository name is correct

**Quick Start Not Working**
- Verify docker-compose.dist.yml is valid
- Check if Docker images exist in registry
- Test run.sh script syntax locally

### Debug Commands
```bash
# Test docker-compose config
docker-compose -f docker-compose.dist.yml config

# Check image exists
docker manifest inspect ghcr.io/aloshy-ai/deep-job-seek:latest

# Test local build
docker build --no-cache .
```

## 📚 Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Buildx Documentation](https://docs.docker.com/buildx/)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)