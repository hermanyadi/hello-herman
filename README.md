# Nifty Watch — Daily Index Dashboard

A free, static dashboard that shows all ~98 NSE Nifty indices, refreshed once a day.
No server, no database, no paid hosting.

## How it works
- A GitHub Action runs once a day (weekday evenings, IST) and fetches NSE's `allIndices` API
- It saves the cleaned result to `data/latest.json` in this repo
- `index.html` is a static page that reads that file and shows a sortable, filterable table
- GitHub Pages hosts `index.html` for free

## Setup (no command line needed — everything below is done on github.com)

### 1. Create the repository
1. Go to https://github.com and sign in (create a free account if you don't have one)
2. Click the **+** icon top-right → **New repository**
3. Name it something like `nifty-watch` → set it to **Public** (required for free GitHub Pages) → **Create repository**

### 2. Upload these files
1. On your new repo's page, click **Add file → Upload files**
2. Drag in all the files from this project, **keeping the folder structure**:
   - `index.html`
   - `requirements.txt`
   - `scripts/fetch_indices.py`
   - `data/latest.json`
   - `.github/workflows/update-indices.yml`
   - (GitHub's upload box supports dragging whole folders — if it flattens them, upload the `scripts`, `data`, and `.github` folders one at a time so the paths stay correct)
3. Scroll down, click **Commit changes**

### 3. Turn on GitHub Pages
1. In your repo, go to **Settings → Pages** (left sidebar)
2. Under "Build and deployment" → Source: select **Deploy from a branch**
3. Branch: select **main** and folder **/(root)** → **Save**
4. Wait ~1 minute. Your dashboard will be live at:
   `https://<your-username>.github.io/nifty-watch/`

### 4. Run the data fetch for the first time
1. Go to the **Actions** tab in your repo
2. If prompted, click **"I understand my workflows, go ahead and enable them"**
3. Click **Update Nifty Indices Data** in the left list
4. Click **Run workflow** (dropdown button, top-right) → **Run workflow**
5. Wait ~30 seconds, refresh the Actions page — you should see a green checkmark
6. Refresh your dashboard URL — data should now appear

After this, it updates itself automatically every weekday evening (11:00 UTC / 4:30 PM IST) — you don't need to do anything.

### 5. Whenever you want fresh data on demand
Repeat step 4 (Actions tab → Update Nifty Indices Data → Run workflow), or just click the
**Refresh** button on the dashboard to re-pull whatever the latest committed data is (it
won't trigger a brand-new NSE fetch by itself — see note below).

## Notes & limits
- **The dashboard's "Refresh" button** only re-reads `data/latest.json` from the repo — it can't call NSE directly from your browser (NSE blocks cross-site browser requests) and can't safely trigger the GitHub Action itself (that would require exposing a private GitHub token on a public page). For genuinely new data, use the Actions tab.
- **Schedule timing**: GitHub's free scheduled Actions can run a few minutes late during high load times — this is normal and fine for a once-a-day refresh.
- **No login/auth**: this dashboard is fully public if hosted on GitHub Pages (repo must be public for the free tier). Don't put anything sensitive in it.
- **Cost**: $0. GitHub Pages and Actions are free for public repos at this usage level (one run/day, <50 visits/day is trivial).

## File structure
```
nifty-watch/
├── index.html                          # the dashboard itself
├── requirements.txt                    # Python deps for the Action
├── data/
│   └── latest.json                     # written by the Action, read by the dashboard
├── scripts/
│   └── fetch_indices.py                # fetches + cleans NSE data
└── .github/workflows/
    └── update-indices.yml              # the daily scheduled job
```
