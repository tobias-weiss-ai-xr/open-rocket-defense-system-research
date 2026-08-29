
## Contrast auditing (WCAG AAA)

The site is held to WCAG AAA color contrast (7:1 normal text, 4.5:1 large/bold).
Two Playwright-based auditors verify every text-owning DOM node with proper
alpha compositing and CSS linear-gradient sampling:

```bash
# Single/multi viewport low-contrast scan (desktop default 1280x900)
python3 scripts/contrast_audit.py <url1> [<url2> ...]

# Multi-viewport scan (320x800, 768x1024, 1440x1000)
python3 scripts/contrast_audit_views.py <url1> [<url2> ...]
```

- CHROME path constant may need editing to your Playwright install.
- Chart.js canvas text is covered by `Chart.defaults.color` set to
  `#334155` (dashboard) / `#475569` (explainer) in the page JS, not by
  these DOM auditors.
- Known gotcha (hit us before): translucent `rgba()` fills and CSS
  gradients expose `transparent` to `getComputedStyle().backgroundColor` —
  the auditors composite alpha and sample gradient stops so results are real.
- A stray global `:nth-child(even) { background: transparent !important }`
  rule once wiped every even-positioned element's background (white-on-white
  in the audit). If you ever see mass 1:1 failures, check for leftover
  universal selectors like that first.
