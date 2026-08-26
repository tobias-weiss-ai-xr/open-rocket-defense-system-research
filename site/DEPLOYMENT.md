# Deployment Guide - AI Defense Analysis Dashboard

## Quick Deploy to GitHub Pages

### Method 1: Deploy from `site/` directory (Recommended)

1. **GitHub Pages settings**:
   ```
   Settings → Pages → Source: GitHub Actions
   Or: Settings → Pages → Source: main branch → /site folder
   ```
   
2. **Create GitHub Actions workflow** (if using Actions):
   ```yaml
   # .github/workflows/deploy.yml
   name: Deploy to GitHub Pages
   
   permissions:
     contents: write
     pages: write
     id-token: write
   
   on:
     push:
       branches: [main]
   
   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         
         - name: Setup Pages
           uses: actions/configure-pages@v3
         
         - name: Copy site files
           run: |
             mkdir -p _site
             cp -r site/* _site/
         
         - name: Upload artifact
           uses: actions/upload-pages-artifact@v2
           with:
             path: '_site'
         
         - name: Deploy to GitHub Pages
           id: deployment
           uses: actions/deploy-pages@v2
   ```

3. **URL**: `https://<username>.github.io/open-rocket-defense-system-research/`

### Method 2: Deploy from root (Simpler)

1. Move site files to repository root:
   ```bash
   git mv site/* .
   git mv site/data/ .
   git mv site/README.md README-SITE.md
   git mv site/DEPLOYMENT.md DEPLOYMENT-SITE.md
   git commit -m "Prepare site for GitHub Pages"
   git push
   ```

2. In GitHub Pages settings:
   - Source: `main` branch, `/ (root)`

3. **URL**: `https://<username>.github.io/open-rocket-defense-system-research/`

### Method 3: Use docs/ directory

1. Clear existing docs:
   ```bash
   git rm -r docs/*.md  # Remove old docs if needed
   ```

2. Move site to docs:
   ```bash
   mv site/* docs/
   mv site/data/ docs/
   git add docs/
   git commit -m "Move site to docs for GitHub Pages"
   git push
   ```

3. In GitHub Pages settings:
   - Source: `main` branch, `/docs` folder

## Local Development

### Preview locally

```bash
cd site
python3 -m http.server 8000
# Open http://localhost:8000
```

### With auto-refresh (requires node.js)

```bash
npx serve site --port 8000
```

### With Docker

```bash
# Start a simple web server
docker run -it --rm -p 8000:80 -v $(pwd)/site:/usr/local/apache2/htdocs/ httpd:2.4
# Open http://localhost:8000
```

## Updating the Dashboard

### Update simulation data

```bash
# 1. Run new simulations
python3 scripts/monte_carlo_defense_analysis.py

# 2. Copy results to site/data /
site/data/ directory:
cp research/monte_carlo_analysis.json site/data/
cp research/monte_carlo_results.csv site/data/

# 3. Commit
cd site
git add data/
git commit -m "Update simulation data"
git push
```

### Update dashboard code

Edit `site/index.html` and test locally before pushing.

## Custom Domain (Optional)

1. In GitHub Pages settings, add your domain under **Custom domain**

2. Configure DNS:
   - CNAME: `your-domain.com` → `<username>.github.io`
   - Or A records: `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`

3. After DNS propagates (~1 hour to 48 hours):
   - In Pages settings, check **Enforce HTTPS**

## Deployment Checklist

- [ ] GitHub Pages enabled in repository settings
- [ ] Data files copied to `site/data/`
- [ ] Charts load correctly (check console for errors)
- [ ] Mobile responsive (test on phone)
- [ ] All recommendatons display
- [ ] Critical finding visible at top
- [ ] Methodology section complete
- [ ] Links work (GitHub repo, etc.)

## Troubleshooting

### Data not loading

**Symptom**: Loading spinner spins forever, no charts appear

**Fix**:
1. Verify `site/data/monte_carlo_analysis.json` exists
2. Check browser console (F12) for errors
3. Ensure file paths are correct in `index.html`
4. Try refreshing the page

### Charts not rendering

**Symptom**: Blank chart containers

**Fix**:
1. Check browser console for Chart.js errors
2. Verify Chart.js CDN is accessible
3. Ensure data is valid (check `analysisData.summary` exists)

### White screen / errors

**Symptom**: Page doesn't load, console shows errors

**Fix**:
1. Check your internet connection
2. Verify all files are in the correct location
3. Test with local server: `python3 -m http.server 8000`
4. Check for JavaScript syntax errors in console

### 404 errors

**Symptom**: Page loads but assets (CSS, images) show 404

**Fix**:
1. Verify all file paths in HTML are relative (e.g., `data/file.json` not `/data/file.json`)
2. Ensure files are in the correct subdirectories
3. Check GitHub Pages settings for correct source directory

### SSL warnings

**Symptom**: Browser shows "Not Secure" warning

**Fix**:
1. Ensure HTTPS is enforced in GitHub Pages settings
2. Check that custom domain DNS is properly configured
3. Wait for SSL certificate to provision (can take hours)

## Advanced Configuration

### Custom 404 page

Create `site/404.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Page Not Found</title>
</head>
<body>
    <h1>404 - Page Not Found</h1>
    <p>The page you're looking for doesn't exist.</p>
    <p><a href="/">Return to home page</a></p>
    <p><a href="https://github.com/tobias-weiss-ai-xr/open-rocket-defense-system-research">View on GitHub</a></p>
</body>
</html>
```

### Password protection (via Cloudflare)

Cannot be done with GitHub Pages alone (it's a static host). Options:
- Use Cloudflare Access in front of GitHub Pages
- Deploy to Netlify/Vercel with password protection
- Create a separate private site

### Search functionality

Add Google Custom Search or use a service like Algolia:

1. Create search form in HTML
2. Use site:your-domain.com query on Google
3. Or integrate with a search API

## Performance Optimization

The site is already optimized, but you can improve it further:

### Preload critical resources

Add to `<head>`:
```html
<link rel="preload" href="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js" as="script">
<link rel="preload" href="data/monte_carlo_analysis.json" as="fetch" crossorigin="anonymous">
```

### Use specific Chart.js version

Current: Uses pinned version `4.4.0` ✅

### Sample CSV data (for large files)

If `monte_carlo_results.csv` becomes too large (>1MB), consider:
- Pre-filtering to 1000-5000 points
- Using JSON instead of CSV
- Loading data progressively

## Verifying Deployment

After deploying:

1. **Check the URL**: Visit your GitHub Pages URL
2. **Test all features**: 
   - Charts load
   - Data is current
   - Links work
   - Mobile layout works
3. **Check accessibility**:
   - Use Chrome DevTools Accessibility tab
   - Test with screen reader
   - Verify keyboard navigation
4. **Check performance**:
   - Use Google Lighthouse
   - First load should be < 2 seconds
   -Repeat load should be < 1 second

## Rollback

If something goes wrong:

```bash
# Find the last good commit
git log --oneline

# Revert to that commit
git revert <commit-hash>
git push

# Or hard reset (if you can't fix Forward)
git reset --hard <commit-hash>
git push --force  # BE CAREFUL with force push
```

---

**Need help?** Check the GitHub repository for the latest deployment guides and troubleshooting tips.
