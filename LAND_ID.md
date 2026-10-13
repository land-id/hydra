# Land id's Hydra fork

The `land-id` branch is the default branch of this fork and what we deploy. It
tracks [Ory Hydra](https://github.com/ory/hydra)'s `master` branch plus a
short list of our own commits. Ory releases open-source Hydra about once a
year, but keeps committing fixes to `master` in between, so we deploy `master`
rather than waiting for releases.

`.github/workflows/land-id-build.yml` builds `.docker/Dockerfile-local-build`
on every push to `land-id` and pushes it to the shared `ory-hydra` ECR
repository, tagged with the short commit SHA. argo-cd's
`argo/<env>/ory-hydra-values.yml` pins that tag per environment.

## What we carry on top of upstream `master`

- **Dynamic client registration omits empty optional fields.** Hydra returned
  unset `client_uri`, `contacts`, etc. as `""`/`null`, which RFC 7591 clients
  like the MCP TypeScript SDK (Claude Code) reject. Ory fixed this in v26.3.10,
  an enterprise release whose fix isn't on open-source `master`.
- **Dependency bumps** for advisories `govulncheck ./...` reports as reachable,
  and the build pinned to a patched Go toolchain.
- This file and the Land id workflows.

Files we changed carry a "Modified by Land id" note under their license
header, as Apache 2.0 asks. Files that can't hold a comment (`go.sum` and the
test snapshots under `client/.snapshots/`) are covered by this list instead.

For PRs into `land-id`, `.github/workflows/land-id-modified-notice.yml` adds
the note to every modified file that lacks one and pushes it to the PR's
branch. Label a PR `skip-modified-notice` to skip it, as for PRs that merge
upstream. Its pushes don't trigger other workflows, so re-run checks after it
if you need them on the final commit.

## Pulling in upstream `master`

1. `git fetch upstream` and branch from `land-id`.
2. `git merge upstream/master`. Where our changes conflict with upstream's,
   keep upstream's and reapply ours on top. Drop the registration fix once
   upstream has its own.
3. Run `govulncheck ./...` and bump what it reports; run
   `go test -tags sqlite ./...`.
4. Check `git diff --name-status <old land-id> HEAD -- persistence/sql/migrations`
   for new migrations. The deploy's migration Job applies them before the new
   pods start, and rolling back the image doesn't undo them.
5. Open a PR into `land-id` labelled `skip-modified-notice` (otherwise every
   file upstream changed would be marked as ours).
