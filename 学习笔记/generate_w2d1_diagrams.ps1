Add-Type -AssemblyName System.Drawing

$ErrorActionPreference = "Stop"

$ScriptDir = if ($PSScriptRoot) {
    $PSScriptRoot
} elseif ($MyInvocation.MyCommand.Path) {
    Split-Path -Parent $MyInvocation.MyCommand.Path
} else {
    Join-Path (Get-Location) "学习笔记"
}
$OutDir = Join-Path $ScriptDir "diagrams"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

function New-Color($hex) {
    return [System.Drawing.ColorTranslator]::FromHtml($hex)
}

function New-FontSafe($name, $size, $style = [System.Drawing.FontStyle]::Regular) {
    try {
        return [System.Drawing.Font]::new($name, $size, $style, [System.Drawing.GraphicsUnit]::Pixel)
    } catch {
        return [System.Drawing.Font]::new("Microsoft YaHei UI", $size, $style, [System.Drawing.GraphicsUnit]::Pixel)
    }
}

function New-Canvas {
    $bmp = [System.Drawing.Bitmap]::new(1200, 720)
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $g.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
    $g.Clear((New-Color "#fffdf7"))
    return @{ Bitmap = $bmp; Graphics = $g }
}

function New-Rect($x, $y, $w, $h) {
    return [System.Drawing.RectangleF]::new([single]$x, [single]$y, [single]$w, [single]$h)
}

function Draw-RoundRect($g, $rect, $fill, $stroke, $width = 4) {
    $radius = 18
    $path = [System.Drawing.Drawing2D.GraphicsPath]::new()
    $d = $radius * 2
    $path.AddArc($rect.X, $rect.Y, $d, $d, 180, 90)
    $path.AddArc($rect.Right - $d, $rect.Y, $d, $d, 270, 90)
    $path.AddArc($rect.Right - $d, $rect.Bottom - $d, $d, $d, 0, 90)
    $path.AddArc($rect.X, $rect.Bottom - $d, $d, $d, 90, 90)
    $path.CloseFigure()
    $brush = [System.Drawing.SolidBrush]::new($fill)
    $pen = [System.Drawing.Pen]::new($stroke, $width)
    $g.FillPath($brush, $path)
    $g.DrawPath($pen, $path)
    $brush.Dispose()
    $pen.Dispose()
    $path.Dispose()
}

function Draw-Text($g, $text, $rect, $font, $color, $align = "Center") {
    $brush = [System.Drawing.SolidBrush]::new($color)
    $fmt = [System.Drawing.StringFormat]::new()
    $fmt.Alignment = if ($align -eq "Left") { [System.Drawing.StringAlignment]::Near } else { [System.Drawing.StringAlignment]::Center }
    $fmt.LineAlignment = [System.Drawing.StringAlignment]::Center
    $fmt.FormatFlags = [System.Drawing.StringFormatFlags]::LineLimit
    $g.DrawString($text, $font, $brush, $rect, $fmt)
    $brush.Dispose()
    $fmt.Dispose()
}

function Draw-Box($g, $x, $y, $w, $h, $title, $body, $fillHex) {
    $ink = New-Color "#1f2937"
    $rect = New-Rect $x $y $w $h
    Draw-RoundRect $g $rect (New-Color $fillHex) $ink 4
    Draw-Text $g $title (New-Rect ($x + 16) ($y + 14) ($w - 32) 34) (New-FontSafe "KaiTi" 28 ([System.Drawing.FontStyle]::Bold)) $ink
    if ($body) {
        Draw-Text $g $body (New-Rect ($x + 22) ($y + 56) ($w - 44) ($h - 72)) (New-FontSafe "Microsoft YaHei UI" 22) $ink
    }
}

function Draw-Arrow($g, $x1, $y1, $x2, $y2, $label = "") {
    $ink = New-Color "#1f2937"
    $pen = [System.Drawing.Pen]::new($ink, 4)
    $cap = [System.Drawing.Drawing2D.AdjustableArrowCap]::new(8, 10)
    $pen.CustomEndCap = $cap
    $g.DrawLine($pen, [single]$x1, [single]$y1, [single]$x2, [single]$y2)
    if ($label) {
        Draw-Text $g $label (New-Rect (($x1 + $x2) / 2 - 70) (($y1 + $y2) / 2 - 28) 140 34) (New-FontSafe "Microsoft YaHei UI" 19) $ink
    }
    $cap.Dispose()
    $pen.Dispose()
}

function Draw-Title($g, $title, $subtitle) {
    $ink = New-Color "#1f2937"
    Draw-Text $g $title (New-Rect 40 28 1120 48) (New-FontSafe "KaiTi" 38 ([System.Drawing.FontStyle]::Bold)) $ink
    Draw-Text $g $subtitle (New-Rect 60 78 1080 32) (New-FontSafe "Microsoft YaHei UI" 21) (New-Color "#4b5563")
}

function Save-Canvas($canvas, $name) {
    $path = Join-Path $OutDir $name
    $canvas.Bitmap.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
    $canvas.Graphics.Dispose()
    $canvas.Bitmap.Dispose()
}

function Draw-StructuredOutputMap {
    $c = New-Canvas
    $g = $c.Graphics
    Draw-Title $g "结构化输出学习地图" "从「可读文本」走向「可被程序稳定处理的数据」"

    Draw-Box $g 80 180 230 180 "普通自然语言" "人能看懂`n程序难接住`n格式会漂移" "#dbeafe"
    Draw-Box $g 370 180 230 180 "要求 JSON" "简单好用`n但仍可能多解释`n字段值不稳定" "#fef3c7"
    Draw-Box $g 660 180 230 180 "工具 Schema" "定义字段`n定义类型`n定义必填项" "#dcfce7"
    Draw-Box $g 950 180 190 180 "程序消费" "入库`n调用 API`n前端渲染" "#e5e7eb"

    Draw-Arrow $g 310 270 370 270
    Draw-Arrow $g 600 270 660 270
    Draw-Arrow $g 890 270 950 270

    Draw-Box $g 235 470 730 110 "一句话记忆" "结构化输出不是让模型更会说，而是让模型输出更像接口。" "#fde2e2"
    Save-Canvas $c "w2d1-structured-output-map.png"
}

function Draw-ThreeLayerValidation {
    $c = New-Canvas
    $g = $c.Graphics
    Draw-Title $g "三层校验：从提示到程序兜底" "每一层都在减少下游系统踩坑的概率"

    Draw-Box $g 95 180 290 260 "第 1 层" "Prompt 控格式`n明确只返回 JSON`n给字段清单`n给示例和模板`n适合快速试验" "#dbeafe"
    Draw-Box $g 455 180 290 260 "第 2 层" "Schema 定结构`n字段名更稳定`n类型更明确`nrequired 更清楚`n适合接口输入" "#dcfce7"
    Draw-Box $g 815 180 290 260 "第 3 层" "程序做校验`nJSON 解析`n类型检查`n范围检查`n异常兜底" "#fef3c7"

    Draw-Arrow $g 385 310 455 310
    Draw-Arrow $g 745 310 815 310

    Draw-Box $g 205 505 790 125 "关键边界" "模型负责生成结构，程序负责验证结构；格式稳定不等于内容一定正确。" "#fde2e2"
    Save-Canvas $c "w2d1-three-layer-validation.png"
}

function Draw-FunctionCallingFlow {
    $c = New-Canvas
    $g = $c.Graphics
    Draw-Title $g "Function Calling 流程" "模型不真正执行函数，它生成的是「应该调用什么 + 参数是什么」"

    Draw-Box $g 70 145 210 150 "1 用户输入" "自然语言需求" "#dbeafe"
    Draw-Box $g 355 145 220 150 "2 工具定义" "name / desc`nparameters" "#e5e7eb"
    Draw-Box $g 650 145 220 150 "3 模型决策" "是否调用工具`n生成参数" "#fef3c7"
    Draw-Box $g 930 145 210 150 "4 程序执行" "真正调用函数`n访问外部系统" "#dcfce7"

    Draw-Arrow $g 280 220 355 220
    Draw-Arrow $g 575 220 650 220
    Draw-Arrow $g 870 220 930 220

    Draw-Box $g 235 420 260 140 "工具结果" "结构化返回给模型" "#dcfce7"
    Draw-Box $g 705 420 260 140 "最终回答" "模型组织成自然语言" "#dbeafe"
    Draw-Arrow $g 930 295 495 420 "结果回填"
    Draw-Arrow $g 495 490 705 490 "总结给用户"

    Save-Canvas $c "w2d1-function-calling-flow.png"
}

function Draw-PromptVsSchema {
    $c = New-Canvas
    $g = $c.Graphics
    Draw-Title $g "Prompt-only JSON vs Tool Schema" "同样是 JSON，稳定程度不一样"

    Draw-Box $g 105 160 430 355 "Prompt-only JSON" "优点：上手快`n`n风险：`n可能包代码块`n可能多一句解释`n字段值格式漂移`nclub 可能一会儿字符串、一会儿数组" "#fef3c7"
    Draw-Box $g 665 160 430 355 "Tool Schema" "优点：更像接口契约`n`n约束：`n字段名固定`n类型更清楚`n必填项明确`n更适合数据库/API/前端" "#dcfce7"

    Draw-Arrow $g 535 338 665 338

    Draw-Box $g 240 550 720 110 "学习判断" "普通 JSON: club = 数组；Schema: club = 字符串。" "#dbeafe"
    Save-Canvas $c "w2d1-prompt-vs-schema.png"
}

Draw-StructuredOutputMap
Draw-ThreeLayerValidation
Draw-FunctionCallingFlow
Draw-PromptVsSchema

Write-Host "Generated diagrams in $OutDir"
