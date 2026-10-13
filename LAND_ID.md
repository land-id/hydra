# Land id's Hydra fork

The `land-id` branch is the default branch of this fork and what we deploy. It
is an [Ory Hydra](https://github.com/ory/hydra) release tag plus a short list
of our own commits. Ory releases open-source Hydra about once a year, so we
carry fixes ourselves between releases.

`.github/workflows/land-id-build.yml` builds `.docker/Dockerfile-local-build`
on every push to `land-id` and pushes it to the shared `ory-hydra` ECR
repository, tagged with the short commit SHA. argo-cd's
`argo/<env>/ory-hydra-values.yml` pins that tag per environment.

## What we carry on top of v26.2.0

- **Dynamic client registration omits empty optional fields.** Hydra returned
  unset `client_uri`, `contacts`, etc. as `""`/`null`, which RFC 7591 clients
  like the MCP TypeScript SDK (Claude Code) reject. Ory fixed this in v26.3.10,
  which hasn't been released as open source.
- **Security fixes cherry-picked from upstream `master`** (`git log` shows each
  one's `cherry picked from commit` line): SSRF error info leaks, the OIDC
  session leak in the device authorization grant, and minor client validation
  hardening.
- **Dependency bumps** for advisories `govulncheck ./...` reports as reachable,
  and the build pinned to a patched Go toolchain.
- This file and the build workflow.

Not yet picked, because they conflict with refactors on `master`: the herodot
upgrade (`d1f2ef96`, error-handling info leaks) and the moby/moby switch that
drops `github.com/docker/docker` (`680b2ac6`, only reachable from test
helpers).

## Moving to a new upstream release

1. `git fetch upstream --tags` and branch from the new tag.
2. Cherry-pick our commits from `land-id` that the release doesn't already
   include (check upstream's changelog; drop the registration fix once a
   release contains it).
3. Run `govulncheck ./...` and `go test -tags sqlite ./...`.
4. Replace `land-id` with the new branch and update this file.

## Picking up a security fix between releases

Cherry-pick it with `git cherry-pick -x <sha>` onto `land-id`, run the tests for
the packages it touches with `-tags sqlite`, and push.
