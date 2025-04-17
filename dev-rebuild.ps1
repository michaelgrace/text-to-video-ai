# Stop and remove containers
docker-compose down

# Remove output directories
Remove-Item -Path "output/*" -Recurse -Force
Remove-Item -Path "temp/*" -Recurse -Force

# Force rebuild with no cache
$env:CACHEBUST = Get-Date -UFormat %s
docker-compose build --no-cache

# Start services
docker-compose up
