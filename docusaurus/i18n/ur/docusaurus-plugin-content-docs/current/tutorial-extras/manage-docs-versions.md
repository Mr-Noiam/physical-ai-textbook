---
sidebar_position: 1
---

# دستاویزات کے ورژنز کا نظم کریں

Docusaurus آپ کی دستاویزات کے متعدد ورژنز کا نظم کر سکتا ہے۔

## ایک دستاویز ورژن بنائیں

اپنے پروجیکٹ کا ورژن 1.0 جاری کریں:

```bash
npm run docusaurus docs:version 1.0
```

`docs` فولڈر کو `versioned_docs/version-1.0` میں کاپی کیا جاتا ہے اور `versions.json` بنائی جاتی ہے۔

اب آپ کی دستاویزات کے 2 ورژن ہیں:

- `1.0` `http://localhost:3000/docs/` پر ورژن 1.0 دستاویزات کے لیے
- `current` `http://localhost:3000/docs/next/` پر **آنے والی، غیر جاری شدہ دستاویزات** کے لیے

## ایک ورژن ڈراپ ڈاؤن شامل کریں

ورژنز کے درمیان بغیر کسی رکاوٹ کے نیویگیٹ کرنے کے لیے، ایک ورژن ڈراپ ڈاؤن شامل کریں۔

`docusaurus.config.js` فائل میں ترمیم کریں:

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

دستاویزات کا ورژن ڈراپ ڈاؤن آپ کے نیوبار میں ظاہر ہوتا ہے۔

## ایک موجودہ ورژن کو اپ ڈیٹ کریں

ورژن شدہ دستاویزات کو ان کے متعلقہ فولڈر میں ترمیم کرنا ممکن ہے:

- `versioned_docs/version-1.0/hello.md` `http://localhost:3000/docs/hello` کو اپ ڈیٹ کرتا ہے
- `docs/hello.md` `http://localhost:3000/docs/next/hello` کو اپ ڈیٹ کرتا ہے