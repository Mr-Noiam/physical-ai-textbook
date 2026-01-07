---
sidebar_position: 2
---

# اپنی سائٹ کا ترجمہ کریں

آئیے `docs/intro.md` کا فرانسیسی میں ترجمہ کریں۔

## i18n کو کنفیگر کریں

`fr` لوکیل کے لیے سپورٹ شامل کرنے کے لیے `docusaurus.config.js` میں ترمیم کریں:

```js title="docusaurus.config.js"
export default {
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'fr'],
  },
};
```

## ایک دستاویز کا ترجمہ کریں

`docs/intro.md` فائل کو `i18n/fr` فولڈر میں کاپی کریں:

```bash
mkdir -p i18n/fr/docusaurus-plugin-content-docs/current/

cp docs/intro.md i18n/fr/docusaurus-plugin-content-docs/current/intro.md
```

`i18n/fr/docusaurus-plugin-content-docs/current/intro.md` کا فرانسیسی میں ترجمہ کریں۔

## اپنی مقامی سائٹ شروع کریں

اپنی سائٹ کو فرانسیسی لوکیل پر شروع کریں:

```bash
npm run start -- --locale fr
```

آپ کی مقامی سائٹ [http://localhost:3000/fr/](http://localhost:3000/fr/) پر قابل رسائی ہے اور `شروع کریں` صفحہ کا ترجمہ ہو چکا ہے۔

:::caution

ترقی میں، آپ ایک وقت میں صرف ایک لوکیل استعمال کر سکتے ہیں۔

:::

## ایک لوکیل ڈراپ ڈاؤن شامل کریں

زبانوں کے درمیان بغیر کسی رکاوٹ کے نیویگیٹ کرنے کے لیے، ایک لوکیل ڈراپ ڈاؤن شامل کریں۔

`docusaurus.config.js` فائل میں ترمیم کریں:

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

لوکیل ڈراپ ڈاؤن اب آپ کے نیوبار میں ظاہر ہوتا ہے:

## اپنی مقامی سائٹ بنائیں

اپنی سائٹ کو ایک مخصوص لوکیل کے لیے بنائیں:

```bash
npm run build -- --locale fr
```

یا اپنی سائٹ کو ایک ساتھ تمام لوکیلز کو شامل کرنے کے لیے بنائیں:

```bash
npm run build
```