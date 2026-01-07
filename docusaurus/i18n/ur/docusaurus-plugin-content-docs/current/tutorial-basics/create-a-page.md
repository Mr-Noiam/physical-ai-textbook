---
sidebar_position: 1
---

# ایک صفحہ بنائیں

ایک **اسٹینڈ لون صفحہ** بنانے کے لیے `src/pages` میں **مارک ڈاؤن یا ری ایکٹ** فائلیں شامل کریں:

- `src/pages/index.js` → `localhost:3000/`
- `src/pages/foo.md` → `localhost:3000/foo`
- `src/pages/foo/bar.js` → `localhost:3000/foo/bar`

## اپنا پہلا ری ایکٹ صفحہ بنائیں

`src/pages/my-react-page.js` پر ایک فائل بنائیں:

```jsx title="src/pages/my-react-page.js"
import React from 'react';
import Layout from '@theme/Layout';

export default function MyReactPage() {
  return (
    <Layout>
      <h1>میرا ری ایکٹ صفحہ</h1>
      <p>یہ ایک ری ایکٹ صفحہ ہے</p>
    </Layout>
  );
}
```

ایک نیا صفحہ اب [http://localhost:3000/my-react-page](http://localhost:3000/my-react-page) پر دستیاب ہے۔

## اپنا پہلا مارک ڈاؤن صفحہ بنائیں

`src/pages/my-markdown-page.md` پر ایک فائل بنائیں:

```mdx title="src/pages/my-markdown-page.md"
# میرا مارک ڈاؤن صفحہ

یہ ایک مارک ڈاؤن صفحہ ہے
```

ایک نیا صفحہ اب [http://localhost:3000/my-markdown-page](http://localhost:3000/my-markdown-page) پر دستیاب ہے۔