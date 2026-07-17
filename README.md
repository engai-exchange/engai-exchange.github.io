# EngAI Xchange Website

Website for the **EngAI Group Exchange Sessions** — a weekly forum for engineering research exchanges, including AI applications.

- **Live site:** [engai-exchange.github.io](https://engai-exchange.github.io)
- **Theme:** [Just the Docs](https://github.com/pmarsceill/just-the-docs) (Jekyll)
- **Adapted from:** [Stanford MedAI Group Exchange Sessions](https://github.com/stanford-medai/stanford-medai.github.io) — with thanks to the MedAI organizers for the template and structure.

## Local development

```bash
# With Docker
docker compose up

# Or with Ruby/Bundler (if Gemfile is present)
bundle exec jekyll serve
```

Then open [http://localhost:4000](http://localhost:4000).

## Content updates

| What | Where |
|------|--------|
| Site title, URL, logo | `_config.yml` |
| Talk schedule | `_data/talks.yml` (`type: upcoming` or `previous`) |
| Organizers | `_data/organizers.yml` + images in `assets/images/` |
| Home / About / Nominate copy | `index.md`, `about.md`, `nominate.md` |

## Talk entry format

```yaml
- speaker: Name
  institution: Affiliation
  type: upcoming   # or previous
  date: M/D/YYYY
  title: "Talk title"
  abstract: "..."
  bio: "..."
  livestream: https://...   # optional
  recording: https://...    # optional
```
