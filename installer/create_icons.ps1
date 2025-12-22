# ====================================
# Créer des icônes par défaut
# ====================================

Write-Host "Création des icônes par défaut..." -ForegroundColor Cyan

$ResourcesDir = Join-Path $PSScriptRoot "package\resources"

# Utiliser Add-Type pour créer des images avec .NET
Add-Type -AssemblyName System.Drawing

# Créer app.ico (32x32)
Write-Host "[INFO] Création de app.ico..." -ForegroundColor Yellow
$bitmap = New-Object System.Drawing.Bitmap(32, 32)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)

# Fond bleu
$brush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(41, 128, 185))
$graphics.FillRectangle($brush, 0, 0, 32, 32)

# Bordure
$pen = New-Object System.Drawing.Pen([System.Drawing.Color]::White, 2)
$graphics.DrawRectangle($pen, 2, 2, 28, 28)

# Texte AY
$font = New-Object System.Drawing.Font("Arial", 10, [System.Drawing.FontStyle]::Bold)
$textBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)
$graphics.DrawString("AY", $font, $textBrush, 6, 8)

# Sauvegarder comme ICO
$iconPath = "$ResourcesDir\app.ico"
$ms = New-Object System.IO.MemoryStream
$bitmap.Save($ms, [System.Drawing.Imaging.ImageFormat]::Png)
$ms.Seek(0, [System.IO.SeekOrigin]::Begin) | Out-Null

# Créer un fichier ICO basique (envelopper le PNG)
$iconBytes = [byte[]](0x00, 0x00, 0x01, 0x00, 0x01, 0x00, 0x20, 0x20, 0x00, 0x00, 0x01, 0x00, 0x20, 0x00)
$iconBytes += [System.BitConverter]::GetBytes([int]$ms.Length)
$iconBytes += [System.BitConverter]::GetBytes([int]22)
[System.IO.File]::WriteAllBytes($iconPath, $iconBytes + $ms.ToArray())

$graphics.Dispose()
$bitmap.Dispose()
$brush.Dispose()
$pen.Dispose()
$font.Dispose()
$textBrush.Dispose()

# Copier pour toutes les icônes
Copy-Item $iconPath "$ResourcesDir\start.ico" -Force
Copy-Item $iconPath "$ResourcesDir\stop.ico" -Force
Copy-Item $iconPath "$ResourcesDir\logs.ico" -Force
Copy-Item $iconPath "$ResourcesDir\config.ico" -Force
Copy-Item $iconPath "$ResourcesDir\uninstall.ico" -Force

Write-Host "[OK] Icônes .ico créées" -ForegroundColor Green

# Créer header.bmp (150x57)
Write-Host "[INFO] Création de header.bmp..." -ForegroundColor Yellow
$headerBitmap = New-Object System.Drawing.Bitmap(150, 57)
$headerGraphics = [System.Drawing.Graphics]::FromImage($headerBitmap)

# Dégradé bleu
$brush1 = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(52, 152, 219))
$brush2 = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(41, 128, 185))
$headerGraphics.FillRectangle($brush1, 0, 0, 75, 57)
$headerGraphics.FillRectangle($brush2, 75, 0, 75, 57)

# Texte
$headerFont = New-Object System.Drawing.Font("Arial", 16, [System.Drawing.FontStyle]::Bold)
$headerBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)
$headerGraphics.DrawString("AY HR", $headerFont, $headerBrush, 20, 15)

$headerBitmap.Save("$ResourcesDir\header.bmp", [System.Drawing.Imaging.ImageFormat]::Bmp)
$headerGraphics.Dispose()
$headerBitmap.Dispose()
$brush1.Dispose()
$brush2.Dispose()
$headerFont.Dispose()
$headerBrush.Dispose()

Write-Host "[OK] header.bmp créé" -ForegroundColor Green

# Créer wizard.bmp (164x314)
Write-Host "[INFO] Création de wizard.bmp..." -ForegroundColor Yellow
$wizardBitmap = New-Object System.Drawing.Bitmap(164, 314)
$wizardGraphics = [System.Drawing.Graphics]::FromImage($wizardBitmap)

# Dégradé vertical
$wizardBrush1 = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(52, 152, 219))
$wizardBrush2 = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(41, 128, 185))
$wizardBrush3 = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::FromArgb(30, 100, 150))

$wizardGraphics.FillRectangle($wizardBrush1, 0, 0, 164, 105)
$wizardGraphics.FillRectangle($wizardBrush2, 0, 105, 164, 105)
$wizardGraphics.FillRectangle($wizardBrush3, 0, 210, 164, 104)

# Texte
$wizardFont = New-Object System.Drawing.Font("Arial", 20, [System.Drawing.FontStyle]::Bold)
$wizardBrush = New-Object System.Drawing.SolidBrush([System.Drawing.Color]::White)
$wizardGraphics.DrawString("AY HR", $wizardFont, $wizardBrush, 30, 130)

$wizardBitmap.Save("$ResourcesDir\wizard.bmp", [System.Drawing.Imaging.ImageFormat]::Bmp)
$wizardGraphics.Dispose()
$wizardBitmap.Dispose()
$wizardBrush1.Dispose()
$wizardBrush2.Dispose()
$wizardBrush3.Dispose()
$wizardFont.Dispose()
$wizardBrush.Dispose()

Write-Host "[OK] wizard.bmp créé" -ForegroundColor Green

Write-Host "`n[SUCCESS] Toutes les icônes ont été créées !" -ForegroundColor Green
Write-Host "[INFO] Emplacement: $ResourcesDir" -ForegroundColor Cyan
Write-Host "`nNOTE: Ces icônes sont basiques. Pour un aspect professionnel," -ForegroundColor Yellow
Write-Host "      remplacez-les par de vraies icônes créées avec un outil graphique." -ForegroundColor Yellow
