# Validation — 20 September 2026

- iOS Debug build and focused simulator tests passed: catalog loading, source classification, optional comparison metadata validation, and all 17 exported theme documents.
- Each exported theme survives JSON decoding and re-encoding without changing its serialized values.
- The existing app-hosted keyboard captures were reused. The new hostless export run intentionally skipped the visual capture test.
- Four Python repository tests passed: manifest/asset consistency, immutable versions for artwork and metadata changes, ignored macOS sidecars, and missing-image rejection.
- Built app inspected: zero NuPhy comparison PNG/JPG files embedded.
- Every manifest entry links to https://nuphy.com/ and is named NuPhy Inspired.
- The app's localization coverage check remains blocked by 19 existing missing strings unrelated to this integration. The new NuPhy Inspired label has translations for all 13 supported UI languages; native-speaker review remains part of release review.

The GitHub repository and first release have not been published. Hosted image loading and the live catalog need a final check after publication.
