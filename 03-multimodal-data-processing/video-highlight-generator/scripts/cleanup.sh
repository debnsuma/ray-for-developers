#!/bin/bash
# Video Highlight Generator - Cleanup Script
# Removes temporary files and large data files

set -e

echo "🧹 Video Highlight Generator - Cleanup Script"
echo "=============================================="
echo ""

# Function to ask for confirmation
confirm() {
    read -p "$1 (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        return 1
    fi
    return 0
}

# ============================================================================
# 1. Clean Python cache files
# ============================================================================
echo "📦 Cleaning Python cache files..."
find . -type d -name "__pycache__" -not -path "./.venv/*" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -not -path "./.venv/*" -delete 2>/dev/null || true
find . -name "*.pyo" -not -path "./.venv/*" -delete 2>/dev/null || true
find . -name "*.py[cod]" -not -path "./.venv/*" -delete 2>/dev/null || true
echo "   ✅ Python cache cleaned"

# ============================================================================
# 2. Clean OS-specific files
# ============================================================================
echo "🗂️  Cleaning OS-specific files..."
find . -name ".DS_Store" -not -path "./.venv/*" -delete 2>/dev/null || true
find . -name "._*" -not -path "./.venv/*" -delete 2>/dev/null || true
find . -name "Thumbs.db" -not -path "./.venv/*" -delete 2>/dev/null || true
find . -name "*.swp" -not -path "./.venv/*" -delete 2>/dev/null || true
find . -name "*.swo" -not -path "./.venv/*" -delete 2>/dev/null || true
echo "   ✅ OS files cleaned"

# ============================================================================
# 3. Clean Ray temporary files
# ============================================================================
echo "⚡ Cleaning Ray temporary files..."
rm -rf /tmp/ray 2>/dev/null || true
rm -rf ray_results/ 2>/dev/null || true
rm -rf .ray/ 2>/dev/null || true
find . -name "ray_*" -type d -not -path "./.venv/*" -exec rm -rf {} + 2>/dev/null || true
echo "   ✅ Ray files cleaned"

# ============================================================================
# 4. Clean log files
# ============================================================================
echo "📝 Cleaning log files..."
find . -name "*.log" -not -path "./.venv/*" -delete 2>/dev/null || true
rm -rf logs/ 2>/dev/null || true
echo "   ✅ Log files cleaned"

# ============================================================================
# 5. Show data directory sizes
# ============================================================================
echo ""
echo "📊 Current data directory sizes:"
echo "================================"
if [ -d "data" ]; then
    du -sh data/* 2>/dev/null | sort -h || true
else
    echo "   No data directory found"
fi

# ============================================================================
# 6. Optional: Clean processed/pipeline data (keeps raw videos)
# ============================================================================
echo ""
if confirm "🗑️  Clean processed pipeline data? (keeps raw videos)"; then
    echo "   Cleaning pipeline outputs..."
    rm -rf data/pipeline/* 2>/dev/null || true
    rm -rf data/processed/* 2>/dev/null || true
    rm -rf data/output/* 2>/dev/null || true
    rm -rf data/features/demo/* 2>/dev/null || true
    rm -rf data/highlights/demo/* 2>/dev/null || true

    # Recreate .gitkeep files
    touch data/pipeline/.gitkeep 2>/dev/null || true
    touch data/processed/.gitkeep 2>/dev/null || true
    touch data/output/.gitkeep 2>/dev/null || true
    touch data/features/demo/.gitkeep 2>/dev/null || true
    touch data/highlights/demo/.gitkeep 2>/dev/null || true

    echo "   ✅ Pipeline data cleaned"
else
    echo "   ⏭️  Skipped pipeline data cleanup"
fi

# ============================================================================
# 7. Optional: Clean YouTube test downloads
# ============================================================================
echo ""
if confirm "🗑️  Clean YouTube test downloads? (709MB)"; then
    echo "   Cleaning YouTube test data..."
    rm -rf data/raw/youtube_test/* 2>/dev/null || true
    touch data/raw/youtube_test/.gitkeep 2>/dev/null || true
    echo "   ✅ YouTube test data cleaned"
else
    echo "   ⏭️  Skipped YouTube test data cleanup"
fi

# ============================================================================
# 8. Optional: Clean ALL downloaded videos (CAUTION!)
# ============================================================================
echo ""
echo "⚠️  WARNING: This will delete ALL downloaded videos including demos!"
if confirm "🗑️  Clean ALL raw video files? (1.5GB - CANNOT BE UNDONE)"; then
    echo "   Cleaning all raw videos..."
    rm -rf data/raw/demo/*.mp4 2>/dev/null || true
    rm -rf data/raw/demo/*.avi 2>/dev/null || true
    rm -rf data/raw/youtube/* 2>/dev/null || true
    rm -rf data/raw/youtube_test/* 2>/dev/null || true

    # Recreate .gitkeep files
    touch data/raw/demo/.gitkeep 2>/dev/null || true
    touch data/raw/youtube/.gitkeep 2>/dev/null || true
    touch data/raw/youtube_test/.gitkeep 2>/dev/null || true

    echo "   ✅ All raw videos cleaned"
    echo "   ⚠️  Run 'python scripts/download_sample_videos.py' to re-download demos"
else
    echo "   ⏭️  Skipped raw video cleanup"
fi

# ============================================================================
# 9. Final summary
# ============================================================================
echo ""
echo "=============================================="
echo "✅ Cleanup complete!"
echo "=============================================="
echo ""
echo "📊 Final data directory sizes:"
if [ -d "data" ]; then
    du -sh data/* 2>/dev/null | sort -h || true
else
    echo "   No data directory found"
fi
echo ""
echo "💡 Tip: Run 'python scripts/download_sample_videos.py' to download demo videos"
echo "💡 Tip: Check .gitignore to see what files are excluded from git"
