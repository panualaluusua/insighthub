#!/bin/bash
# Usage: ./scripts/gemini/code-review.sh path/to/file_or_dir
gemini -p "Review this code for best practices and security issues:" "$1" --all_files 