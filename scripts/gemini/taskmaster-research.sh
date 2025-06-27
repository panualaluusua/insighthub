#!/bin/bash
# Usage: ./scripts/gemini/taskmaster-research.sh "Your research prompt or Taskmaster task description"
gemini -p "Research and summarize the following task or question: $1" 