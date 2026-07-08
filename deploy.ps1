# Deploy to LibyanSpider cPanel via FTP
# Usage: .\deploy.ps1

$ftpServer = "ftp.yourdomain.com"   # <-- fill in your FTP host
$ftpUser   = "youruser"             # <-- fill in your cPanel/FTP username
$ftpPass   = "yourpassword"         # <-- fill in your FTP password
$remoteDir = "/public_html"         # <-- fill in your remote folder

# Build credential
$secPass = ConvertTo-SecureString $ftpPass -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential($ftpUser, $secPass)

# Get changed files since last push
$files = git diff --name-only HEAD~1
if (-not $files) { $files = git ls-files }

foreach ($f in $files) {
    $remote = "$remoteDir/$f".Replace("\", "/")
    $uri    = "ftp://$ftpServer$remote"
    Write-Host "Uploading: $f -> $remote"
    try {
        Invoke-WebRequest -Uri $uri -Method Put -InFile $f -Credential $cred -ErrorAction Stop | Out-Null
        Write-Host "  OK" -ForegroundColor Green
    } catch {
        Write-Host "  FAILED: $_" -ForegroundColor Red
    }
}
Write-Host "`nDone." -ForegroundColor Yellow
