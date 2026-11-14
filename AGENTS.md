# MangoSpace

NASA Space Apps 2026 submission for [Dancing with the SARs](https://www.spaceappschallenge.org/2026/challenges/dancing-with-the-sars/).
Status: building. Plan: https://claude.ai/artifact/RnQvBADeQY7pRJLrBH8YR8

## Stack

- `app/`: Next.js (static export, no server), TypeScript, MapLibre GL JS, SVG charts, Web Audio. Deploys to Vercel.
- `pipeline/`: Python 3.12 with uv. Runs offline. Writes JSON and PNG files into `app/public/data`.
- `app/lib/data.ts` is the data contract between the two. Only the tech lead changes it.
- The app reads only `app/public/data`. Do not call NASA services from the browser.
- Checks before a PR: `cd app && npm run lint && npm run build && npm test`.

## Tools

| Tool | For | Setup |
| --- | --- | --- |
| pstack | How agents work (below) | See Workflow |
| Shortcut | Stories, epics, iterations. The team's source of truth for who does what | MCP in `.mcp.json`. Each person signs in once through `/mcp` |
| Playwright | Driving the app in a real browser for tests and proof | MCP in `.mcp.json`. Needs Node 18+ and Chrome |

- Every task starts from a Shortcut story. Put the story ID in the branch name (`sc-123-short-name`) and at the end of the PR title (`[sc-123]`), and have the agent read the story before it starts.
- Proof screenshots and videos come from Playwright.

## Workflow: pstack

Every teammate installs pstack once:

```
/plugin marketplace add cursor/plugins
/plugin install pstack@cursor-plugins
/pstack:setup-pstack
```

In Claude Code every pstack command has the `pstack:` prefix, for example `/pstack:poteto-mode`.

### Every real task

1. Start from the Shortcut story: `/pstack:poteto-mode do sc-123`. It picks the playbook and the skills.
2. If the story or report is vague, have the agent restate the problem in its own words before it writes code.
3. End the prompt with "verify with Playwright and attach screenshots as proof". Passing tests or a clean compile is not proof.
4. If you don't understand a choice it made: `/pstack:teach me why you did it this way and not X`.

Skip this for typos and one-line changes.

### Before a big or unclear feature

Stop at the first step that settles it:

1. Understand: `/pstack:how`, `/pstack:why`, `/pstack:recall`.
2. Explore: `/pstack:poteto-mode prototype a few options for X`. Throwaway versions with screenshots beat a debate.
3. Design: `/pstack:architect X` when other code will depend on it (core data types, a module boundary, an API).
4. Plan: `/pstack:poteto-mode turn this design into a plan` only if it spans several PRs. Delete the plan once it merges.

Don't accept the first design, and don't over-plan on paper. If the code needs `any`, forced casts, or the same workaround in several places, the design is wrong. Throw it away.

### Verification (Playwright)

After any UI change, the agent starts the dev server, drives the change through the Playwright MCP the way a user would, checks the console and network for errors, and attaches screenshots. Fix failures before reporting back.

Two layers:

- **Playwright MCP**: live, ad-hoc checks. Exploring, reproducing bugs, proof screenshots.
- **Playwright Test** (committed specs): the reusable control tool. Any check you'll need again becomes a spec. Video and traces come from here (`video: 'on'`, `trace: 'on'`). The MCP can generate the TypeScript for the steps it took.

Setup order:

1. Build a web app, so Playwright can drive it.
2. Once the first screen runs: `npm init playwright@latest` and one smoke spec (app loads, no console errors). Add one command that starts the dev server and seeds sample data.
3. Right after: `/pstack:create-verification-skill`. It wraps the Playwright flows into a control skill and builds the Feature Map. Done: the skill is `verify-hubas` (`.claude/skills/verify-hubas/`), and its control tool is `cd app && npm run control -- help`.
4. After each batch of features: `/pstack:maintain-verification-skill`.

Upkeep:

- An agent clicking the same steps by hand through the MCP again means that flow should be a committed spec.
- Fix a flaky spec immediately. Flaky checks train everyone to ignore checks.
- When an agent struggles to drive the app, fix the control tool first.

### By task type

| Task | Prompt |
| --- | --- |
| Bug | `/pstack:poteto-mode reproduce sc-123 with Playwright first, then fix and show the same flow passing` |
| UI choice | `/pstack:poteto-mode prototype 3 options, Playwright screenshots of each` |
| Slow page | `/pstack:poteto-mode record a Playwright trace of the current state first`, fix, then `/pstack:swarm` repeated runs to confirm |
| Demo for judges | Record a Playwright video of the main flow |

## Commit messages

Commit subjects and PR titles use Conventional Commits, with the Shortcut story ID at the end:

```
<type>: <summary> [sc-123]
```

| Type | For |
| --- | --- |
| `feat` | A new thing the user can see or do |
| `fix` | A bug fix |
| `refactor` | A code change with no change in behavior |
| `perf` | A speed improvement |
| `test` | Specs only |
| `docs` | Documentation only |
| `data` | Pipeline output in `app/public/data` |
| `ci` | Workflows and build setup |
| `chore` | Other upkeep: dependencies, config, cleanup |

- The summary is in the imperative, lower case, with no period, 72 characters or less: `feat: add play button to the time slider [sc-84]`.
- One type for each commit. If a commit needs two types, split it.
- Leave out `[sc-123]` only for typos and one-line changes that have no story.
- The body, if any, says why. The diff shows what.

## Pull requests

The tech lead reviews every PR. To get a PR merged:

- The title has the same format as a commit subject.
- The description follows `.github/pull_request_template.md`. GitHub fills it in when you open a PR. With `gh pr create`, start the body from that file.

- Small and single-purpose. One change per PR.
- The description includes Playwright proof: screenshots, a video, or a test run. A PR that adds or changes a user flow includes its Playwright spec.
- Run `/pstack:no-comments` before opening it. Keep comments that explain why, drop ones that narrate what.
- Write docs and PR descriptions with `/pstack:technical-writing` or `/pstack:unslop`.

### Tech lead toolkit

| Situation | Use |
| --- | --- |
| Any UI PR | Check out the branch, ask Claude to run its flow with Playwright and show you |
| Small PR you don't fully trust | `/pstack:blast-radius` |
| Risky or disputed PR | `/pstack:interrogate` |
| PR you don't understand | `/pstack:teach` |
| Same mistake shows up a second time | `/pstack:correct` (turn it into a type, lint, or test) |
| Lessons after a long agent session | `/pstack:reflect` |
| Refactor or migration | `/pstack:poteto-mode` refactoring playbook: lock in current behavior first, delete before adding, move callers and delete the old API in the same change |

Skip the Cursor-only parts of pstack (cloud agents, Bugbot, Automations).
