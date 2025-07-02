#!/bin/bash
# tm-test-guard.sh – Prevent commits if tests fail and remind about TDD Red → Green flow
set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

echo -e "${YELLOW}tm-test-guard: running pytest...${NC}"
pytest -q
PYTEST_EXIT=$?

echo -e "${YELLOW}tm-test-guard: running npm test (if present)...${NC}"
# npm test returns 0 if script missing with --if-present flag
npm test --silent --if-present
NPM_EXIT=$?

if [[ $PYTEST_EXIT -ne 0 || $NPM_EXIT -ne 0 ]]; then
  echo -e "${RED}❌ Tests failed. Commit aborted.${NC}"
  exit 1
fi

echo -e "${GREEN}✅ All tests passed.${NC}"
read -p "Did you first see FAILING tests before making them pass? (y/N) " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
  echo -e "${RED}Commit aborted by tm-test-guard – ensure TDD Red phase occurred.${NC}"
  exit 1
fi

exit 0 