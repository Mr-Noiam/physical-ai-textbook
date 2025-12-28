---
sidebar_position: 2
---

# ایک دستاویز بنائیں

دستاویزات **صفحات کے گروپ** ہیں جو مندرجہ ذیل کے ذریعے جڑے ہوئے ہیں:

- ایک **سائیڈبار**
- **پچھلا/اگلا نیویگیشن**
- **ورژننگ**

## اپنا پہلا دستاویز بنائیں

`docs/hello.md` میں ایک Markdown فائل بنائیں:

```md title="docs/hello.md"
# السلام علیکم

یہ میرا **پہلا Docusaurus دستاویز** ہے!
```

اب ایک نئی دستاویز [http://localhost:3000/docs/hello](http://localhost:3000/docs/hello) پر دستیاب ہے۔

## سائیڈبار کی تشکیل کریں

Docusaurus خود بخود `docs` فولڈر سے **سائیڈبار** بناتا ہے۔

سائیڈبار کے لیبل اور مقام کو اپنی مرضی کے مطابق بنانے کے لیے میٹا ڈیٹا شامل کریں:

```md title="docs/hello.md" {1-4}
---
sidebar_label: 'ہیلو!'
sidebar_position: 3
---

# السلام علیکم

یہ میرا **پہلا Docusaurus دستاویز** ہے!
```

یہ ممکن ہے کہ آپ اپنے سائیڈبار کو `sidebars.js` میں واضح طور پر بھی بنائیں:

```js title="sidebars.js"
export default {
  tutorialSidebar: [
    'intro',
    // highlight-next-line
    'hello',
    {
      type: 'category',
      label: 'نصاب',
      items: ['tutorial-basics/create-a-document'],
    },
  ],
};
```