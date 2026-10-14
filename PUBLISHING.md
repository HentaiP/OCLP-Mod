# Publish as an actual OCLP-Mod GitHub fork

1. Connect the intended GitHub account in OpenClaw Agent Settings → Tools,
   or authenticate your own Git client. No credential is stored in this package.
2. Use GitHub's **Fork** button on https://github.com/laobamac/OCLP-Mod to create
   an actual fork under your account. A newly created unrelated repository is
   not equivalent under the retained donor terms.
3. Clone that fork. Inspect its `main`: the prepared parent is
   `63555b94610c74703a000058ac6876f65b92e638`. Do not overwrite existing work.
4. Import the supplied `OCLP-Mod-Intel-Tahoe-fork-update.bundle`:

```sh
git bundle verify /path/to/OCLP-Mod-Intel-Tahoe-fork-update.bundle
git fetch /path/to/OCLP-Mod-Intel-Tahoe-fork-update.bundle intel-tahoe:review/intel-tahoe
git switch review/intel-tahoe
git diff --stat origin/main...HEAD
```

5. The new integration commit uses a neutral source-export author and no private
   commit history. If desired, set your **repository-local** public/noreply Git
   identity and amend that one unpushed integration commit with `--reset-author`.
   Do not rewrite the inherited upstream history.
6. Push only the reviewed integration branch to your fork:

```sh
git push origin HEAD:intel-tahoe
```

7. Choose `intel-tahoe` as the fork's default branch in GitHub settings if that
   is the intended landing page. Do not tag an official OCLP 3.0.0 release,
   claim hardware certification or attach the existing private App/Pkg.

The bundle requires the original Mod parent already present in the clone.
The source ZIP is an equivalent clean snapshot without Git metadata, not a
substitute for creating GitHub's fork relationship. Source archive hashes are
in the publication kit's `SHA256SUMS`.
