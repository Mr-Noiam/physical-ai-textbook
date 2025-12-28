---
sidebar_position: 1
---

# دستاویزات کے ورژن کا انتظام کریں

Docusaurus آپ کی دستاویزات کے متعدد ورژنز کا انتظام کر سکتا ہے۔

## دستاویزات کا ورژن بنائیں

اپنے پروجیکٹ کا ورژن 1.0 جاری کریں:

```bash
npm run docusaurus docs:version 1.0
```

`docs` فولڈر کو `versioned_docs/version-1.0` میں کاپی کیا جاتا ہے اور `versions.json` بنایا جاتا ہے۔

آپ کی دستاویزات اب 2 ورژنز میں ہیں:

- `1.0` پر `http://localhost:3000/docs/` ورژن 1.0 کی دستاویزات کے لیے
- `current` پر `http://localhost:3000/docs/next/` **آنے والی، غیر جاری شدہ دستاویزات** کے لیے

## ورژن ڈراپ ڈاؤن شامل کریں

ورژنز کے درمیان ہموار نیویگیشن کے لیے، ایک ورژن ڈراپ ڈاؤن شامل کریں۔

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

دستاویزات کا ورژن ڈراپ ڈاؤن آپ کی نیوی بار میں ظاہر ہوتا ہے:

![Docs Version Dropdown](./img/docsVersionDropdown.png)

## موجودہ ورژن کو اپ ڈیٹ کریں

اپنے متعلقہ فولڈر میں ورژنڈ دستاویزات میں ترمیم کرنا ممکن ہے:

- `versioned_docs/version-1.0/hello.md` `http://localhost:3000/docs/hello` کو اپ ڈیٹ کرتا ہے
- `docs/hello.md` `http://localhost:3000/docs/next/hello` کو اپ ڈیٹ کرتا ہے