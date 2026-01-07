---
sidebar_position: 2
---

# ایک دستاویز بنائیں

دستاویزات **صفحات کے گروپس** ہیں جو اس کے ذریعے جڑے ہوئے ہیں:

- ایک **سائڈبار**
- **پچھلا/اگلا نیویگیشن**
- **ورژننگ**

## اپنی پہلی دستاویز بنائیں

`docs/hello.md` پر ایک مارک ڈاؤن فائل بنائیں:

```md title="docs/hello.md"
# ہیلو

یہ میری **پہلی Docusaurus دستاویز** ہے!
```

ایک نئی دستاویز اب [http://localhost:3000/docs/hello](http://localhost:3000/docs/hello) پر دستیاب ہے۔

## سائڈبار کو کنفیگر کریں

Docusaurus خود بخود `docs` فولڈر سے **ایک سائڈبار بناتا ہے**۔

سائڈبار لیبل اور پوزیشن کو اپنی مرضی کے مطابق بنانے کے لیے میٹا ڈیٹا شامل کریں:

```md title="docs/hello.md" {1-4}
---
sidebar_label: 'ہیلو!'
sidebar_position: 3
---

# ہیلو

یہ میری **پہلی Docusaurus دستاویز** ہے!
```

`sidebars.js` میں واضح طور پر اپنا سائڈبار بنانا بھی ممکن ہے:

```js title="sidebars.js"
export default {
  tutorialSidebar: [
    'intro',
    // highlight-next-line
    'hello',
    {
      type: 'category',
      label: 'ٹیوٹوریل',
      items: ['tutorial-basics/create-a-document'],
    },
  ],
};
```