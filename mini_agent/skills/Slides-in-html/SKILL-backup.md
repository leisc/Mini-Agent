---

name: slides-in-html
description: Create stunning, animation-rich HTML presentations from scratch or by converting PowerPoint files. Automatically adapts to the user's language (e.g., English -> English, Chinese -> Chinese) for both communication and slide content.
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
- If input is English -> Set mode to English.
- If input is Chinese (Simplified/Traditional) -> Set mode to Chinese.
- If input is other languages -> Set mode accordingly.

**Mode A: New Presentation**
- User wants to create slides from scratch.
- Proceed to Phase 1 (Content Discovery).

**Mode B: PPT Conversion**
- User has a PowerPoint file (.ppt, .pptx) to convert.
- Proceed to Phase 4 (PPT Extraction). *Note: The target language for the web presentation should match the source PPT content.*

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

**REFERENCE: existing styles for reference**
- ./STYLE_PRESENTS.md

### Step 2.3: Present Previews

Create the previews in: `./slide-previews/`

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
<html lang="zh-CN"> <!-- DYNAMIC: Change to 'en', 'ja', etc. based on user lang -->
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>演示文稿标题</title> <!-- DYNAMIC: Title in user language -->

    <!-- Fonts: CRITICAL to match language -->
    <!-- Chinese Example -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;700&family=Noto+Serif+SC:wght@400;700&display=swap" rel="stylesheet">

    <style>
        /* ===========================================
           CSS CUSTOM PROPERTIES (THEME)
           =========================================== */
        :root {
            /* Colors */
            --bg-primary: #0a0f1c;
            --text-primary: #ffffff;
            --accent: #00ffcc;

            /* Typography: DYNAMIC FONTS */
            /* Ensure line-height is larger for CJK characters (1.6 - 1.8) */
            --font-display: 'Noto Sans SC', sans-serif;
            --font-body: 'Noto Sans SC', sans-serif;

            /* Spacing */
            --slide-padding: clamp(2rem, 5vw, 4rem);
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: var(--font-body);
            background: var(--bg-primary);
            color: var(--text-primary);
            overflow-x: hidden;
            /* Enhance legibility for CJK */
            -webkit-font-smoothing: antialiased;
            text-rendering: optimizeLegibility;
        }

        /* ... (Keep existing slide structure) ... */
    </style>
</head>
<body>
    <!-- Navigation hints must be in user language -->
    <div class="keyboard-hint">按空格键或点击翻页</div>

    <section class="slide title-slide">
        <h1 class="reveal">这里是您的标题</h1>
        <p class="reveal">副标题或演讲者信息</p>
    </section>

    <script>
        /* ===========================================
           SLIDE PRESENTATION CONTROLLER
           =========================================== */
        class SlidePresentation {
            constructor() {
                this.slides = document.querySelectorAll('.slide');
                this.currentSlide = 0;
                this.init();
            }

            init() {
                // ... event listeners ...
                this.updateUI();
            }

            updateUI() {
                // Update progress bar or navigation dots
                // Ensure no hardcoded English text appears here
            }
        }
    </script>
</body>
</html>
```

### Localization Requirements

When generating the final HTML:

1.  **`lang` Attribute:** The `<html>` tag must have the correct language code (e.g., `lang="zh-CN"`, `lang="en"`).
2.  **Content:** All slide text, headings, and button labels must be in the target language.
3.  **UI Strings:** If you include JS-based alerts or hints (e.g., "Press Space"), translate them.
    - EN: "Press Space or Click to navigate"
    - ZH: "按空格键或点击翻页"
4.  **Typography Adjustments:**
    - For Chinese/Japanese: Use `letter-spacing: 0.05em` often helps readability for headings.
    - Increase `line-height` to 1.6 or 1.7 for body text in non-Latin scripts.

## Phase 4: PPT Conversion

### Step 4.1: Extract Content

Use the existing Python script (`python-pptx`). It extracts raw bytes, so it handles any character set automatically.

### Step 4.2: Confirm Content Structure

Present the extracted content to the user **in the language of the extracted text** (or the language they used to ask for the conversion).

```
I've extracted the following from your PowerPoint:
(我已经从您的 PowerPoint 中提取了以下内容：)

**Slide 1: [Title]**
- [Content summary]
...

Does this look correct? Should I proceed with style selection?
(这看起来正确吗？我应该继续进行风格选择吗？)
```

### Step 4.3: Style Selection & Generation

Proceed to Phase 2, but ensure the **Style Preview text** uses dummy text in the same language as the extracted PPT content.

If the PPT is in Chinese, generate previews with Chinese titles ("标题示例", "副标题") so the user can judge the typography correctly.


## Phase 5: Delivery

### Final Output

1.  **Open the presentation.**
2.  **Provide summary in user's language.**

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
- Colors: Look for `:root` CSS variables
- Fonts: Change the Google Fonts link

Would you like me to make any adjustments?
(您还需要做任何调整吗？)
```


## Enhanced Style Reference: Multilingual Typography

When designing for specific languages, adjust typography accordingly:

### For Chinese Presentations (Zh)
- **Fonts:** Noto Sans SC, PingFang SC, Microsoft YaHei.
- **Weight:** Use bolder weights (700/900) for titles to ensure impact.
- **Spacing:** Increase letter-spacing slightly for titles (`0.05em`).
- **Alignment:** Strict center-alignment or left-alignment works best; avoid justified text as it creates awkward gaps between characters (hanzi).

### For Japanese Presentations (Ja)
- **Fonts:** Noto Sans JP, Hiragino Kaku Gothic Pro.
- **Vertical Mode:** Consider `writing-mode: vertical-rl` for a traditional editorial look on specific accent slides.

### For English/Western Presentations
- **Fonts:** Clash Display, Satoshi, Inter, DM Sans.
- **Contrast:** Can afford tighter tracking and varying line-heights.


## Animation Patterns Reference (Cultural Context)

### Dramatic / Cinematic (Suitable for Asian Markets)
- Large, bold typography with slow reveals.
- Red/Gold palettes often imply prestige in Chinese contexts (unless modern tech).
- Vertical text transitions.

### Techy / Futuristic
- Neon glow effects work universally.
- Glitch effects are very popular in Japanese cyberpunk aesthetics.


## Troubleshooting

### Fonts not loading (Language Specific)
- Verify Google Fonts URL includes the specific subset (e.g., `&subset=chinese-simplified`).
- Ensure `font-family` stack includes a fallback to system fonts (e.g., `"Microsoft YaHei", sans-serif`).

### Garbled Text (Mojibake)
- Ensure `<meta charset="UTF-8">` is present.
- If extracting from PPT, ensure Python script handles encoding correctly (default `utf-8` usually works).

### Layout Breaking with Long Words
- CJK characters don't wrap like English words. Ensure containers handle overflow or use `word-break: break-all` only if strictly necessary for long URLs.


## Example Session Flow (Bilingual)

**Scenario A (English):**
1. User: "I want a pitch deck for my coffee startup."
2. Skill (English): "Purpose? What is this for?" -> [Pitch deck, Tutorial...]
3. Skill: Generates previews with text "Presentation Title", "Coffee Startup".
4. Output: Full English HTML.

**Scenario B (Chinese):**
1. User: "我想为我的咖啡创业公司做一个路演 PPT。"
2. Skill (Chinese): "演示目的？这个演示文稿的用途是什么？" -> [商业路演, 教学...]
3. Skill: Generates previews with text "演示文稿标题", "咖啡创业公司" (using Noto Sans SC).
4. Output: Full Chinese HTML with `lang="zh-CN"`, hints reading "按空格键翻页".

