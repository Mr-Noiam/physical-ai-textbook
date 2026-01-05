---
sidebar_position: 2
---

[TRANSLATION_FAILED] # Translate your site

[TRANSLATION_FAILED] Let's translate `docs/intro.md` to French.

[TRANSLATION_FAILED] ## Configure i18n

[TRANSLATION_FAILED] Modify `docusaurus.config.js` to add support for the `fr` locale:

```js title="docusaurus.config.js"
export default {
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'fr'],
  },
};
```

[TRANSLATION_FAILED] ## Translate a doc

[TRANSLATION_FAILED] Copy the `docs/intro.md` file to the `i18n/fr` folder:

```bash
mkdir -p i18n/fr/docusaurus-plugin-content-docs/current/

cp docs/intro.md i18n/fr/docusaurus-plugin-content-docs/current/intro.md
```

[TRANSLATION_FAILED] Translate `i18n/fr/docusaurus-plugin-content-docs/current/intro.md` in French.

[TRANSLATION_FAILED] ## Start your localized site

[TRANSLATION_FAILED] Start your site on the French locale:

```bash
npm run start -- --locale fr
```

[TRANSLATION_FAILED] Your localized site is accessible at [http://localhost:3000/fr/](http://localhost:3000/fr/) and the `Getting Started` page is translated.

[TRANSLATION_FAILED] :::caution

[TRANSLATION_FAILED] In development, you can only use one locale at a time.

[TRANSLATION_FAILED] :::

[TRANSLATION_FAILED] ## Add a Locale Dropdown

[TRANSLATION_FAILED] To navigate seamlessly across languages, add a locale dropdown.

[TRANSLATION_FAILED] Modify the `docusaurus.config.js` file:

```js title="docusaurus.config.js"
export default {
  themeConfig: {
    navbar: {
      items: [
        // highlight-start
        {
          type: 'localeDropdown',
        },
        // highlight-end
      ],
    },
  },
};
```

[TRANSLATION_FAILED] The locale dropdown now appears in your navbar:

[TRANSLATION_FAILED] ## Build your localized site

[TRANSLATION_FAILED] Build your site for a specific locale:

```bash
npm run build -- --locale fr
```

[TRANSLATION_FAILED] Or build your site to include all the locales at once:

```bash
npm run build
```
