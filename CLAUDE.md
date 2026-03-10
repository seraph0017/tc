# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**teachter** is a teaching content production system that transforms source articles into structured educational deliverables. It uses a 4-agent pipeline to produce three synchronized outputs from raw technical articles: course handouts (讲义), lecture scripts (讲课稿), and presentation slides (课件).

## Agent Pipeline Architecture

The production workflow follows a strict sequential pipeline with defined dependencies:

```
Curriculum-Architect (课程架构师)
       |
       v  outputs course-design.md
Writing-Specialist (Agent-A, P0)  -->  handout/*.md
       |
       |  (after 50% handout completion)
       v
Lecture-Script-Creation-Specialist (Agent-B, P1)  -->  script/*.md
Educational-PPT-Design (Agent-C, P1)              -->  slides/*.md
       |
       v
Curriculum-Architect (终审 final review)
```

- **Curriculum-Architect** initiates projects: reads source material, confirms requirements (topic, audience, duration, objectives), outputs a 3-in-1 outline. Also performs final review using checklist in course-design.md Section 7.
- **Writing-Specialist** produces handouts with complete runnable code, teaching annotations, knowledge supplements (`[知识补给站]`), and self-test questions per module.
- **Lecture-Script-Creation-Specialist** converts handouts into verbatim lecture scripts with per-minute timing, interaction markers (`[互动]`, `[演示]`, `[练习]`), and natural transitions.
- **Educational-PPT-Design** designs slide decks following "one topic per page, max 3 lines, keywords over sentences" principle. Pages typed as `[COVER]`, `[CONCEPT]`, `[DIAGRAM]`, `[CODE]`, `[QUESTION]`, etc.

## Directory Structure

```
origin/           # Source articles (read-only input)
course-design.md  # Master course design plan (Curriculum-Architect output)
handout/          # lesson-01-*.md to lesson-06-*.md (Writing-Specialist output)
script/           # lesson-01-script.md to lesson-06-script.md (Lecture-Script output)
slides/           # lesson-01-slides.md to lesson-06-slides.md (PPT-Design output)
.claude/agents/   # Agent definition files
```

## Key Rules for Content Production

1. **Three-carrier sync**: Handout module X.Y, script section X.Y, and slide X-Y must use unified numbering and cross-reference each other.
2. **Code consistency**: Same code across all three carriers must be character-level identical. Slides extract subsets from handout code only.
3. **Depth gradient**: Slides = "1" (core sentence), Script = "3" (explanation + analogy), Handout = "10" (complete knowledge + code + extensions).
4. **Interaction alignment**: Every `[互动]` in script must have a corresponding `[QUESTION]` slide page.
5. **Content language**: Chinese (follows source material). Use Chinese punctuation consistently.
6. **Slide density**: Max 5 lines / 50 chars per page text, max 15 lines per code page.

## Current Project State

- Source material: `origin/clawbot-to-openclaw-journey.md` (AI Agent system evolution, 9 chapters)
- Course: "AI Agent系统工程实战" - 6 lessons x 3 hours = 18 hours total
- Agent-A handout files go in `handout/`, Agent-B scripts in `script/`, Agent-C slides in `slides/`
