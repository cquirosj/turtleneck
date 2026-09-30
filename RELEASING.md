# Releasing

1. If skill text changed, run `./evals/regress.sh` and commit the new
   scorecard. No protocol change ships without one.
2. Move the Unreleased section of CHANGELOG.md under the new version with
   today's date. Include the regression mean when the skill changed.
3. Bump the version in all three manifests in one commit:
   `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `package.json`.
   Minor when skill text changes behavior, patch for docs and evals.
   Check they agree:

       python3 -c "import json; vs={f: json.load(open(f))['version'] for f in ['.claude-plugin/plugin.json','.codex-plugin/plugin.json','package.json']}; print(vs); assert len(set(vs.values()))==1"

4. Tag and push:

       git tag v<version> && git push origin main --tags

   CI fails the tag if the manifests disagree or the tag does not match.

The skills CLI and pi track main, so they see changes without a release.
Codex caches by version, so a Codex user only gets new skill text after a
version bump. Claude Code shows the version in the plugin list.
