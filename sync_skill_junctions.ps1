<#
.SYNOPSIS
    skills-main/skills-main/skills 配下のスキルと ~/.claude/skills/, ~/.agent/skills/ の junction を同期する。

.DESCRIPTION
    - 実体スキャン: $SourceRoot 配下で SKILL.md を持つディレクトリを抽出（template 等は除外、claude.ai 配下の 1 階層ネストも探索）
    - 各 target ($env:USERPROFILE\.claude\skills\, $env:USERPROFILE\.agent\skills\) について:
        1. 期待集合に無い junction を削除（target が $SourceRoot 内を指すもののみ）
        2. 期待集合の junction が無ければ作成、あればスキップ
    - 第三者スキル junction（target が $SourceRoot 外 = ~/.agents/skills/ など）は保護して触らない
    - 出力: created / removed / kept / external-preserved / not-junction-skipped の各リスト

.PARAMETER DryRun
    実際の作成・削除を行わず、計画のみ表示する

.EXAMPLE
    pwsh sync_skill_junctions.ps1 -DryRun
    pwsh sync_skill_junctions.ps1
#>

[CmdletBinding()]
param(
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'

$SourceRoot = 'C:\work\utility\skills-main\skills-main\skills'
$Targets = @(
    (Join-Path $env:USERPROFILE '.claude\skills'),
    (Join-Path $env:USERPROFILE '.agent\skills')
)
$ExcludedNames = @('template', '.claude-plugin', 'node_modules', 'spec', '__pycache__', '.git')

if (-not (Test-Path -LiteralPath $SourceRoot)) {
    throw "SourceRoot not found: $SourceRoot"
}

# Normalize a directory path for case-insensitive comparison (strip trailing backslashes).
function Get-NormalizedPath {
    param([string]$Path)
    if ([string]::IsNullOrEmpty($Path)) { return '' }
    return $Path.TrimEnd('\')
}

# Return the first resolved target of a junction/symlink, or $null.
function Get-LinkTarget {
    param($Item)
    return ($Item.Target | Select-Object -First 1)
}

# True if $Path is equal to $Root or nested under it (case-insensitive).
function Test-PathUnder {
    param([string]$Path, [string]$Root)
    $normPath = Get-NormalizedPath $Path
    $normRoot = Get-NormalizedPath $Root
    if (-not $normPath -or -not $normRoot) { return $false }
    if ($normPath -ieq $normRoot) { return $true }
    return $normPath.StartsWith("$normRoot\", [StringComparison]::OrdinalIgnoreCase)
}

function Get-ExpectedSkills {
    param([string]$Root)
    $result = @{}

    $topDirs = Get-ChildItem -LiteralPath $Root -Directory |
        Where-Object { $_.Name -notin $ExcludedNames }

    foreach ($dir in $topDirs) {
        $hasSkill = Test-Path -LiteralPath (Join-Path $dir.FullName 'SKILL.md')
        if ($hasSkill) {
            # Top-level skill
            $result[$dir.Name] = $dir.FullName
        }

        # Also explore one-level nested (e.g. claude.ai/vercel-deploy-claimable).
        # Continue even when top-level itself is a skill, so a parent containing both
        # its own SKILL.md and nested skill subfolders won't drop the children.
        Get-ChildItem -LiteralPath $dir.FullName -Directory -ErrorAction SilentlyContinue |
            Where-Object {
                ($_.Name -notin $ExcludedNames) -and
                (Test-Path -LiteralPath (Join-Path $_.FullName 'SKILL.md'))
            } |
            ForEach-Object {
                if ($result.ContainsKey($_.Name)) {
                    Write-Warning "Skill name collision: nested '$($_.Name)' under '$($dir.Name)' ignored (existing entry '$($result[$_.Name])' kept). Rename one to avoid silent drop."
                } else {
                    $result[$_.Name] = $_.FullName
                }
            }
    }

    return $result
}

function Sync-Target {
    param(
        [string]$TargetDir,
        [hashtable]$Expected
    )

    $report = [PSCustomObject]@{
        Target             = $TargetDir
        Created            = @()
        Removed            = @()
        Kept               = @()
        ExternalPreserved  = @()
        NotJunctionSkipped = @()
        SkippedReason      = $null
    }

    # If the target dir ITSELF is a junction into the source tree, skip — it auto-syncs implicitly.
    if (Test-Path -LiteralPath $TargetDir) {
        $rootItem = Get-Item -LiteralPath $TargetDir -Force
        if ($rootItem.LinkType -eq 'Junction') {
            $rootTarget = Get-LinkTarget $rootItem
            if (Test-PathUnder -Path $rootTarget -Root $SourceRoot) {
                $report.SkippedReason = "Root junction -> $rootTarget (auto-syncs via parent link; per-skill management not applicable)"
                return $report
            }
        }
    } elseif ($DryRun) {
        Write-Host "[DryRun] Would create directory: $TargetDir"
    } else {
        New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null
    }

    # Inspect existing entries in target
    $existing = @{}
    if (Test-Path -LiteralPath $TargetDir) {
        Get-ChildItem -LiteralPath $TargetDir -Force -ErrorAction SilentlyContinue | ForEach-Object {
            $existing[$_.Name] = $_
        }
    }

    # Pass 1: remove junctions not in expected (only if target is inside $SourceRoot)
    foreach ($name in @($existing.Keys)) {
        $item = $existing[$name]

        if ($item.LinkType -ne 'Junction') {
            $report.NotJunctionSkipped += $name
            continue
        }

        $linkTarget = Get-LinkTarget $item
        $isInternal = Test-PathUnder -Path $linkTarget -Root $SourceRoot

        if (-not $isInternal) {
            $report.ExternalPreserved += "$name -> $linkTarget"
            continue
        }

        if (-not $Expected.ContainsKey($name)) {
            if ($DryRun) {
                Write-Host "[DryRun] Would remove junction: $($item.FullName) -> $linkTarget"
            } else {
                # Defensive re-check immediately before destructive op (TOCTOU + future-edit safety).
                # Without this, a refactor that drops the earlier LinkType guard could silently delete
                # a real directory (Directory::Delete on a non-junction removes the directory itself
                # when empty).
                if ($item.LinkType -ne 'Junction') {
                    Write-Warning "Skipping non-junction in delete pass: $($item.FullName) (LinkType=$($item.LinkType))"
                    continue
                }
                [System.IO.Directory]::Delete($item.FullName, $false)
            }
            # Update local tracking in both real and dry-run modes so Pass 2 sees the
            # post-removal state. Otherwise dry-run would mis-classify Would-create entries as Kept.
            $existing.Remove($name)
            $report.Removed += $name
        }
    }

    # Pass 2: create missing junctions (or retarget mismatched ones)
    foreach ($name in ($Expected.Keys | Sort-Object)) {
        $src = $Expected[$name]
        $linkPath = Join-Path $TargetDir $name

        if ($existing.ContainsKey($name)) {
            $item = $existing[$name]

            if ($item.LinkType -ne 'Junction') {
                $report.NotJunctionSkipped += "$name (exists as non-junction; manual review needed)"
                continue
            }

            $linkTarget = Get-LinkTarget $item
            $isCorrectTarget = (Get-NormalizedPath $linkTarget) -ieq (Get-NormalizedPath $src)

            if ($isCorrectTarget) {
                $report.Kept += $name
                continue
            }

            # Junction points elsewhere - recreate
            if ($DryRun) {
                Write-Host "[DryRun] Would recreate junction (target mismatch): $linkPath ($linkTarget -> $src)"
            } else {
                # Defensive: confirm it is still a junction immediately before destructive op.
                if ($item.LinkType -ne 'Junction') {
                    Write-Warning "Skipping retarget for $name (LinkType=$($item.LinkType); manual review needed)"
                    continue
                }
                try {
                    [System.IO.Directory]::Delete($linkPath, $false)
                    New-Item -ItemType Junction -Path $linkPath -Value $src -ErrorAction Stop | Out-Null
                } catch {
                    Write-Warning "Failed to retarget $linkPath -> $src : $($_.Exception.Message)"
                    continue
                }
            }
            $report.Removed += "$name (retarget)"
            $report.Created += $name
            continue
        }

        # Missing — create
        if ($DryRun) {
            Write-Host "[DryRun] Would create junction: $linkPath -> $src"
        } else {
            try {
                New-Item -ItemType Junction -Path $linkPath -Value $src -ErrorAction Stop | Out-Null
            } catch {
                Write-Warning "Failed to create junction $linkPath -> $src : $($_.Exception.Message)"
                continue
            }
        }
        $report.Created += $name
    }

    return $report
}

# Main
Write-Host ""
Write-Host "=== Skill Junction Sync ===" -ForegroundColor Cyan
if ($DryRun) { Write-Host "Mode: DRY-RUN (no changes will be made)" -ForegroundColor Yellow }
Write-Host "Source: $SourceRoot"
Write-Host ""

$expected = Get-ExpectedSkills -Root $SourceRoot
Write-Host "Expected skills (with SKILL.md): $($expected.Count)"
Write-Host ""

$results = @()
foreach ($t in $Targets) {
    Write-Host "Syncing: $t" -ForegroundColor Cyan
    $r = Sync-Target -TargetDir $t -Expected $expected
    $results += $r

    if ($r.SkippedReason) {
        Write-Host "  [Skipped] $($r.SkippedReason)" -ForegroundColor DarkGray
        Write-Host ""
        continue
    }

    Write-Host ("  Created: {0}, Removed: {1}, Kept: {2}, External: {3}, NotJunction: {4}" -f `
        $r.Created.Count, $r.Removed.Count, $r.Kept.Count, $r.ExternalPreserved.Count, $r.NotJunctionSkipped.Count)
    if ($r.Created.Count -gt 0)            { Write-Host "    + " ($r.Created -join ', ')            -ForegroundColor Green    }
    if ($r.Removed.Count -gt 0)            { Write-Host "    - " ($r.Removed -join ', ')            -ForegroundColor Red      }
    if ($r.ExternalPreserved.Count -gt 0)  { Write-Host "    ~ " ($r.ExternalPreserved -join '; ')  -ForegroundColor DarkGray }
    if ($r.NotJunctionSkipped.Count -gt 0) { Write-Host "    ! " ($r.NotJunctionSkipped -join ', ') -ForegroundColor Yellow   }
    Write-Host ""
}

Write-Host "=== Summary ===" -ForegroundColor Cyan
Write-Host "Expected: $($expected.Count) skills"
foreach ($r in $results) {
    if ($r.SkippedReason) {
        Write-Host ("  {0}: SKIPPED ({1})" -f $r.Target, $r.SkippedReason)
    } else {
        Write-Host ("  {0}: created={1}, removed={2}, kept={3}, external={4}" -f `
            $r.Target, $r.Created.Count, $r.Removed.Count, $r.Kept.Count, $r.ExternalPreserved.Count)
    }
}
if ($DryRun) {
    Write-Host ""
    Write-Host "Dry-run finished. Re-run without -DryRun to apply." -ForegroundColor Yellow
}
