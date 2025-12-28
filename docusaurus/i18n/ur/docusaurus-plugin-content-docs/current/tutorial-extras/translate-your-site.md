---
sidebar_position: 2
---

# اپنے سائٹ کا ترجمہ کریں

آئیں `docs/intro.md` کا فرانسیسی میں ترجمہ کریں۔

## i18n کی تشکیل کریں

`docusaurus.config.js` میں ترمیم کریں تاکہ `fr` لوکیل کی حمایت شامل کی جا سکے:

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

آپ کی مقامی سائٹ [http://localhost:3000/fr/](http://localhost:3000/fr/) پر دستیاب ہے اور `Getting Started` صفحہ ترجمہ شدہ ہے۔

:::caution

ترقی کے دوران، آپ ایک وقت میں صرف ایک لوکیل استعمال کر سکتے ہیں۔

:::

## لوکیل ڈراپ ڈاؤن شامل کریں

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

اب لوکیل ڈراپ ڈاؤن آپ کی نیویگیشن بار میں ظاہر ہوتا ہے:

![Locale Dropdown](./img/localeDropdown.png)

## اپنی مقامی سائٹ بنائیں

ایک مخصوص لوکیل کے لیے اپنی سائٹ بنائیں:

```bash
npm run build -- --locale fr
```

یا اپنی سائٹ کو ایک ساتھ تمام لوکیل شامل کرنے کے لیے بنائیں:

```bash
npm run build
```