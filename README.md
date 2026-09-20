<p align="center">
  <img src="https://raw.githubusercontent.com/anti-ltd/clink-language-packs/main/icon-1024.png" width="96" alt="Clink app icon">
</p>

<h1 align="center">Clink NuPhy themes</h1>

<p align="center">NuPhy inspired keyboard themes for Clink.</p>

Themes inspired by [NuPhy](https://nuphy.com/) keyboards, with their colours, keycap shapes, and accents adapted for Clink. Each theme's description identifies it as NuPhy inspired. The info button shows the original keyboard beside its Clink theme and links to NuPhy's website.

## Official Clink repositories

[Language packs](https://github.com/anti-ltd/clink-language-packs) · [Layouts](https://github.com/anti-ltd/clink-layouts) · [Profiles](https://github.com/anti-ltd/clink-profiles) · [Themes](https://github.com/anti-ltd/clink-themes) · [NuPhy themes](https://github.com/anti-ltd/clink-themes-nuphy) · [Panels](https://github.com/anti-ltd/clink-panels) · [Actions](https://github.com/anti-ltd/clink-actions) · [Fonts](https://github.com/anti-ltd/clink-fonts) · [Sounds](https://github.com/anti-ltd/clink-sounds)

## Included themes

The collection includes 17 themes inspired by these NuPhy keyboards:

- **Halo75 V2**, in Ionic White, Obsidian Black, Mojito, and Blue Lagoon.
- **Air75**, including V3 Nova White, V3 Nebula Dark, and HE.
- **Field75**, including Electro, Noether, and the first-generation HE.
- **Node**, including Node75 Lunar White and Ink Gray, and Node100 Light Pink.
- **Gem80**, in Cosmic Mocha and Mystic Indigo with matching keycaps.
- **Kick75**, with its low-profile stock keycaps.
- **NuPhyX BH65**, with mint legends and violet accents.

The complete collection is published under [`Themes/`](Themes). The generated [`manifest.json`](manifest.json) describes every release asset. [`Images/`](Images) holds the comparison photos and Clink previews; [`comparisons.json`](comparisons.json) records the model names, descriptions, and photo sources.

## Make your first theme

You do not need to build Clink or write a manifest.

1. Fork this repository.
2. In Clink, make a theme and choose **Export** from the theme menu. This gives you a `.clinktheme` file.
3. Put the file in [`Themes/`](Themes), for example `Themes/nuphy-my-theme.clinktheme`.
4. Open the file in a text editor. Give it a permanent lowercase `id` and a clear visible `name` beginning with `NuPhy`.
5. Do not include `backgroundImageID` or `keyImageID`. Theme documents contain colours, gradients, and materials; comparison images live separately.
6. Add a matching entry in [`comparisons.json`](comparisons.json), with a description beginning `NuPhy inspired`, the keyboard model, image filenames, and photo sources. Put the product photo and matching Clink preview in [`Images/`](Images).
7. Run these commands:

   ```sh
   python3 tools/build-manifest.py
   python3 -m unittest discover -s tests
   ```

   The tests also check that the curated collection contains all 17 themes. Update that count when adding a new theme.

8. Push to `main`. GitHub Actions publishes the themes, images, and manifest to the `latest` release.

## Add your repository to Clink

This repository appears automatically under **Customize → Look → Nuphy** in builds that include the NuPhy catalog. Its first GitHub release must be published before themes can be downloaded.

For a fork, open **General → Repositories** in Clink and add `owner/repository`, for example:

```text
your-name/clink-themes-nuphy
```

Then open **Customize → Look**, choose your repository's chip, and download a theme. Downloaded themes remain available offline. They stay read-only, but anyone can make an editable copy.

Comparison images load from the repository's GitHub release when the info sheet opens. They are not bundled in the app or installed into the keyboard extension.

## What Clink verifies

Clink accepts only public HTTPS GitHub release manifests. Each theme must come from that repository's release, be a `.clinktheme` JSON file no larger than 128 KB, and match the SHA-256 hash and byte count in the manifest.

Clink downloads each file into a temporary directory, verifies its checksum and safe data-only structure, and only then installs it. Theme documents cannot contain photos or executable code. Comparison image URLs must point to the same release as their theme.

Adding a repository is a trust decision. Only add repositories whose release contents you trust.

## Publishing is automatic

Keep `Themes/`, `Images/`, `comparisons.json`, `tools/`, `tests/`, and `.github/workflows/` in your fork. Add or update a theme and its matching preview, regenerate the manifest, and push to `main`. GitHub Actions validates the files and refreshes the `latest` release so Clink can download them.

Release tags include the theme files, comparison images, and metadata. Changing any of these creates a new release, keeping older cached manifests linked to their matching files.

NuPhy names and product photographs belong to their respective owners. Photo sources are recorded in [`comparisons.json`](comparisons.json).
