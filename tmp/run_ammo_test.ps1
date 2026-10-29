param([string]$Test = 'validate_ammo', [switch]$Render, [switch]$Import, [switch]$Fixed)
$ErrorActionPreference = 'Stop'
$env:APPDATA = 'C:/Dev/BlenderMCP/.local_appdata'
$projectPath = 'C:/Users/stevi/OneDrive/Documents/space-game-prototype'
$logPath = "C:/Dev/BlenderMCP/tmp/$Test-ammo.log"
$arguments = @('--path', ('"' + $projectPath + '"'), '--log-file', $logPath)
if (-not $Render) { $arguments += '--headless' }
if ($Fixed) { $arguments += @('--fixed-fps', '60') }
if ($Import) { $arguments += @('--editor', '--import', '--quit') }
else { $arguments += @('--script', "res://tests/$Test.gd") }
$run = Start-Process -FilePath 'C:/Users/stevi/OneDrive/Desktop/Godot_v4.7.2-stable_win64.exe' -ArgumentList $arguments -WindowStyle Hidden -PassThru
Write-Output "$Test process=$($run.Id)"
$run.WaitForExit()
Write-Output "$Test exit=$($run.ExitCode)"
Get-Content -LiteralPath $logPath -Tail 55
exit $run.ExitCode
