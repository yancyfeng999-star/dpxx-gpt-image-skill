# GPT Image Workflow

1. Confirm `ROOTFLOWAI_GPT_API_KEY` or receive the key from the user for one-time `--api-key` use.
2. Choose resolution:
   - `1K` -> `gpt-image-2-count`
   - `2K` -> `gpt-image-2-hd-count`
   - `4K` -> `gpt-image-2-4k-count`
3. Choose ratio. For 4K, only use `16:9`, `9:16`, `2:1`, `1:2`, `21:9`, or `9:21`.
4. Build the prompt from `references/prompt-patterns.md` or the six-slot fallback.
5. Confirm the final command summary with the user.
6. Run `generate_image.py` or `edit_image.py`.
7. Report the saved path, model, ratio, quality, and any skipped response items.
