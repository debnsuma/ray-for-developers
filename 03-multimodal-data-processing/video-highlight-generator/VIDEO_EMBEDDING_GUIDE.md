# Video Embedding Guide for GitHub README

## Problem

Your demo video (`demo_video_highlighter.mov`) is **160MB**, but GitHub has limitations:
- **Git repository limit**: 100MB per file (hard limit)
- **GitHub video display limit**: 10MB recommended
- **README rendering**: Only supports images, animated GIFs, and external video links

---

## ✅ Recommended Solutions (Best to Worst)

### Solution 1: YouTube Upload (Recommended) ⭐⭐⭐⭐⭐

**Best for**: Professional presentation, unlimited file size, good performance

#### Steps:
1. Upload video to YouTube (can be unlisted for privacy)
2. Embed in README with preview image

#### Implementation:

```markdown
## 🎬 Live Demo

[![Video Highlight Generator Demo](https://img.youtube.com/vi/YOUR_VIDEO_ID/maxresdefault.jpg)](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)

*Click to watch the full demo (2 minutes)*
```

**Pros**:
- ✅ Unlimited file size
- ✅ Professional video player
- ✅ Good performance
- ✅ Automatic thumbnails
- ✅ Works everywhere (mobile, desktop)
- ✅ Can be unlisted (not public)

**Cons**:
- ❌ Requires YouTube account
- ❌ External dependency

---

### Solution 2: Git LFS + GitHub Releases ⭐⭐⭐⭐

**Best for**: Keeping video in repository, no external services

#### Steps:

1. **Install Git LFS**:
```bash
# Install Git LFS
brew install git-lfs  # macOS
# or: apt-get install git-lfs  # Linux

# Initialize in repo
git lfs install
```

2. **Track video files**:
```bash
cd /Users/suman/Work/code/ray-for-developers

# Track .mov files
git lfs track "recordings/*.mov"
git add .gitattributes

# Add your video
git add recordings/demo_video_highlighter.mov
git commit -m "Add demo video via Git LFS"
```

3. **Create GitHub Release** and attach video

4. **Link in README**:
```markdown
## 🎬 Live Demo

[Download Demo Video (160MB)](https://github.com/debnsuma/ray-for-developers/releases/download/v1.0/demo_video_highlighter.mov)

Or watch online:
- [Direct Link](https://github.com/debnsuma/ray-for-developers/raw/main/recordings/demo_video_highlighter.mov)
```

**Pros**:
- ✅ Keeps video in your repository
- ✅ No external services
- ✅ Version controlled

**Cons**:
- ❌ Requires Git LFS setup
- ❌ No inline playback (download required)
- ❌ Bandwidth costs for large files

---

### Solution 3: Convert to Animated GIF ⭐⭐⭐

**Best for**: Quick preview without external services

#### Steps:

1. **Convert video to GIF** (compress to < 10MB):
```bash
# Using FFmpeg
ffmpeg -i recordings/demo_video_highlighter.mov \
  -vf "fps=10,scale=800:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" \
  -loop 0 recordings/demo_preview.gif

# Optimize further if needed
gifsicle -O3 --lossy=80 recordings/demo_preview.gif -o recordings/demo_optimized.gif
```

2. **Embed in README**:
```markdown
## 🎬 Live Demo

![Video Highlight Generator Demo](./recordings/demo_optimized.gif)

*Animated preview - [Download full video (160MB)](./recordings/demo_video_highlighter.mov)*
```

**Pros**:
- ✅ Plays inline on GitHub
- ✅ No external services
- ✅ Immediate visual

**Cons**:
- ❌ Quality loss
- ❌ Large GIF file (still 10-20MB)
- ❌ No audio
- ❌ Limited frame rate

---

### Solution 4: Vimeo/Google Drive/Dropbox ⭐⭐⭐

**Best for**: Alternative to YouTube

#### Implementation:

**Vimeo**:
```markdown
[![Demo](https://vumbnail.com/YOUR_VIMEO_ID.jpg)](https://vimeo.com/YOUR_VIMEO_ID)
```

**Google Drive** (make video public):
```markdown
[Watch Demo Video](https://drive.google.com/file/d/YOUR_FILE_ID/view)
```

**Pros**:
- ✅ Good video quality
- ✅ No file size limits

**Cons**:
- ❌ External dependency
- ❌ Requires account

---

### Solution 5: GitHub Video (New Feature) ⭐⭐⭐⭐

**Note**: GitHub now supports video uploads directly in README!

#### Steps:

1. **Compress video to < 10MB**:
```bash
# Compress to smaller size
ffmpeg -i recordings/demo_video_highlighter.mov \
  -vcodec h264 \
  -acodec aac \
  -vf "scale=1280:-1" \
  -crf 28 \
  recordings/demo_compressed.mp4
```

2. **Upload via GitHub UI**:
   - Edit README on GitHub web interface
   - Drag & drop video file
   - GitHub will automatically upload and embed

3. **Result**:
```markdown
## 🎬 Live Demo

https://user-images.githubusercontent.com/XXXXX/XXXXX-XXXXX.mp4
```

**Pros**:
- ✅ Native GitHub integration
- ✅ Inline playback
- ✅ No external services

**Cons**:
- ❌ 10MB file size limit
- ❌ Requires compression (quality loss)

---

## 🎯 Recommended Approach for Your Case

### Option A: YouTube + Compressed Preview (Best)

1. **Upload full video to YouTube** (unlisted)
2. **Create compressed MP4** for GitHub (< 10MB)
3. **Provide both options** in README

```markdown
## 🎬 Live Demo

### Watch Online
[![Full Demo on YouTube](https://img.youtube.com/vi/YOUR_ID/maxresdefault.jpg)](https://www.youtube.com/watch?v=YOUR_ID)
*Full quality demo (2 minutes) on YouTube*

### Quick Preview
https://user-images.githubusercontent.com/XXXXX/demo_compressed.mp4
*Compressed preview embedded in README*

### Download
- [Full Quality Video (160MB)](https://github.com/debnsuma/ray-for-developers/releases/download/v1.0/demo_video_highlighter.mov)
```

---

## 🛠️ Quick Commands for Your Video

### 1. Create Compressed Version (< 10MB)

```bash
cd /Users/suman/Work/code/ray-for-developers/recordings

# High compression (720p, ~8MB)
ffmpeg -i demo_video_highlighter.mov \
  -vf "scale=1280:720" \
  -c:v libx264 -crf 28 \
  -c:a aac -b:a 128k \
  -movflags +faststart \
  demo_compressed_720p.mp4

# Check file size
ls -lh demo_compressed_720p.mp4
```

### 2. Create Animated GIF Preview

```bash
# Create optimized GIF (first 30 seconds, 800px wide)
ffmpeg -i demo_video_highlighter.mov \
  -t 30 \
  -vf "fps=10,scale=800:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" \
  demo_preview.gif

# Check size
ls -lh demo_preview.gif
```

### 3. Create Thumbnail for YouTube

```bash
# Extract a good frame for thumbnail
ffmpeg -i demo_video_highlighter.mov \
  -ss 00:00:05 \
  -frames:v 1 \
  -q:v 2 \
  demo_thumbnail.jpg
```

---

## 📝 README Examples

### Example 1: YouTube Primary (Recommended)

```markdown
## 🎬 Live Demo

Watch the Video Highlight Generator in action:

[![Video Demo](https://img.youtube.com/vi/YOUR_VIDEO_ID/maxresdefault.jpg)](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)

**Demo highlights:**
- ✨ Real-time Ray worker visualization
- 📊 4-phase pipeline execution
- 🎬 Side-by-side video comparison
- ⚡ Complete processing in 28 seconds

*Click image to watch on YouTube (2 minutes)*
```

### Example 2: GitHub Video Embed

```markdown
## 🎬 Live Demo

See the complete workflow in action:

https://user-images.githubusercontent.com/XXXXX/XXXXX.mp4

**What you're seeing:**
1. Video selection (Big Buck Bunny - 10 minutes)
2. Ray cluster initialization and actor distribution
3. Real-time processing with live worker visualization
4. Highlight detection and 30-second reel generation
5. Side-by-side comparison playback

[Download full quality video (160MB)](https://github.com/debnsuma/ray-for-developers/releases/download/v1.0/demo_video_highlighter.mov)
```

### Example 3: Animated GIF Preview

```markdown
## 🎬 Live Demo

![Demo Preview](./recordings/demo_preview.gif)

*Animated preview showing pipeline execution and Ray cluster visualization*

**[Download full video (160MB)](./recordings/demo_video_highlighter.mov)** for complete demo with audio
```

---

## ⚡ Quick Decision Matrix

| Priority | Best Solution | Effort | Quality | Cost |
|----------|---------------|--------|---------|------|
| **Professional** | YouTube | Low | High | Free |
| **Self-hosted** | Git LFS | Medium | High | Bandwidth |
| **Quick & Easy** | GitHub Video | Low | Medium | Free |
| **Preview Only** | Animated GIF | Medium | Low | Free |

---

## 🎯 My Recommendation for You

**Step 1**: Upload to YouTube (unlisted)
```bash
# Upload demo_video_highlighter.mov to YouTube
# Set as unlisted if you don't want it public
# Get video ID from URL
```

**Step 2**: Create compressed version
```bash
cd /Users/suman/Work/code/ray-for-developers/recordings

ffmpeg -i demo_video_highlighter.mov \
  -vf "scale=1280:720" \
  -c:v libx264 -crf 28 \
  -c:a aac -b:a 128k \
  -movflags +faststart \
  demo_compressed.mp4

# Should be ~8-10MB
```

**Step 3**: Update README with both
```markdown
## 🎬 Live Demo

### Full Demo on YouTube
[![Watch Demo](https://img.youtube.com/vi/YOUR_ID/maxresdefault.jpg)](https://www.youtube.com/watch?v=YOUR_ID)

*Full quality demo with audio (2 minutes)*

### Quick Preview
*Compressed preview for quick viewing:*

https://github.com/debnsuma/ray-for-developers/assets/XXXXX/demo_compressed.mp4

---

**Features shown in demo:**
- ✨ Real-time Ray cluster visualization
- 📊 Live worker task monitoring
- 🎬 4-phase pipeline execution
- ⚡ Processing 10-minute video in 28 seconds
- 🎥 Side-by-side video comparison
```

---

## 🚀 Next Steps

1. **Choose your approach** (I recommend YouTube + compressed MP4)
2. **Compress video** using commands above
3. **Upload to hosting** (YouTube, GitHub, or Git LFS)
4. **Update README** with embedded video
5. **Test on GitHub** to ensure it works

Would you like me to create the compressed version and update the README with the embedding code?
