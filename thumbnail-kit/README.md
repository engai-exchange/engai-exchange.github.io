# EngAI Xchange — YouTube thumbnail kit

Offline tool to make a **unique, branded 1280×720** YouTube thumbnail for each talk.  
Not part of the website (excluded from Jekyll).

## Quick start

1. Drop the speaker photo into `speakers/`  
   (clear headshot, square or portrait works best)

2. Edit `config.yaml`:

```yaml
image: speakers/example-aliyu.jpg
speaker: Aliyu Kasimu
institution: HKUST
title: "Your talk title here"
date: "Jul 28, 2025"
badge: Talk
```

3. Generate:

```powershell
cd thumbnail-kit
pip install -r requirements.txt
python generate.py
```

4. Open the PNG in `output/` and upload to YouTube.

## One-off without editing config

```powershell
python generate.py `
  --image speakers/franklin.jpg `
  --speaker "Franklin Eze" `
  --institution "Central South University" `
  --title "Aerodynamics of High-Speed Vehicles" `
  --date "Aug 4, 2025" `
  --badge Talk
```

## Layout (what you get)

| Region | Content |
|--------|---------|
| Left | EngAI brand, badge, date, speaker name, institution, title |
| Right | Speaker photo in rose-framed card |
| Base | Ink background + soft grid + rose glow (matches site identity) |

## Tips

- Prefer a **well-lit face** photo; the generator center-crops to fill the frame.
- Keep titles under **~90 characters** so they stay readable at small sizes.
- Use `badge: LIVE` for livestreams, or `Journal Club` for paper sessions.
- Re-run anytime — files in `output/` are safe to overwrite or delete.

## Files

```
thumbnail-kit/
  config.yaml       ← edit each week
  generate.py       ← generator
  speakers/         ← drop photos here
  output/           ← generated thumbnails
  assets/           ← logo files (already included)
```
