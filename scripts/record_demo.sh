#!/usr/bin/env bash
set -u

clear_screen() {
  printf '\033c'
}

prompt() {
  printf '\033[1;35m$\033[0m %s\n' "$1"
}

clear_screen
printf '\033[1;35mRAGOps\033[0m — catch regressions before production\n\n'
printf 'No clone · no account · no model credential\n'
sleep 2

prompt 'uvx ragops demo'
uvx ragops demo
sleep 5

clear_screen
printf '\033[1;34m1 / ACCEPTED BASELINE\033[0m\n\n'
prompt 'uvx ragops evaluate --scenario ragops-demo/scenario.json --responses ragops-demo/baseline.json --format markdown'
uvx ragops evaluate \
  --scenario ragops-demo/scenario.json \
  --responses ragops-demo/baseline.json \
  --format markdown
sleep 10

clear_screen
printf '\033[1;33m2 / REGRESSED CANDIDATE\033[0m\n\n'
prompt 'open ragops-demo/release-report.md'
sed -n '1,80p' ragops-demo/release-report.md
sleep 15

clear_screen
printf '\n\033[1;31mBLOCK\033[0m  Release stopped before production.\n\n'
printf 'Metric deltas and named reasons are saved in:\n'
printf '  \033[1;36mragops-demo/release-report.html\033[0m\n\n'
printf 'Fix the candidate, then run the same gate again.\n'
sleep 12
