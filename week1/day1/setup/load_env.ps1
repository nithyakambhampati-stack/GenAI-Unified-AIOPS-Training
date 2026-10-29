<#
  load_env.ps1
  ------------
  Copies the values in .env into the CURRENT PowerShell session, so that Claude Code CLI
  (which does not read .env itself) can see ANTHROPIC_API_KEY.

  IMPORTANT: "dot-source" this file (note the leading dot and space), otherwise the
  variables disappear when the script ends:

      . .\setup\load_env.ps1

  The values live only in this terminal window and vanish when you close it.
#>
$envFile = Join-Path (Split-Path -Parent $PSScriptRoot) ".env"
if (-not (Test-Path $envFile)) { Write-Host "No .env found at $envFile - copy .env.example first." -ForegroundColor Red; return }

Get-Content $envFile | ForEach-Object {
    $line = $_.Trim()
    # Skip blank lines and comments.
    if ($line -eq "" -or $line.StartsWith("#")) { return }
    $name, $value = $line -split "=", 2
    if ($value) {
        # Remove optional surrounding quotes, then set the variable for this session only.
        Set-Item -Path "Env:$($name.Trim())" -Value $value.Trim().Trim('"').Trim("'")
    }
}
Write-Host "Loaded .env into this PowerShell session." -ForegroundColor Green
