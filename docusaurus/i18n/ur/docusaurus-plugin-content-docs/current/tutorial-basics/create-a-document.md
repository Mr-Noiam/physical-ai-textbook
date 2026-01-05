---
sidebar_position: 2
---

[TRANSLATION_FAILED] # Create a Document

[TRANSLATION_FAILED] Documents are **groups of pages** connected through:

[TRANSLATION_FAILED] - a **sidebar**
[TRANSLATION_FAILED] - **previous/next navigation**
[TRANSLATION_FAILED] - **versioning**

[TRANSLATION_FAILED] ## Create your first Doc

[TRANSLATION_FAILED] Create a Markdown file at `docs/hello.md`:

```md title="docs/hello.md"
# Hello

This is my **first Docusaurus document**!
```

[TRANSLATION_FAILED] A new document is now available at [http://localhost:3000/docs/hello](http://localhost:3000/docs/hello).

[TRANSLATION_FAILED] ## Configure the Sidebar

[TRANSLATION_FAILED] Docusaurus automatically **creates a sidebar** from the `docs` folder.

[TRANSLATION_FAILED] Add metadata to customize the sidebar label and position:

```md title="docs/hello.md" {1-4}
---
sidebar_label: 'Hi!'
sidebar_position: 3
---

# Hello

This is my **first Docusaurus document**!
```

[TRANSLATION_FAILED] It is also possible to create your sidebar explicitly in `sidebars.js`:

```js title="sidebars.js"
export default {
  tutorialSidebar: [
    'intro',
    // highlight-next-line
    'hello',
    {
      type: 'category',
      label: 'Tutorial',
      items: ['tutorial-basics/create-a-document'],
    },
  ],
};
```
