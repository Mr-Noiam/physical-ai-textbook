---
sidebar_position: 1
---

# صفحہ بنائیں

**Markdown یا React** فائلیں `src/pages` میں شامل کریں تاکہ ایک **خود مختار صفحہ** بنایا جا سکے:

- `src/pages/index.js` → `localhost:3000/`
- `src/pages/foo.md` → `localhost:3000/foo`
- `src/pages/foo/bar.js` → `localhost:3000/foo/bar`

## اپنا پہلا React صفحہ بنائیں

`src/pages/my-react-page.js` پر ایک فائل بنائیں:

```jsx title="src/pages/my-react-page.js"
import React from 'react';
import Layout from '@theme/Layout';

export default function MyReactPage() {
  return (
    <Layout>
      <h1>میرا React صفحہ</h1>
      <p>یہ ایک React صفحہ ہے</p>
    </Layout>
  );
}
```

اب ایک نیا صفحہ [http://localhost:3000/my-react-page](http://localhost:3000/my-react-page) پر دستیاب ہے۔

## اپنا پہلا Markdown صفحہ بنائیں

`src/pages/my-markdown-page.md` پر ایک فائل بنائیں:

```mdx title="src/pages/my-markdown-page.md"
# میرا Markdown صفحہ

یہ ایک Markdown صفحہ ہے
```

اب ایک نیا صفحہ [http://localhost:3000/my-markdown-page](http://localhost:3000/my-markdown-page) پر دستیاب ہے۔