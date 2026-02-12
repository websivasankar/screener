#!/bin/bash
rm -f .git/index.lock
rm -f .git/refs/heads/*.lock
rm -f .git/refs/remotes/origin/*.lock
echo "Git locks cleaned!"