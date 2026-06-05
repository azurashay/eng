# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A static HTML/CSS/JS vocabulary game site for Israeli schoolchildren learning English from the "Hey" textbook. No build system, no package manager, no framework — just plain HTML files opened directly in a browser.

## How to run

Open any `.html` file directly in a browser. No server needed. On Mac:

```bash
open index.html
```

## Project structure

- `index.html` — main hub linking to all games
- `learn.html` — flashcard-style vocabulary viewer with TTS (Web Speech API), search, and unit tabs
- `game1-memory.html` — flip-card memory matching game (English ↔ Hebrew pairs)
- `game2-quiz.html` — multiple-choice quiz
- `game3-hangman.html` — hangman game
- `mate/game4-math.html` — separate math game (percentages & volume), not linked from index
- `eng-repo/` — backup copy of the main files, not the active version

## Vocabulary data

All vocab lives in `learn.html` inside the `VOCAB` object — a JS object keyed by unit number (1, 2, 3), each an array of `{en, he, tr}` objects (English, Hebrew, Hebrew transliteration). The game files (`game1`, `game2`, `game3`) each embed their own copy of this data — if you add words, update all four files.

## Key patterns

- All pages are RTL (`<html dir="rtl">`) with Hebrew UI text
- TTS is handled via `window.speechSynthesis` with `lang='en-US'` for English pronunciation
- No external dependencies except `mate/game4-math.html` which loads Heebo from Google Fonts
- Styling is all inline `<style>` blocks — no separate CSS files
