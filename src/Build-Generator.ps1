param([Parameter(Mandatory)][string]$PayloadZip,[Parameter(Mandatory)][string]$Branding,[Parameter(Mandatory)][string]$Output)
$ErrorActionPreference='Stop'
$outputFile=[IO.Path]::GetFullPath($Output)
$buildFolder=Join-Path ([IO.Path]::GetDirectoryName($outputFile)) 'build-generator'
New-Item -ItemType Directory -Path $buildFolder -Force|Out-Null
$oldTemp=$env:TEMP;$oldTmp=$env:TMP
try{
 $env:TEMP=$buildFolder;$env:TMP=$buildFolder
 $hash=(Get-FileHash -LiteralPath $PayloadZip -Algorithm SHA256).Hash.ToLowerInvariant()
 $source=[IO.File]::ReadAllText((Join-Path $PSScriptRoot 'Generator.cs')).Replace('__PAYLOAD_SHA256__',$hash)
 $generated=Join-Path $buildFolder 'Generator.cs';[IO.File]::WriteAllText($generated,$source,[Text.UTF8Encoding]::new($false))
 $compiler=Join-Path $env:WINDIR 'Microsoft.NET/Framework64/v4.0.30319/csc.exe'
 & $compiler /nologo /target:winexe /platform:x64 /optimize+ /codepage:65001 /reference:System.Windows.Forms.dll /reference:System.Drawing.dll /reference:System.Web.Extensions.dll /reference:System.Core.dll /reference:System.IO.Compression.dll /reference:System.IO.Compression.FileSystem.dll "/resource:$PayloadZip,payload.zip" "/resource:$PSScriptRoot/locales.json,locales.json" "/resource:$Branding/RatchetJak.ico,brand.icon" "/resource:$Branding/RatchetJak-logo.png,brand.logo" "/win32icon:$Branding/RatchetJak.ico" "/out:$outputFile" $generated (Join-Path $PSScriptRoot 'IsoSafety.cs') (Join-Path $PSScriptRoot 'Lang.cs')
 if($LASTEXITCODE -ne 0){throw 'Falló la compilación del generador'}
 Get-FileHash -LiteralPath $outputFile -Algorithm SHA256|Select-Object Path,Hash
}finally{$env:TEMP=$oldTemp;$env:TMP=$oldTmp}
