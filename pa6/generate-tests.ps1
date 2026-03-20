# Run all .ac tests: python3 acdc.py tests/testX.ac tests/testX.dc
# @@ -0,0 +1,12 @@
$ErrorActionPreference = "Stop"

$testsPath = Join-Path $PSScriptRoot "tests"

Get-ChildItem -Path $testsPath -Filter "*.ac" | ForEach-Object {
    $acfile = $_.FullName
    $base = $_.BaseName
    $dcfile = Join-Path $testsPath ($base + ".dc")

    Write-Host "Running: $base"
    python acdc.py $acfile $dcfile
}