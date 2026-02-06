# gd-manufacturing-demo

Manufacturing demo project for GoodData Cloud.

### Data pipeline

The sample data lives in a public CSV. This repo includes a GitHub Actions pipeline that refreshes a MotherDuck table (`main.production_line`) from that CSV:

- Workflow: `.github/workflows/production_line_pipeline.yml`
- Script: `data_pipeline/main.py`

See `Manufacturing.md` for setup details.
