$deckPath = "C:\Projects\FSM-NIDS\presentation\TraceGuard AI — Editorial Theory of Computation Deck.pptx"
$outDir = "C:\Projects\FSM-NIDS\frontend\public\slides"

if (!(Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
}

try {
    $ppt = New-Object -ComObject PowerPoint.Application
    $pres = $ppt.Presentations.Open($deckPath, [Microsoft.Office.Core.MsoTriState]::msoTrue, [Microsoft.Office.Core.MsoTriState]::msoFalse, [Microsoft.Office.Core.MsoTriState]::msoFalse)
    
    Write-Host "Presentation opened: $($pres.Slides.Count) slides found."
    
    for ($i = 1; $i -le $pres.Slides.Count; $i++) {
        $slide = $pres.Slides.Item($i)
        $slideFile = Join-Path $outDir ("slide_{0:D2}.png" -f $i)
        $slide.Export($slideFile, "PNG", 1920, 1080)
        Write-Host "Exported slide $i -> $slideFile"
    }
    
    $pres.Close()
    $ppt.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($ppt) | Out-Null
    Write-Host "SUCCESS: All 22 slides exported to $outDir"
} catch {
    Write-Error "Failed to export editorial slides: $_"
}
