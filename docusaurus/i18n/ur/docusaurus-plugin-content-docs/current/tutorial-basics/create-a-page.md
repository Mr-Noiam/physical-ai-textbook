---
sidebar_position: 1
---

[TRANSLATION_FAILED] # Create a Page

[TRANSLATION_FAILED] Add **Markdown or React** files to `src/pages` to create a **standalone page**:

[TRANSLATION_FAILED] - `src/pages/index.js` → `localhost:3000/`
[TRANSLATION_FAILED] - `src/pages/foo.md` → `localhost:3000/foo`
[TRANSLATION_FAILED] - `src/pages/foo/bar.js` → `localhost:3000/foo/bar`

[TRANSLATION_FAILED] ## Create your first React Page

[TRANSLATION_FAILED] Create a file at `src/pages/my-react-page.js`:

```jsx title="src/pages/my-react-page.js"
import React from 'react';
import Layout from '@theme/Layout';

export default function MyReactPage() {
  return (
    <Layout>
      <h1>My React page</h1>
      <p>This is a React page</p>
    </Layout>
  );
}
```

[TRANSLATION_FAILED] A new page is now available at [http://localhost:3000/my-react-page](http://localhost:3000/my-react-page).

[TRANSLATION_FAILED] ## Create your first Markdown Page

[TRANSLATION_FAILED] Create a file at `src/pages/my-markdown-page.md`:

```mdx title="src/pages/my-markdown-page.md"
# My Markdown page

This is a Markdown page
```

[TRANSLATION_FAILED] A new page is now available at [http://localhost:3000/my-markdown-page](http://localhost:3000/my-markdown-page).
