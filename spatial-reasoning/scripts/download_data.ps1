# Downloads the public GEO datasets listed in Slack #data (posted by Myles, 15/10/2026).
#
# Safe to re-run at any time: finished files are skipped and interrupted downloads resume
# where they stopped (e.g. after the laptop slept or the Wi-Fi dropped).
#
# Run from the project folder:
#   powershell -ExecutionPolicy Bypass -File .\scripts\download_data.ps1
#
# 1. Downloads into the project's data/raw (fast, reliable, and what we analyse from).
# 2. Extracts each GEO *_RAW.tar archive.
# 3. Copies the extracted files into Google Drive, which then uploads them in the background.

$Local = Join-Path $PSScriptRoot "..\data\raw"
$Drive = "G:\Mi unidad\TECNUN 2026-27\Alumno_Interno\02_data\raw"
$Base  = "https://ftp.ncbi.nlm.nih.gov/geo/series"

# Smallest first, so there is something to explore while the big ones download.
$Datasets = [ordered]@{
    "GSE316760" = @("GSE316760_RAW.tar")                                 #  87 MB  primary melanoma, 2 Visium samples
    "GSE300445" = @("GSE300445_RAW.tar")                                 # 316 MB  melanoma pre anti-PD1, 4 Visium samples
    "GSE298774" = @("GSE298774_RAW.tar", "GSE298774_A2_features.tsv.gz") # 1.4 GB  nevus -> melanoma, 11 Visium slides
    "GSE221390" = @("GSE221390_RAW.tar")                                 # 1.6 GB  SCC/BCC/melanoma atlas + scRNA-seq
}

$failed = @()

foreach ($gse in $Datasets.Keys) {
    $url_dir  = "$Base/$($gse.Substring(0, 6))nnn/$gse/suppl"
    $download = Join-Path $Local "$gse\download"
    $files    = Join-Path $Local "$gse\files"
    New-Item -ItemType Directory -Force $download, $files | Out-Null

    Write-Host "`n===== $gse =====" -ForegroundColor Cyan

    foreach ($name in @("filelist.txt") + $Datasets[$gse]) {
        $url  = "$url_dir/$name"
        $dest = Join-Path $download $name

        $expected = [int64](Invoke-WebRequest -Uri $url -Method Head -UseBasicParsing).Headers["Content-Length"]
        if ((Test-Path $dest) -and ((Get-Item $dest).Length -eq $expected)) {
            Write-Host "already downloaded: $name"
        } else {
            Write-Host "downloading: $name ($([math]::Round($expected / 1MB)) MB)"
            curl.exe -L --retry 20 --retry-delay 10 --retry-all-errors -C - -o $dest $url
            if ((Get-Item $dest).Length -ne $expected) {
                Write-Host "INCOMPLETE: $name - run this script again to resume" -ForegroundColor Red
                $failed += $name
                continue
            }
        }

        if ($name -like "*.tar") {
            $marker = "$dest.extracted"
            if (-not (Test-Path $marker)) {
                Write-Host "extracting: $name"
                tar.exe -xf $dest -C $files
                if ($LASTEXITCODE -eq 0) { New-Item -ItemType File $marker | Out-Null } else { $failed += $name; continue }
            }
        } else {
            Copy-Item $dest $files -Force
        }
    }

    Write-Host "copying $gse to Google Drive..."
    robocopy $files (Join-Path $Drive $gse) /E /NP /NJH /NJS /NDL | Out-Null
    if ($LASTEXITCODE -ge 8) { $failed += "$gse (copy to Drive)" }
}

Write-Host ""
if ($failed.Count -eq 0) {
    Write-Host "ALL DONE. Local copy: $Local   Drive copy: $Drive" -ForegroundColor Green
} else {
    Write-Host "Finished with problems: $($failed -join ', '). Run the script again to retry." -ForegroundColor Yellow
}
