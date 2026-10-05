# React + Vite Scaffold Test

This proves the real npm install -> npm run dev -> real page render chain
works, before any AI model generation gets layered on top.

## How to test on your machine

```bash
cd react_scaffold_test
npm install
npm run dev
```

Then open http://localhost:5173/ in your browser.

You should see:
- "AZIZ AI - React scaffold works"
- A working button that increments a counter on click (real React state)

If you see that, the whole toolchain (Node, npm, Vite, React) is working
correctly on your machine, and we're ready to wire the AI model in to
generate real components instead of this hardcoded one.
