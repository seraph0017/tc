# Lecture Script Creation Specialist - Memory

## Project Structure
- Course design: `/Users/xunan/Projects/teachter/course-design.md`
- Handouts: `/Users/xunan/Projects/teachter/handout/lesson-XX-*.md`
- Scripts: `/Users/xunan/Projects/teachter/script/lesson-XX-script.md`
- Slides: `/Users/xunan/Projects/teachter/slides/lesson-XX-slides.md`
- Total: 6 lessons, 3h each, AI Agent Systems Engineering course

## Script Standards
- Target: 4,000-5,000 Chinese characters per lesson (approx 5,000-6,000 with English terms)
- Tags: [互动] [演示] [练习] [讨论] [切换幻灯片到X-Y]
- Module numbering: 环节X.Y aligns with handout 模块X.Y and slides Slide X-Y
- Must include: opening hook, minute-level timestamps, transitions, 3-sentence closing summary
- Interactive node every 20 minutes minimum
- Code: only highlight key lines, explain "why" not "what"
- First person, colloquial Chinese, teacher perspective

## Lessons Completed
- Lesson 1 (memory system): ~5,400 chars - done
- Lesson 2 (model routing): ~4,800 chars - done
- Lesson 3 (multi-agent): ~5,800 chars - done
- Lessons 4-6: not yet started

## Key Patterns
- Chinese char count via `re.findall(r'[\u4e00-\u9fff]', text)` is the proper metric
- `wc -w` severely undercounts Chinese text - never rely on it
- Each lesson handout is 800-1500 lines, read fully before scripting
