---

name: slides-in-html
description: Create stunning, animation-rich HTML presentations from scratch or by converting PowerPoint/PDF files. Automatically adapts to the user's language (e.g., English -> English, Chinese -> Chinese) for both communication and slide content.
---

# Slides-in-html Skill

Create zero-dependency, animation-rich HTML presentations that run entirely in the browser. This skill helps non-designers discover their preferred aesthetic through visual exploration ("show, don't tell"), then generates production-quality slide decks.

## Core Philosophy

1.  **Zero Dependencies** — Single HTML files with inline CSS/JS. No npm, no build tools.
2.  **Language Consistency** — **CRITICAL**: The agent must detect the user's language immediately. All agent-user communication AND all content generated within the presentation (slides, UI text, navigation hints) must be in that language.
3.  **Show, Don't Tell** — People don't know what they want until they see it. Generate visual previews, not abstract choices.
4.  **Distinctive Design** — Avoid generic "AI slop" aesthetics. Every presentation should feel custom-crafted.
5.  **Production Quality** — Code should be well-commented, accessible, and performant.


## Phase 0: Detect Mode & Language

First, determine what the user wants and **identify their language**.

**Language Detection Rule:**
- Analyze the user's input.
- If input is English -> Set mode to English.í
- If input is Chinese (Simplified/Traditional) -> Set mode to Chinese.
- If input is other languages -> Set mode accordingly.

**Mode A: New Presentation**
- User wants to create slides from scratch.
- Proceed to Phase 1 (Content Discovery).

**Mode B: File Conversion (PPT or PDF)**
- User has a PowerPoint file (.ppt, .pptx) or PDF to convert.
- Proceed to Phase 4 (File Extraction).

**Mode C: Existing Presentation Enhancement**
- User has an HTML presentation and wants to improve it.
- Read the existing file, understand the structure, then enhance.


## Phase 1: Content Discovery (New Presentations)

Before designing, understand the content. **All questions must be asked in the user's detected language.**

### Step 1.1: Presentation Context

**Question 1: Purpose**
- *Header:* [Translate: "Purpose" / "演示目的"]
- *Question:* [Translate: "What is this presentation for?" / "这个演示文稿的用途是什么？"]
- *Options:*
  - "Pitch deck" — Selling an idea/product (商业路演)
  - "Teaching/Tutorial" — Educational content (教学/教程)
  - "Conference talk" — Speaking at an event (会议演讲)
  - "Internal presentation" — Team updates (内部汇报)

**Question 2: Slide Count**
- *Header:* [Translate: "Length" / "篇幅"]
- *Question:* [Translate: "Approximately how many slides?" / "大约有多少页幻灯片？"]
- *Options:*
  - "Short (5-10)" — Quick pitch (简短)
  - "Medium (10-20)" — Standard (标准)
  - "Long (20+)" — Deep dive (详细)

**Question 3: Content**
- *Header:* [Translate: "Content" / "内容准备"]
- *Question:* [Translate: "Do you have the content ready, or do you need help structuring it?" / "您准备好内容了吗，还是需要我协助整理？"]
- *Options:*
  - "I have all content ready" (内容已齐全)
  - "I have rough notes" (只有粗略笔记)
  - "I have a topic only" (只有一个主题)

If user has content, ask them to share it in their preferred language.


## Phase 2: Style Discovery (Visual Exploration)

**CRITICAL: This is the "show, don't tell" phase.**

Most people can't articulate design preferences in words. Instead of asking "do you want minimalist or bold?", we generate mini-previews and let them react.

### Step 2.1: Mood Selection

**Question 1: Feeling**
- *Header:* [Translate: "Vibe" / "氛围感"]
- *Question:* [Translate: "What feeling should the audience have when viewing your slides?" / "观众观看幻灯片时应该有什么感觉？"]
- *Options:* (Translate contextually)
  - "Impressed/Confident" — Professional, trustworthy (专业/自信)
  - "Excited/Energized" — Innovative, bold (兴奋/充满活力)
  - "Calm/Focused" — Clear, thoughtful (冷静/专注)
  - "Inspired/Moved" — Emotional, storytelling (感动/启发)
- multiSelect: true

### Step 2.2: Generate Style Previews

Based on their mood selection, generate **3 distinct style previews**. Each preview should be a single title slide showing:
- Typography (appropriate for the language, e.g., Noto Sans SC for Chinese)
- Color palette
- Animation style
- Overall aesthetic

**Preview Styles to Consider:**
| Mood | Style Options |
|------|---------------|
| Impressed/Confident | "Corporate Elegant", "Dark Executive", "Clean Minimal" |
| Excited/Energized | "Neon Cyber", "Bold Gradients", "Kinetic Motion" |
| Calm/Focused | "Paper & Ink", "Soft Muted", "Swiss Minimal" |
| Inspired/Moved | "Cinematic Dark", "Warm Editorial", "Atmospheric" |

**IMPORTANT: Typography & Language Handling**
- **For Chinese/Non-Latin:** Do not use generic system fonts that look broken.
- **Font Recommendations:**
  - Chinese: 'Noto Sans SC', 'PingFang SC', 'Microsoft YaHei'
  - Japanese: 'Noto Sans JP', 'Hiragino Kaku Gothic Pro'
  - General: Use Fontshare for Latin, Google Fonts for CJK.
- **Preview Text:** The title slide in the preview MUST use dummy text in the user's language (e.g., "演示文稿标题" for Chinese, not "Presentation Title").

### Step 2.3: Present Previews

Create the previews in: `.claude-design/slide-previews/`

Present to user (in their language):
```
I've created 3 style previews for you to compare:
(我为您创建了 3 个风格预览供您比较：)

**Style A: [Name]** — [Description]
**Style B: [Name]** — [Description]
**Style C: [Name]** — [Description]

[Instructions to open files]
...

[Translate: "Take a look and tell me:" / "请查看后告诉我："]
1. Which style resonates most? (哪个风格最打动您？)
2. What do you like about it? (您喜欢它的哪一点？)
3. Anything you'd change? (有什么需要调整的吗？)
```

Then use AskUserQuestion:
- *Header:* [Translate: "Style" / "风格选择"]
- *Question:* [Translate: "Which style preview do you prefer?" / "您更偏好哪种风格预览？"]
- *Options:* Style A, Style B, Style C, Mix elements.


## Phase 3: Generate Presentation

Now generate the full presentation based on:
- Content from Phase 1
- Style from Phase 2
- **Language from Phase 0**

### File Structure

For single presentations:
```
presentation.html    # Self-contained presentation
assets/              # Images, if any
```

### HTML Architecture

Follow this structure, ensuring proper language attributes:

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>演示文稿标题</title>

    <!-- Fonts (DYNAMIC: Change based on language) -->
    <!-- Chinese Example -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;700&family=Noto+Serif+SC:wght@400;700&display=swap" rel="stylesheet">
    <!-- English Example -->
    <!-- <link rel="stylesheet" href="https://api.fontshare.com/v2/css?f[]=clash-display@600&f[]=satoshi@400,500"> -->

    <style>
        /* ===========================================
           CSS CUSTOM PROPERTIES (THEME)
           =========================================== */
        :root {
            /* Colors */
            --bg-primary: #0a0f1c;
            --bg-secondary: #111827;
            --text-primary: #ffffff;
            --text-secondary: #9ca3af;
            --accent: #00ffcc;
            --accent-glow: rgba(0, 255, 204, 0.3);

            /* Typography */
            --font-display: 'Noto Sans SC', sans-serif; /* Adjust font here */
            --font-body: 'Noto Sans SC', sans-serif;    /* Adjust font here */

            /* Spacing */
            --slide-padding: clamp(2rem, 5vw, 4rem);

            /* Animation */
            --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
            --duration-normal: 0.6s;
        }

        /* ===========================================
           BASE STYLES
           =========================================== */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        html {
            scroll-behavior: smooth;
            scroll-snap-type: y mandatory;
        }

        body {
            font-family: var(--font-body);
            background: var(--bg-primary);
            color: var(--text-primary);
            overflow-x: hidden;
            -webkit-font-smoothing: antialiased;
            text-rendering: optimizeLegibility;
        }

        /* ===========================================
           SLIDE CONTAINER
           Each section is one slide
           =========================================== */
        .slide {
            min-height: 100vh;
            padding: var(--slide-padding);
            scroll-snap-align: start;
            display: flex;
            flex-direction: column;
            justify-content: center;
            position: relative;
            overflow: hidden;
        }

        /* ===========================================
           ANIMATIONS
           Trigger via .visible class (added by JS on scroll)
           =========================================== */
        .reveal {
            opacity: 0;
            transform: translateY(30px);
            transition: opacity var(--duration-normal) var(--ease-out-expo),
                        transform var(--duration-normal) var(--ease-out-expo);
        }

        .slide.visible .reveal {
            opacity: 1;
            transform: translateY(0);
        }

        /* Stagger children */
        .reveal:nth-child(1) { transition-delay: 0.1s; }
        .reveal:nth-child(2) { transition-delay: 0.2s; }
        .reveal:nth-child(3) { transition-delay: 0.3s; }
        .reveal:nth-child(4) { transition-delay: 0.4s; }
        .reveal:nth-child(5) { transition-delay: 0.5s; }
        .reveal:nth-child(6) { transition-delay: 0.6s; }
        .reveal:nth-child(7) { transition-delay: 0.7s; }
        .reveal:nth-child(8) { transition-delay: 0.8s; }

        /* Typography Helpers */
        h1, h2, h3 {
            font-family: var(--font-display);
            line-height: 1.2;
            margin-bottom: 1rem;
        }

        h1 { font-size: clamp(2.5rem, 6vw, 5rem); }
        h2 { font-size: clamp(2rem, 4vw, 3.5rem); }
        p, li {
            font-size: clamp(1rem, 2vw, 1.25rem);
            line-height: 1.6; /* Higher for CJK */
            color: var(--text-secondary);
            margin-bottom: 1rem;
            max-width: 60ch;
        }

        /* Progress Bar */
        .progress-bar {
            position: fixed;
            top: 0;
            left: 0;
            height: 4px;
            background: var(--accent);
            width: 0%;
            z-index: 100;
            transition: width 0.1s linear;
        }

        /* Nav Dots */
        .nav-dots {
            position: fixed;
            right: 20px;
            top: 50%;
            transform: translateY(-50%);
            display: flex;
            flex-direction: column;
            gap: 10px;
            z-index: 100;
        }

        .nav-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: rgba(255,255,255,0.2);
            cursor: pointer;
            transition: all 0.3s;
        }

        .nav-dot.active {
            background: var(--accent);
            transform: scale(1.5);
        }

        /* Keyboard Hint */
        .keyboard-hint {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 0.8rem;
            color: rgba(255,255,255,0.3);
            z-index: 100;
            pointer-events: none;
        }

        /* Responsive */
        @media (max-width: 768px) {
            .nav-dots { display: none; }
            .keyboard-hint { display: none; }
            h1 { font-size: 2.5rem; }
        }
    </style>
</head>
<body>
    <!-- Progress bar -->
    <div class="progress-bar"></div>

    <!-- Navigation dots -->
    <nav class="nav-dots"></nav>

    <!-- Hint -->
    <div class="keyboard-hint">按空格键或点击翻页 / Press Space or Click to navigate</div>

    <!-- Slides -->
    <section class="slide title-slide">
        <h1 class="reveal">演示文稿标题</h1>
        <p class="reveal">副标题或演讲者信息</p>
    </section>

    <section class="slide">
        <h2 class="reveal">第一章：核心概念</h2>
        <p class="reveal">这里是正文内容，用于阐述您的核心观点。文字会自动换行以适应屏幕宽度。</p>
        <p class="reveal">第二段内容，带有交错的动画效果。</p>
    </section>

    <!-- More slides... -->

    <script>
        /* ===========================================
           SLIDE PRESENTATION CONTROLLER
           Handles navigation, animations, and interactions
           =========================================== */

        class SlidePresentation {
            constructor() {
                this.slides = document.querySelectorAll('.slide');
                this.currentSlide = 0;
                this.progressBar = document.querySelector('.progress-bar');
                this.navDotsContainer = document.querySelector('.nav-dots');
                this.totalSlides = this.slides.length;

                this.init();
            }

            init() {
                this.createNavDots();
                this.updateSlideVisibility();
                this.bindEvents();
            }

            createNavDots() {
                this.slides.forEach((_, index) => {
                    const dot = document.createElement('div');
                    dot.classList.add('nav-dot');
                    if (index === 0) dot.classList.add('active');
                    dot.addEventListener('click', () => this.goToSlide(index));
                    this.navDotsContainer.appendChild(dot);
                });
            }

            updateSlideVisibility() {
                const dots = document.querySelectorAll('.nav-dot');
                
                this.slides.forEach((slide, index) => {
                    if (index === this.currentSlide) {
                        slide.classList.add('visible');
                        dots[index].classList.add('active');
                    } else {
                        slide.classList.remove('visible');
                        dots[index].classList.remove('active');
                    }
                });

                // Update Progress Bar
                const progress = ((this.currentSlide + 1) / this.totalSlides) * 100;
                this.progressBar.style.width = `${progress}%`;
            }

            goToSlide(index) {
                if (index >= 0 && index < this.totalSlides) {
                    this.currentSlide = index;
                    this.slides[index].scrollIntoView({ behavior: 'smooth' });
                    this.updateSlideVisibility();
                }
            }

            nextSlide() {
                if (this.currentSlide < this.totalSlides - 1) {
                    this.goToSlide(this.currentSlide + 1);
                }
            }

            prevSlide() {
                if (this.currentSlide > 0) {
                    this.goToSlide(this.currentSlide - 1);
                }
            }

            bindEvents() {
                // Keyboard Navigation
                document.addEventListener('keydown', (e) => {
                    if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'ArrowDown') {
                        e.preventDefault();
                        this.nextSlide();
                    } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
                        e.preventDefault();
                        this.prevSlide();
                    }
                });

                // Mouse Wheel Navigation (Debounced)
                let isScrolling = false;
                window.addEventListener('wheel', (e) => {
                    if (isScrolling) return;
                    isScrolling = true;
                    
                    if (e.deltaY > 0) {
                        this.nextSlide();
                    } else {
                        this.prevSlide();
                    }

                    setTimeout(() => { isScrolling = false; }, 1000);
                });

                // Touch Swipe
                let touchStartY = 0;
                window.addEventListener('touchstart', (e) => {
                    touchStartY = e.touches[0].clientY;
                });

                window.addEventListener('touchend', (e) => {
                    const touchEndY = e.changedTouches[0].clientY;
                    const diff = touchStartY - touchEndY;

                    if (Math.abs(diff) > 50) {
                        if (diff > 0) this.nextSlide();
                        else this.prevSlide();
                    }
                });
            }
        }

        // Initialize
        new SlidePresentation();
    </script>
</body>
</html>
```


## Phase 4: File Extraction (PPT & PDF)

### Step 4.1: Detect File Type

Check the file extension provided by the user.

### Step 4.2: Extract Content (PPT/PPTX)

Use Python with `python-pptx`:

```python
from pptx import Presentation
import json
import os
import base64

def extract_pptx(file_path, output_dir):
    """
    Extract all content from a PowerPoint file.
    Returns a JSON structure with slides, text, and images.
    """
    prs = Presentation(file_path)
    slides_data = []

    # Create assets directory
    assets_dir = os.path.join(output_dir, 'assets')
    os.makedirs(assets_dir, exist_ok=True)

    for slide_num, slide in enumerate(prs.slides):
        slide_data = {
            'number': slide_num + 1,
            'title': '',
            'content': [],
            'images': [],
            'notes': ''
        }

        for shape in slide.shapes:
            # Extract title
            if shape.has_text_frame:
                if shape == slide.shapes.title:
                    slide_data['title'] = shape.text
                else:
                    slide_data['content'].append({
                        'type': 'text',
                        'content': shape.text
                    })

            # Extract images
            if shape.shape_type == 13:  # Picture
                image = shape.image
                image_bytes = image.blob
                image_ext = image.ext
                image_name = f"slide{slide_num + 1}_img{len(slide_data['images']) + 1}.{image_ext}"
                image_path = os.path.join(assets_dir, image_name)

                with open(image_path, 'wb') as f:
                    f.write(image_bytes)

                slide_data['images'].append({
                    'path': f"assets/{image_name}",
                    'width': shape.width,
                    'height': shape.height
                })

        # Extract notes
        if slide.has_notes_slide:
            notes_frame = slide.notes_slide.notes_text_frame
            slide_data['notes'] = notes_frame.text

        slides_data.append(slide_data)

    return slides_data
```

### Step 4.3: Extract Content (PDF)

Use Python with `PyMuPDF` (fitz). This is superior for extracting layout and images compared to pypdf.

```python
import fitz  # PyMuPDF
import json
import os

def extract_pdf(file_path, output_dir):
    """
    Extract all content from a PDF file.
    PDFs don't have explicit "titles" like PPT, so we use heuristics.
    """
    doc = fitz.open(file_path)
    slides_data = []

    # Create assets directory
    assets_dir = os.path.join(output_dir, 'assets')
    os.makedirs(assets_dir, exist_ok=True)

    for page_num, page in enumerate(doc):
        page_data = {
            'number': page_num + 1,
            'title': '',
            'content': [],
            'images': []
        }

        # 1. Extract Text Blocks
        # We sort blocks by vertical position (y0) then horizontal (x0)
        blocks = page.get_text("blocks")
        blocks.sort(key=lambda b: (b[1], b[0]))

        text_blocks = [b for b in blocks if b[6] == 0]  # 0 means text

        if text_blocks:
            # Heuristic: First block with font size > 15 is likely title
            # Or just first block if font size isn't available easily
            title_block = text_blocks[0]
            page_data['title'] = title_block[4].strip()  # text is at index 4
            
            # Rest are content
            for block in text_blocks[1:]:
                text = block[4].strip()
                if text:
                    page_data['content'].append({
                        'type': 'text',
                        'content': text
                    })

        # 2. Extract Images
        image_list = page.get_images()
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            
            image_name = f"pdf_page{page_num + 1}_img{img_index + 1}.{image_ext}"
            image_path = os.path.join(assets_dir, image_name)

            with open(image_path, "wb") as f:
                f.write(image_bytes)
            
            page_data['images'].append({
                'path': f"assets/{image_name}",
                'width': 0, # PDF images need bbox extraction if sizing is critical
                'height': 0 # Keeping simple for now
            })

        slides_data.append(page_data)

    doc.close()
    return slides_data
```

### Step 4.4: Confirm Content Structure

Present the extracted content to the user in their language:

```
I've extracted the following from your [PowerPoint/PDF]:
(我已经从您的 [PowerPoint/PDF] 中提取了以下内容：)

**Slide 1: [Title]**
- [Content summary]
- Images: [count]

**Slide 2: [Title]**
- [Content summary]
- Images: [count]

...

All images have been saved to the assets folder.
(所有图片已保存至 assets 文件夹。)

Does this look correct? Should I proceed with style selection?
(这看起来正确吗？我应该继续进行风格选择吗？)
```

### Step 4.5: Style Selection

Proceed to Phase 2 (Style Discovery) with the extracted content in mind.

### Step 4.6: Generate HTML

Convert the extracted content into the chosen style, preserving:
- All text content
- All images (referenced from assets folder)
- Slide order
- Any speaker notes (as HTML comments or separate file)


## Phase 5: Delivery

### Final Output

When the presentation is complete:

1.  **Clean up temporary files**
    -   Delete `.claude-design/slide-previews/` if it exists

2.  **Open the presentation**
    -   Use `open [filename].html` to launch in browser

3.  **Provide summary (in user language)**
```
Your presentation is ready!
(您的演示文稿已经准备好了！)

📁 File: [filename].html
🎨 Style: [Style Name]
📊 Slides: [count]

**Navigation:**
(导航方式：)
- Arrow keys (← →) or Space to navigate
- (使用方向键或空格键翻页)

**To customize:**
(自定义方法：)
- Colors: Look for `:root` CSS variables at the top
- Fonts: Change the Fontshare/Google Fonts link

Would you like me to make any adjustments?
(您还需要做任何调整吗？)
```

## Style Reference: Effect → Feeling Mapping

Use this guide to match animations to intended feelings:

### Dramatic / Cinematic
- Slow fade-ins (1-1.5s)
- Large scale transitions (0.9 → 1)
- Dark backgrounds with spotlight effects
- Parallax scrolling
- Full-bleed images

### Techy / Futuristic
- Neon glow effects (box-shadow with accent color)
- Particle systems (canvas background)
- Grid patterns
- Monospace fonts for accents
- Glitch or scramble text effects
- Cyan, magenta, electric blue palette

### Playful / Friendly
- Bouncy easing (spring physics)
- Rounded corners (large radius)
- Pastel or bright colors
- Floating/bobbing animations
- Hand-drawn or illustrated elements

### Professional / Corporate
- Subtle, fast animations (200-300ms)
- Clean sans-serif fonts
- Navy, slate, or charcoal backgrounds
- Precise spacing and alignment
- Minimal decorative elements
- Data visualization focus

### Calm / Minimal
- Very slow, subtle motion
- High whitespace
- Muted color palette
- Serif typography
- Generous padding
- Content-focused, no distractions

### Editorial / Magazine
- Strong typography hierarchy
- Pull quotes and callouts
- Image-text interplay
- Grid-breaking layouts
- Serif headlines, sans-serif body
- Black and white with one accent

---

## Animation Patterns Reference

### Entrance Animations

```css
/* Fade + Slide Up (most common) */
.reveal {
    opacity: 0;
    transform: translateY(30px);
    transition: opacity 0.6s var(--ease-out-expo),
                transform 0.6s var(--ease-out-expo);
}

.visible .reveal {
    opacity: 1;
    transform: translateY(0);
}

/* Scale In */
.reveal-scale {
    opacity: 0;
    transform: scale(0.9);
    transition: opacity 0.6s, transform 0.6s var(--ease-out-expo);
}

/* Slide from Left */
.reveal-left {
    opacity: 0;
    transform: translateX(-50px);
    transition: opacity 0.6s, transform 0.6s var(--ease-out-expo);
}

/* Blur In */
.reveal-blur {
    opacity: 0;
    filter: blur(10px);
    transition: opacity 0.8s, filter 0.8s var(--ease-out-expo);
}
```

### Background Effects

```css
/* Gradient Mesh */
.gradient-bg {
    background:
        radial-gradient(ellipse at 20% 80%, rgba(120, 0, 255, 0.3) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 20%, rgba(0, 255, 200, 0.2) 0%, transparent 50%),
        var(--bg-primary);
}

/* Noise Texture */
.noise-bg {
    background-image: url("data:image/svg+xml,..."); /* Inline SVG noise */
}

/* Grid Pattern */
.grid-bg {
    background-image:
        linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
    background-size: 50px 50px;
}
```

### Interactive Effects

```javascript
/* 3D Tilt on Hover */
class TiltEffect {
    constructor(element) {
        this.element = element;
        this.element.style.transformStyle = 'preserve-3d';
        this.element.style.perspective = '1000px';
        this.bindEvents();
    }

    bindEvents() {
        this.element.addEventListener('mousemove', (e) => {
            const rect = this.element.getBoundingClientRect();
            const x = (e.clientX - rect.left) / rect.width - 0.5;
            const y = (e.clientY - rect.top) / rect.height - 0.5;

            this.element.style.transform = `
                rotateY(${x * 10}deg)
                rotateX(${-y * 10}deg)
            `;
        });

        this.element.addEventListener('mouseleave', () => {
            this.element.style.transform = 'rotateY(0) rotateX(0)';
        });
    }
}
```


## Troubleshooting

### Common Issues

**Fonts not loading:**
- Check Fontshare/Google Fonts URL
- Ensure font names match in CSS

**Animations not triggering:**
- Verify Intersection Observer is running
- Check that `.visible` class is being added

**Scroll snap not working:**
- Ensure `scroll-snap-type` on html/body
- Each slide needs `scroll-snap-align: start`

**Mobile issues:**
- Disable heavy effects at 768px breakpoint
- Test touch events
- Reduce particle count or disable canvas

**Performance issues:**
- Use `will-change` sparingly
- Prefer `transform` and `opacity` animations
- Throttle scroll/mousemove handlers

**PDF Extraction Issues:**
- PyMuPDF is required (`pip install pymupdf`).
- PDFs as images (scanned docs) won't have text extract. Use OCR logic if needed (optional advanced feature).

