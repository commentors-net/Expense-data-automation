# Smart Expense Importer - Google Cloud Deployment Script
# Deploys backend to Cloud Run with production settings

param(
    [Parameter(Mandatory=$false)]
    [string]$ProjectId = "",
    
    [Parameter(Mandatory=$false)]
    [string]$Region = "us-central1",
    
    [Parameter(Mandatory=$false)]
    [string]$ServiceName = "expense-importer-api"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Smart Expense Importer - GCP Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get project ID if not provided
if ([string]::IsNullOrEmpty($ProjectId)) {
    $ProjectId = gcloud config get-value project 2>$null
    if ([string]::IsNullOrEmpty($ProjectId)) {
        Write-Host "❌ No GCP project configured. Please run:" -ForegroundColor Red
        Write-Host "   gcloud config set project YOUR_PROJECT_ID" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "📋 Configuration:" -ForegroundColor Green
Write-Host "   Project ID: $ProjectId"
Write-Host "   Region: $Region"
Write-Host "   Service: $ServiceName"
Write-Host ""

# Check if .env exists
if (-not (Test-Path "backend\.env")) {
    Write-Host "⚠️  Warning: backend\.env not found" -ForegroundColor Yellow
    Write-Host "   Create it from backend\.env.example" -ForegroundColor Yellow
    Write-Host ""
}

# Get Gemini API key from .env or prompt
$geminiKey = ""
if (Test-Path "backend\.env") {
    $envContent = Get-Content "backend\.env" -Raw
    if ($envContent -match 'GEMINI_API_KEY=([^\r\n]+)') {
        $geminiKey = $matches[1]
    }
}

if ([string]::IsNullOrEmpty($geminiKey)) {
    Write-Host "🔑 Gemini API Key not found in .env" -ForegroundColor Yellow
    $geminiKey = Read-Host "   Enter your Gemini API key"
}

Write-Host ""
Write-Host "🚀 Starting deployment..." -ForegroundColor Cyan
Write-Host ""

# Enable required APIs
Write-Host "1️⃣  Enabling required Google Cloud APIs..." -ForegroundColor Yellow
gcloud services enable run.googleapis.com --project=$ProjectId
gcloud services enable firestore.googleapis.com --project=$ProjectId
gcloud services enable storage.googleapis.com --project=$ProjectId
gcloud services enable artifactregistry.googleapis.com --project=$ProjectId

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to enable APIs" -ForegroundColor Red
    exit 1
}

Write-Host "✅ APIs enabled successfully" -ForegroundColor Green
Write-Host ""

# Create Artifact Registry repository
Write-Host "2️⃣  Creating Artifact Registry repository..." -ForegroundColor Yellow
$repoName = "expense-repo"
gcloud artifacts repositories describe $repoName `
    --location=$Region `
    --project=$ProjectId 2>$null

if ($LASTEXITCODE -ne 0) {
    Write-Host "   Creating new repository..." -ForegroundColor Gray
    gcloud artifacts repositories create $repoName `
        --repository-format=docker `
        --location=$Region `
        --project=$ProjectId
}

Write-Host "✅ Repository ready" -ForegroundColor Green
Write-Host ""

# Build and push Docker image
Write-Host "3️⃣  Building and pushing Docker image..." -ForegroundColor Yellow
$imageName = "$Region-docker.pkg.dev/$ProjectId/$repoName/backend:latest"

Push-Location backend
gcloud builds submit --tag $imageName --project=$ProjectId
Pop-Location

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to build image" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Image built and pushed" -ForegroundColor Green
Write-Host ""

# Deploy to Cloud Run
Write-Host "4️⃣  Deploying to Cloud Run..." -ForegroundColor Yellow
gcloud run deploy $ServiceName `
    --image $imageName `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --set-env-vars "ENVIRONMENT=production,GEMINI_API_KEY=$geminiKey,FIRESTORE_COLLECTION=expenses" `
    --project=$ProjectId

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Deployment failed" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Backend deployed successfully" -ForegroundColor Green
Write-Host ""

# Get service URL
$serviceUrl = gcloud run services describe $ServiceName `
    --region $Region `
    --project=$ProjectId `
    --format="value(status.url)" 2>$null

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " ✅ Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Backend API URL:" -ForegroundColor Cyan
Write-Host "   $serviceUrl" -ForegroundColor White
Write-Host ""
Write-Host "📝 Next Steps:" -ForegroundColor Yellow
Write-Host "   1. Update frontend .env with: VITE_API_BASE_URL=$serviceUrl/api"
Write-Host "   2. Build frontend: cd frontend && npm run build"
Write-Host "   3. Deploy frontend to Cloud Storage or Firebase Hosting"
Write-Host ""
Write-Host "📊 View logs:" -ForegroundColor Yellow
Write-Host "   gcloud run services logs tail $ServiceName --region=$Region"
Write-Host ""
Write-Host "🔗 API Documentation:" -ForegroundColor Yellow
Write-Host "   $serviceUrl/docs"
Write-Host ""
