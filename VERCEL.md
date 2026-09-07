# Vercel Git integration

## Existing resources

- Vercel team: `cfpperches-projects`
- Vercel project: `picode-companion-c02`
- GitHub repository: `cfpperche/picode-companion`
- Production branch: `main`
- Public URL: https://picode-companion-c02.vercel.app/

## Connection status

The repository `cfpperche/picode-companion` is connected to the existing Vercel project, confirmed by the owner's screenshot of **Connected Git Repository**. Git-triggered deployment is being checked with this documentation commit.

The connected Vercel API still returns 403 for the team's settings. That API limitation is separate from the Git connection shown in the dashboard.

## Configuration reference

1. Open [the existing project's Git settings](https://vercel.com/cfpperches-projects/picode-companion-c02/settings/git).
2. Under Connected Git Repository, connect GitHub and select `cfpperche/picode-companion`.
3. If the repository is not listed, grant the Vercel GitHub integration access to this repository.
4. Set the production branch to `main` in the project's production environment settings.
5. Keep framework **Other**, repository root as the root directory, output directory **public**, and no build command. The translated pages and runtime catalogs are committed.
6. Confirm the GitHub repository is shown as connected, then verify the next push or manual deployment from `main` reports the expected Git commit.

Future edits to translations require running `python3 scripts/build_locales.py` and committing the generated `public/` files alongside the catalogs. Once the native Git connection is enabled, pushes to the production branch can deploy through Vercel's Git integration.

Official documentation: [Vercel Git integration](https://vercel.com/docs/git), [Git settings](https://vercel.com/docs/project-configuration/git-settings).
