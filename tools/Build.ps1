[CmdletBinding()]
param(
    [string]$KeyPath = $env:GARMIN_DEVELOPER_KEY,
    [string]$SdkPath = '',
    [switch]$Run,
    [switch]$CheckOnly
)
$ErrorActionPreference = 'Stop'
$project = Split-Path -Parent $PSScriptRoot
if (-not $KeyPath) { $KeyPath = Join-Path $project 'keys\developer_key' }
$ciqRoot = Join-Path $env:APPDATA 'Garmin\ConnectIQ'
try {
    if (-not $SdkPath) {
        $current = Join-Path $ciqRoot 'current-sdk.cfg'
        if (Test-Path -LiteralPath $current -PathType Leaf) {
            $SdkPath = (Get-Content -LiteralPath $current -Raw).Trim().Trim('"')
        }
        if (-not $SdkPath -or -not (Test-Path -LiteralPath (Join-Path $SdkPath 'bin\monkeyc.bat'))) {
            $sdkRoot = Join-Path $ciqRoot 'Sdks'
            $candidates = @(Get-ChildItem -LiteralPath $sdkRoot -Directory -ErrorAction SilentlyContinue |
                Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'bin\monkeyc.bat') } |
                Sort-Object LastWriteTime -Descending)
            if ($candidates.Count -eq 0) { throw 'SDK not found. Run Monkey C: Open SDK Manager or pass -SdkPath.' }
            $SdkPath = $candidates[0].FullName
        }
    }
    if (-not (Test-Path -LiteralPath (Join-Path $SdkPath 'bin\monkeybrains.jar') -PathType Leaf)) {
        throw 'SdkPath must be the SDK folder containing bin, not bin itself.'
    }
    $deviceFile = Join-Path $ciqRoot 'Devices\fenix6xpro\compiler.json'
    if (-not (Test-Path -LiteralPath $deviceFile -PathType Leaf)) {
        throw 'fenix6xpro device missing. Download it in SDK Manager > Devices.'
    }
    if (-not (Test-Path -LiteralPath $KeyPath -PathType Leaf)) {
        throw ('Developer key is not a file: ' + $KeyPath + '. Pass -KeyPath with the actual key FILE path. Do not select a folder.')
    }
    $javaCommand = Get-Command java.exe -ErrorAction SilentlyContinue
    $java = if ($javaCommand) { $javaCommand.Source } else { $null }
    if (-not $java -and $env:JAVA_HOME) {
        $candidate = Join-Path $env:JAVA_HOME 'bin\java.exe'
        if (Test-Path -LiteralPath $candidate) { $java = $candidate }
    }
    if (-not $java) { throw 'Java not found in PATH/JAVA_HOME. Use VS Code Ctrl+F5, or set JAVA_HOME to your existing JDK.' }
    Write-Host 'Aurora 6X Studio 3.3.2 - typefaces + total calories'
    Write-Host ('Project: ' + $project)
    Write-Host ('SDK:     ' + $SdkPath)
    Write-Host ('Device:  fenix6xpro (280 x 280)')
    Write-Host ('Key:     ' + $KeyPath)
    Write-Host ('Java:    ' + $java)
    if ($CheckOnly) { Write-Host 'Environment checks passed. No files changed.'; exit 0 }

    # Validate every setting before writing resources. No arbitrary code evaluation.
    $config = Get-Content -LiteralPath (Join-Path $project 'config.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    $schema = Get-Content -LiteralPath (Join-Path $project 'tools\settings-schema.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    # Compatible with the previous 19-setting config; C1 was fixed to heart rate.
    if ($null -eq $config.PSObject.Properties['C1']) {
        $config | Add-Member -NotePropertyName 'C1' -NotePropertyValue 0
    }
    foreach ($newKey in @('TimeTypeface','DataTypeface')) {
        if ($null -eq $config.PSObject.Properties[$newKey]) {
            $config | Add-Member -NotePropertyName $newKey -NotePropertyValue $schema.defaults.$newKey
        }
    }
    foreach ($entry in $schema.defaults.PSObject.Properties) {
        $name = $entry.Name
        $value = $config.$name
        if ($name -eq 'CustomText') {
            if ($value -isnot [string] -or $value.Length -gt 18 -or $value -match '[^\x20-\x7e]') {
                throw 'CustomText must contain at most 18 printable ASCII characters.'
            }
            continue
        }
        if ($null -eq $value -or $value -is [bool] -or $value -is [string] -or [double]$value -ne [math]::Truncate([double]$value)) {
            throw ('Invalid or missing v3 config setting: ' + $name + '. Use the NEW settings helper; use the v3 config.json.')
        }
        $choices = $schema.options.$name
        if ($null -ne $choices) { $lo = 0; $hi = $choices.Count - 1 }
        else { $lo = $schema.ranges.$name[0]; $hi = $schema.ranges.$name[1] }
        if ($value -lt $lo -or $value -gt $hi) { throw ('Out-of-range config setting: ' + $name) }
    }
    $propertyFile = Join-Path $project 'resources\settings\properties.xml'
    [xml]$properties = Get-Content -LiteralPath $propertyFile -Raw -Encoding UTF8
    foreach ($node in $properties.properties.property) {
        $value = $config.($node.id)
        if ($value -is [bool]) { $value = $value.ToString().ToLowerInvariant() }
        $node.InnerText = [string]$value
    }
    $properties.Save($propertyFile)
    $bin = Join-Path $project 'bin'
    New-Item -Path $bin -ItemType Directory -Force | Out-Null
    $output = Join-Path $bin 'Aurora6X.prg'
    $arguments = @('-Dfile.encoding=UTF-8','-jar',(Join-Path $SdkPath 'bin\monkeybrains.jar'),'-f',(Join-Path $project 'monkey.jungle'),'-d','fenix6xpro','-y',$KeyPath,'-o',$output,'-w')
    if (-not $Run) { $arguments += '-r' }
    & $java @arguments
    if ($LASTEXITCODE -ne 0) { throw ('Compiler failed. Exit code: ' + $LASTEXITCODE + '. Read the first ERROR above.') }
    Write-Host ('SUCCESS: ' + $output) -ForegroundColor Green
    if ($Run) {
        # SDK monkeydo.bat expects Java in PATH. Set only this process environment.
        $env:PATH = (Split-Path -Parent $java) + ';' + $env:PATH
        Start-Process -FilePath (Join-Path $SdkPath 'bin\connectiq.bat') -WorkingDirectory (Join-Path $SdkPath 'bin') -WindowStyle Hidden
        Start-Sleep -Seconds 4
        & (Join-Path $SdkPath 'bin\monkeydo.bat') $output 'fenix6xpro'
        if ($LASTEXITCODE -ne 0) { throw 'Simulator launch failed. Open the simulator, then try 01_Run_Simulator.cmd again.' }
    }
} catch {
    Write-Host ('ERROR: ' + $_.Exception.Message) -ForegroundColor Red
    exit 1
}
