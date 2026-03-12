---
applyTo: commit
---

# GitHub Copilot Commit Instructions

Use conventional commits: `type(scope): subject`

## Commit Types (mandatory)

| Type       | Use                         |
| ---------- | --------------------------- |
| `feat`     | New features                |
| `fix`      | Bug fixes                   |
| `docs`     | Documentation               |
| `style`    | Formatting (no code change) |
| `refactor` | Code changes (no feat/fix)  |
| `perf`     | Performance                 |
| `test`     | Tests                       |
| `build`    | Build/dependencies          |
| `ci`       | CI config                   |
| `chore`    | Maintenance                 |
| `revert`   | Reverts                     |

## Scopes (recommended, lowercase)

| Scope                      | Area                                   |
| -------------------------- | -------------------------------------- |
| `api`                      | Backend/API                            |
| `next` / `ui` / `frontend` | Next.js/React pages, components, hooks |
| `db`                       | Database (PostgreSQL)                  |
| `auth`                     | Authentication                         |
| `utils`                    | Helpers                                |
| `config`                   | Config/env                             |
| `core`                     | App logic                              |
| `deps`                     | Dependencies                           |
| `styles`                   | CSS/Tailwind                           |

## Subject Rules

- Imperative mood: `add`, `fix`, `update` — not `added`, `fixed`
- ≤72 chars, lowercase after `type(scope):`, no trailing period
- Be specific: what + where

## Body (bullets, detailed)

- Technical details: files, classes, methods, tech used
- Why/context/impact
- Breaking changes noted

## Footer

```
Closes #123.
BREAKING CHANGE: description of breaking change
```

## Commit Command (mandatory)

**Never use `git commit -m` with multiline text — it breaks in the terminal tool and truncates the body onto the subject line.**

Always write the message to `/tmp/cm.txt` using a heredoc, commit with `-F`, delete the file, then **immediately print a confirmation line** with `git log -1`. This last step is critical — the terminal tool truncates long output so the commit result is often invisible. The log line guarantees you always see proof it landed.

```bash
cat > /tmp/cm.txt << 'EOF'
type(scope): subject

- bullet 1
- bullet 2
- bullet 3
EOF
git commit -F /tmp/cm.txt && rm /tmp/cm.txt && git log -1 --format="✓ committed: %h %s"
```

**Never retry a commit** if the output looks empty or cut off — the terminal truncates long output and the commit very likely succeeded. Always check the log first before doing anything:

```bash
git log origin/main..HEAD --format="%h %s"
```

Only if the commit is genuinely absent should you try again.

For amending an unpushed commit:

```bash
cat > /tmp/cm.txt << 'EOF'
type(scope): subject

- bullet 1
- bullet 2
EOF
git commit --amend -F /tmp/cm.txt && rm /tmp/cm.txt && git log -1 --format="✓ amended: %h %s"
```

## Grouping Rules (Logical commits)

Group changes if they are:

- Part of a single feature or bug fix
- Functionally dependent on each other
- In the same module/scope (e.g., Next.js page + hook + styles + test)
- Multiple changes in a single file → use multiple bullet points

Stage incrementally: `git add <group>`, commit, repeat.

## Examples

**Next.js feature:**

```
feat(next): add dashboard analytics page

- Create app/dashboard/page.tsx with RSC data fetch
- Add hooks/useDashboard.ts with caching
- Implement components/DashboardChart.tsx (Tailwind responsive)
- Add tests/dashboard.test.tsx (loading/error states)
```

**Backend fix:**

```
fix(api): resolve auth token refresh

- Update FastAPI AuthController refresh endpoint
- Add SQLAlchemy model validation
- Include perf optimization for DB query
```

**Multi-file group:**

```
git add app/profile/page.tsx hooks/useProfile.ts styles/profile.css tests/profile.test.tsx

feat(next): add user profile page

- Create app/profile/page.tsx with server-side data fetch
- Add hooks/useProfile.ts with optimistic updates
- Style profile layout in styles/profile.css (Tailwind)
- Add tests/profile.test.tsx (loading/error/success)
```
