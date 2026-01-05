---
sidebar_position: 1
---

[TRANSLATION_FAILED] # Manage Docs Versions

[TRANSLATION_FAILED] Docusaurus can manage multiple versions of your docs.

[TRANSLATION_FAILED] ## Create a docs version

[TRANSLATION_FAILED] Release a version 1.0 of your project:

```bash
npm run docusaurus docs:version 1.0
```

[TRANSLATION_FAILED] The `docs` folder is copied into `versioned_docs/version-1.0` and `versions.json` is created.

[TRANSLATION_FAILED] Your docs now have 2 versions:

[TRANSLATION_FAILED] - `1.0` at `http://localhost:3000/docs/` for the version 1.0 docs
[TRANSLATION_FAILED] - `current` at `http://localhost:3000/docs/next/` for the **upcoming, unreleased docs**

[TRANSLATION_FAILED] ## Add a Version Dropdown

[TRANSLATION_FAILED] To navigate seamlessly across versions, add a version dropdown.

[TRANSLATION_FAILED] Modify the `docusaurus.config.js` file:

```js title="docusaurus.config.js"
export default {
  themeConfig: {
    navbar: {
      items: [
        // highlight-start
        {
          type: 'docsVersionDropdown',
        },
        // highlight-end
      ],
    },
  },
};
```

[TRANSLATION_FAILED] The docs version dropdown appears in your navbar.

[TRANSLATION_FAILED] ## Update an existing version

[TRANSLATION_FAILED] It is possible to edit versioned docs in their respective folder:

[TRANSLATION_FAILED] - `versioned_docs/version-1.0/hello.md` updates `http://localhost:3000/docs/hello`
[TRANSLATION_FAILED] - `docs/hello.md` updates `http://localhost:3000/docs/next/hello`
