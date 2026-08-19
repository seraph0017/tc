# AGENTS.md

Guidance for Codex when working in this repository.

## Project

- This repository contains AI Agent teaching-course materials.
- User-facing content should be written in Chinese unless a source file clearly uses another language.
- The course outputs are private teaching materials; do not introduce public-license or publication assumptions.

## Structure

- `README.md` is the repository index.
- Each course directory follows this shape:
  - `course-design.md`: master course design.
  - `origin/`: source material. Treat as read-only input.
  - `handout/`: full reference handouts.
  - `script/`: lecture scripts with timing and interaction markers.
  - `slides/`: Markdown slide scripts.
  - `ppt/`: generated presentation files.

## Content Rules

- Keep the three teaching carriers synchronized: handout section, script section, and slide page should use consistent numbering and terminology.
- Preserve the depth gradient: slides are concise focus points, scripts are spoken explanations, handouts are complete references.
- For slides, prefer one topic per page, keywords over long sentences, and low text density.
- Every script `[互动]` should have a corresponding question or interaction slide.
- Code shown in slides or scripts should match the canonical handout code unless explicitly adapting it for display.

## Editing Rules

- Do not rewrite `origin/` source material unless the user explicitly asks.
- Keep course language, audience level, and lesson duration aligned with each course `README.md` and `course-design.md`.
- Avoid unrelated cleanup. Keep generated assets and large binary outputs unchanged unless they are part of the requested task.
- When changing scripts that generate slides or PPT files, run the narrowest relevant verification command and report whether generated outputs were updated.
