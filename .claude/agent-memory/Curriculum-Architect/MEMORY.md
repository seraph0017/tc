# Curriculum Architect Memory

## Project Structure
- Origin article: /Users/xunan/Projects/teachter/origin/clawbot-to-openclaw-journey.md (2586 lines, ~30k words, 9 chapters)
- Course design: /Users/xunan/Projects/teachter/course-design.md
- Output dirs: handout/, script/, slides/ (each gets 6 lesson files)

## Course Design Decisions
- 6 lessons x 3 hours = 18 total hours
- Lesson 5 (quant trading) is optional/advanced
- Original chapters 6+7 merged into Lesson 4; chapters 8+9 merged into Lesson 6
- Target audience: 1-3 year Python devs transitioning to AI Agent development
- Three deliverable types: Handout (P0), Script (P1), Slides (P1)

## Execution Order
- Agent-A (Handout) starts first - other agents depend on it
- Agent-B (Script) and Agent-C (Slides) can start after Agent-A delivers 50%
- Curriculum Architect does final review after all three complete

## Key Patterns
- Use module numbering X.Y consistently across all three deliverables
- Code must be character-level identical across deliverables (handout is source of truth)
- Every [interactive] tag in script must have matching [QUESTION] page in slides
- Slides: max 15 lines of code per page, max 5 lines/50 chars of text per page
