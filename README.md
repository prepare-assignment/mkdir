# mkdir

Make a directory.

## Example

```yml
- name: Create image dir
  uses: mkdir
  with:
    directory: out/images
    parents: true
```

## Options

The following options are available:

```yaml
directory:
  description: The directory to create
  type: string
  required: true
parents:
  description: Make parent directories if needed
  required: false
  type: boolean
  default: false
allow-outside-working-directory:
  description: The directory can be outside the working directory
  required: false
  type: boolean
  default: false
```

The directory is created relative to the working directory. A directory outside it (e.g. `../out`, or an absolute path elsewhere) fails, unless `allow-outside-working-directory` is set.

## Releases

Releases are automated with [semantic-release](https://semantic-release.gitbook.io/). Pull requests are squash merged, so the PR title becomes the commit on `main` and must follow [Conventional Commits](https://www.conventionalcommits.org/) (checked on every PR):

| PR title | Release |
|----------|---------|
| `fix: ...`, `perf: ...` | patch (1.2.3 → 1.2.4) |
| `feat: ...` | minor (1.2.3 → 1.3.0) |
| `!` after the type (e.g. `feat!: ...`, `refactor!: ...`) or a `BREAKING CHANGE:` footer | major (1.2.3 → 2.0.0) |
| `docs:`, `chore:`, `ci:`, `build:`, `refactor:`, `test:`, `style:`, `revert:` | no release |

On every merge to `main` the next version is determined, tagged (`vX.Y.Z`) and a GitHub release is created. The major tag (e.g. `v1`) is moved to the new release, so `uses: mkdir@v1` always gets the newest 1.x version.

Because the major tag moves, `git pull` in an existing clone can fail with `! [rejected] v1 -> v1 (would clobber existing tag)`. Update the tags once with `git fetch --tags --force` and pull again.
