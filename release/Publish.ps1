[CmdletBinding()]
param([string]$Owner='yilongzhao1122',[string]$Repo='aurora6x-studio')
$ErrorActionPreference='Stop'
$root=Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $root
& gh auth status
if($LASTEXITCODE -ne 0){throw 'Sign in with gh auth login first.'}
$login=(& gh api user --jq .login).Trim()
if($login -ne $Owner){throw 'Authenticated account does not match the requested owner.'}
[xml]$manifest=Get-Content -LiteralPath manifest.xml -Raw -Encoding UTF8
$version=$manifest.manifest.application.version
if(-not $version){throw 'Application version missing.'}
$status=git status --porcelain
if($status){throw 'Commit the intended source changes before packaging.'}
$remote=git remote get-url origin
if($remote -notmatch [regex]::Escape("$Owner/$Repo")){throw 'Origin does not match the requested repository.'}
& gh release view "v$version" --repo "$Owner/$Repo" 2>$null
if($LASTEXITCODE -eq 0){throw 'A release already exists; inspect it before publishing.'}
git push origin main
if($LASTEXITCODE -ne 0){throw 'Push failed; history was not overwritten.'}
python release/package_source.py
if($LASTEXITCODE -ne 0){throw 'Source packaging failed.'}
& gh release create "v$version" "dist/Aurora6X-Studio-v$version-Source-CN.zip" "dist/Aurora6X-Studio-v$version-Source-EN.zip" dist/SHA256SUMS.txt --repo "$Owner/$Repo" --target main --title "Aurora 6X Studio v$version" --notes-file RELEASE_NOTES.md --latest
if($LASTEXITCODE -ne 0){throw 'Release creation failed; inspect the repository before retrying.'}
& gh release view "v$version" --repo "$Owner/$Repo" --json url,assets
