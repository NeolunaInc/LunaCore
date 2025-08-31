#!/usr/bin/env bash
set -Eeuo pipefail

echo "Fetching and pruning remote branches..."
git fetch --all --prune

echo "Remote branches not merged into origin/main:"
branches=$(git branch -r --no-merged origin/main | grep -vE '->|origin/main' || true)

if [ -z "$branches" ]; then
    echo "(none)"
    exit 0
fi

echo "$branches"

declare -a to_delete_remote=()
declare -a to_delete_both=()

while IFS= read -r branch; do
    if [ -z "$branch" ]; then continue; fi
    branch=$(echo "$branch" | sed 's|origin/||')
    echo
    echo "Branch: $branch"
    echo "[k]eep (default), [d]elete remote only, [b]oth (delete remote + local)"
    read -p "Choice: " choice
    choice=${choice:-k}
    case $choice in
        d|D)
            to_delete_remote+=("$branch")
            ;;
        b|B)
            to_delete_both+=("$branch")
            ;;
        k|K|*)
            echo "Keeping $branch"
            ;;
    esac
done <<< "$branches"

echo
echo "Summary:"
if [ ${#to_delete_remote[@]} -gt 0 ]; then
    echo "Delete remote only: ${to_delete_remote[*]}"
fi
if [ ${#to_delete_both[@]} -gt 0 ]; then
    echo "Delete both: ${to_delete_both[*]}"
fi

if [ ${#to_delete_remote[@]} -eq 0 ] && [ ${#to_delete_both[@]} -eq 0 ]; then
    echo "No deletions."
    exit 0
fi

read -p "Proceed with deletions? (y/N): " confirm
if [[ ! $confirm =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

for branch in "${to_delete_remote[@]}"; do
    echo "Deleting remote branch origin/$branch"
    git push origin --delete "$branch"
done

for branch in "${to_delete_both[@]}"; do
    echo "Deleting remote branch origin/$branch"
    git push origin --delete "$branch"
    if git branch -l | grep -q "$branch"; then
        echo "Deleting local branch $branch"
        git branch -D "$branch"
    fi
done

echo "Cleanup complete."
