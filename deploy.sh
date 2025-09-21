#!/bin/bash

# Secure Deployment Script for CloudKitchens Kitchen Optimizer
# This script implements security best practices for deployment

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="kitchen-optimizer"
ENVIRONMENT="${ENVIRONMENT:-production}"
LOG_FILE="/var/log/kitchen-optimizer-deploy.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if running as root (security concern)
    if [[ $EUID -eq 0 ]]; then
        error "Do not run this script as root for security reasons"
    fi
    
    # Check required commands
    local required_commands=("docker" "docker-compose" "git" "openssl")
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            error "$cmd is required but not installed"
        fi
    done
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        error "Docker daemon is not running or accessible"
    fi
    
    success "Prerequisites check passed"
}

# Security setup
setup_security() {
    log "Setting up security configurations..."
    
    # Create secrets directory
    mkdir -p secrets
    chmod 700 secrets
    
    # Generate secure random passwords if they don't exist
    if [[ ! -f secrets/grafana_password.txt ]]; then
        openssl rand -base64 32 > secrets/grafana_password.txt
        chmod 600 secrets/grafana_password.txt
        log "Generated Grafana password"
    fi
    
    # Set secure file permissions
    find . -name "*.sh" -exec chmod 755 {} \;
    find . -name "*.yml" -exec chmod 644 {} \;
    find . -name "*.yaml" -exec chmod 644 {} \;
    
    # Create secure data directories
    sudo mkdir -p /opt/kitchen-optimizer/{data,logs,backups}
    sudo chown -R "$(whoami):$(whoami)" /opt/kitchen-optimizer/
    chmod 750 /opt/kitchen-optimizer/{data,logs,backups}
    
    success "Security setup completed"
}

# Environment validation
validate_environment() {
    log "Validating environment configuration..."
    
    # Check if .env file exists
    if [[ ! -f .env ]]; then
        warning ".env file not found, using defaults from .env.example"
        cp .env.example .env
    fi
    
    # Validate critical environment variables
    source .env
    
    if [[ -z "${DATA_DIR:-}" ]]; then
        error "DATA_DIR environment variable is required"
    fi
    
    success "Environment validation passed"
}

# Run security scans
run_security_scans() {
    log "Running security scans..."
    
    # Install security tools if not present
    if ! command -v trivy &> /dev/null; then
        log "Installing Trivy security scanner..."
        curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
    fi
    
    # Build the image for scanning
    docker build -t "$PROJECT_NAME:scan" .
    
    # Run Trivy scan
    log "Scanning Docker image for vulnerabilities..."
    trivy image --exit-code 1 --severity HIGH,CRITICAL "$PROJECT_NAME:scan" || {
        warning "High/Critical vulnerabilities found. Review the scan results."
        read -p "Continue deployment? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            error "Deployment aborted due to security vulnerabilities"
        fi
    }
    
    success "Security scans completed"
}

# Deploy application
deploy_application() {
    log "Deploying application..."
    
    # Pull latest images
    docker-compose pull
    
    # Build and start services
    if [[ "$ENVIRONMENT" == "production" ]]; then
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
    else
        docker-compose up -d --build
    fi
    
    # Wait for services to be healthy
    log "Waiting for services to be healthy..."
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if docker-compose ps | grep -q "Up (healthy)"; then
            break
        fi
        
        if [[ $attempt -eq $max_attempts ]]; then
            error "Services failed to become healthy within timeout"
        fi
        
        log "Waiting for services... (attempt $attempt/$max_attempts)"
        sleep 10
        ((attempt++))
    done
    
    success "Application deployed successfully"
}

# Run tests
run_tests() {
    log "Running post-deployment tests..."
    
    # Run application tests inside container
    docker-compose exec -T kitchen-optimizer python3 run_tests.py || {
        error "Tests failed after deployment"
    }
    
    # Test application functionality
    docker-compose exec -T kitchen-optimizer python3 demo.py || {
        error "Demo script failed after deployment"
    }
    
    success "Post-deployment tests passed"
}

# Setup monitoring
setup_monitoring() {
    if [[ "$ENVIRONMENT" == "production" ]]; then
        log "Setting up monitoring..."
        
        # Create monitoring configuration
        mkdir -p monitoring/grafana/provisioning/{dashboards,datasources}
        
        # Wait for Grafana to be ready
        local max_attempts=30
        local attempt=1
        
        while [[ $attempt -le $max_attempts ]]; do
            if curl -s http://localhost:3000/api/health &> /dev/null; then
                break
            fi
            
            if [[ $attempt -eq $max_attempts ]]; then
                warning "Grafana health check timeout"
                break
            fi
            
            sleep 5
            ((attempt++))
        done
        
        success "Monitoring setup completed"
    fi
}

# Backup function
create_backup() {
    log "Creating backup..."
    
    local backup_dir="/opt/kitchen-optimizer/backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Backup data
    if [[ -d /opt/kitchen-optimizer/data ]]; then
        cp -r /opt/kitchen-optimizer/data "$backup_dir/"
    fi
    
    # Backup configuration
    cp -r . "$backup_dir/config"
    
    # Compress backup
    tar -czf "$backup_dir.tar.gz" -C "$(dirname "$backup_dir")" "$(basename "$backup_dir")"
    rm -rf "$backup_dir"
    
    success "Backup created: $backup_dir.tar.gz"
}

# Cleanup function
cleanup() {
    log "Cleaning up..."
    
    # Remove old images
    docker image prune -f
    
    # Remove old backups (keep last 5)
    find /opt/kitchen-optimizer/backups -name "*.tar.gz" -type f | sort -r | tail -n +6 | xargs -r rm
    
    success "Cleanup completed"
}

# Main deployment function
main() {
    log "Starting secure deployment of $PROJECT_NAME"
    log "Environment: $ENVIRONMENT"
    
    # Create log file if it doesn't exist
    sudo touch "$LOG_FILE"
    sudo chown "$(whoami):$(whoami)" "$LOG_FILE"
    
    # Run deployment steps
    check_prerequisites
    validate_environment
    setup_security
    create_backup
    run_security_scans
    deploy_application
    run_tests
    setup_monitoring
    cleanup
    
    success "Deployment completed successfully!"
    log "Application is running at: http://localhost:8000"
    
    if [[ "$ENVIRONMENT" == "production" ]]; then
        log "Monitoring dashboard: http://localhost:3000"
        log "Prometheus metrics: http://localhost:9090"
    fi
    
    log "Deployment logs: $LOG_FILE"
}

# Handle script interruption
trap 'error "Deployment interrupted"' INT TERM

# Run main function
main "$@"