# ==============================================================================
# OS Simulator Launcher (PowerShell Entrypoint)
# ==============================================================================

$PSScriptRoot = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
$env:PYTHONPATH = "$PSScriptRoot;$env:PYTHONPATH"

python "$PSScriptRoot\main.py" $args
