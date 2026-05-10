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
