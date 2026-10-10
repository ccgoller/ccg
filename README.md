# ccg

Quarto website scaffold for a personal page based on the MB360 `about.qmd` profile content.

## Local preview

If Quarto is installed:

```bash
quarto preview
```

## Publish to GitHub Pages

This repository includes a workflow at `.github/workflows/deploy-pages.yml` that renders the Quarto site and deploys `_site/` to GitHub Pages on pushes to the default branch.

In GitHub repository settings:

1. Go to **Settings → Pages**
2. Set **Source** to **GitHub Actions**

After the deployment workflow succeeds, the public site URL is:

- https://ccgoller.github.io/ccg/

## Verify the published site

After deploy, open the URL above and confirm:

- Home page loads
- About page link works (`/ccg/about.html`)

## Accessibility checks

After `quarto render`, check each page at 320px, tablet, and desktop widths.
Check keyboard-only navigation: the first Tab reaches “Skip to main content”,
Enter focuses the main landmark, and focus remains visible on navigation,
search, reader mode, and table controls. Verify the mobile menu, table sorting,
search, filters, and citation downloads. Also check enlarged text, reduced
motion, and screen-reader table headings and chart descriptions.

The post-render `fix-aria.py` hook fixes the navigation button role and moves
the skip link before navigation. Publication and mentoring tables load locally
vendored jQuery before DataTables; both scripts are required for full search
and pagination. Basic sorting and filters remain available if DataTables fails
to load, and bibliography downloads are offered when JavaScript is disabled.
These checks support accessibility improvements, not a certification of full
WCAG compliance.
