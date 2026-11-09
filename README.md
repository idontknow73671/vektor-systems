# Vektor Systems

A responsive informational site for Vektor Systems. The project uses plain HTML, CSS, JavaScript, and Python's standard library.

## Edit the site

- Edit the copy, section order, navigation, and prices in `index.html`. Both pricing tables are in the Pricing section.
- Edit colors, typography, spacing, and layout in `style.css`. Theme variables are at the top.
- Replace `assets/logo.png` to update the emblem.
- Edit `script.js` to change the navigation behavior.

Use `index.html` for everyday editing. The generated `dist/index.svg` is rebuilt from the source files.

## Build and preview

Run this command from the project directory with Python 3.9 or newer.

```sh
python convert.py
```

Open `index.html` for the original site or `dist/index.svg` directly in a browser. To preview over HTTP, run `python -m http.server 8000` in the project directory and open either path at `http://localhost:8000`.

Keep HTML nesting explicit so the converter can produce valid XML. Place scripts in `script.js`, stylesheet rules in `style.css`, and assets in the project folder. The converter embeds local `src` and `poster` assets and local CSS `url(...)` references. It reports errors for unsupported constructs such as `srcset`, embedded frames, and CSS imports.

## Distribution

Open the SVG as a top-level browser document. SVG image contexts such as an HTML `<img>` can suppress script execution and interaction. Browser SVG support can also vary in viewers and other image tools.

For jsDelivr, commit `dist/index.svg` to a public GitHub repository and use this URL pattern with your commit SHA.

```text
https://cdn.jsdelivr.net/gh/OWNER/REPO@COMMIT/dist/index.svg
```

The SVG contains its styles, script, and logo. It needs no adjacent files at runtime. Use a new commit URL after rebuilding and publishing an update.
