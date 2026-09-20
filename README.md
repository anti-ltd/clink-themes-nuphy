# NuPhy Inspired themes for Clink

17 Clink themes inspired by NuPhy keyboards, with product photographs and Clink keyboard previews for comparison. Each theme is explicitly named **NuPhy Inspired**. Visit [NuPhy](https://nuphy.com/).

## Contents

- `Themes/`: downloadable `.clinktheme` JSON documents.
- `Images/`: product photos and matching Clink keyboard captures.
- `comparisons.json`: model names, image filenames, and original photo attribution links.
- `manifest.json`: generated app catalog, including the NuPhy website link and comparison image URLs.

Clink includes this repository as a built-in catalog source. The app downloads the manifest and verifies theme JSON before installation. The info sheet loads comparison artwork on demand from GitHub release assets. No comparison images are bundled in the app or installed into its keyboard extension.

## Publish

Create `anti-ltd/clink-themes-nuphy` on GitHub and push this local repository's `main` branch. The included GitHub Actions workflow validates the contents and publishes a release. The app looks for `releases/latest/download/manifest.json`; it can show the catalog after that first release exists.

```sh
python3 -m unittest discover -s tests
python3 tools/build-manifest.py
```

Release tags incorporate theme files, images, and metadata. Updating any of these creates a new immutable release, so older cached manifests continue to resolve to their matching artwork and theme files.

## Edit a theme

Update its JSON in `Themes/`, keep its `id` stable and its name prefixed with `NuPhy Inspired`, then replace the matching capture in `Images/`. Update `comparisons.json` when the reference model or image attribution changes. Theme definitions were exported from Clink's reviewed debug presets on 20 September 2026.

NuPhy names and product photographs belong to their respective owners. This repository does not grant a license to those assets or describe the themes as official NuPhy products.

To refresh these initial exports from the app, run the `NuPhyThemeReviewTests` suite, export its attachments with `xcrun xcresulttool export attachments`, then run `python3 tools/import-clink-exports.py <attachments-directory>`. The export test checks that theme JSON survives decoding without changing its serialized values.

After committing and publishing this standalone repository, register it in the parent `clink-index` checkout with `git submodule add git@github.com:anti-ltd/clink-themes-nuphy.git clink-themes-nuphy`. Git can reuse this existing local checkout once it has its first commit.
