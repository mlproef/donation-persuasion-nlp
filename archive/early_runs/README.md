# Earlier runs

Outputs from earlier versions of the pipeline, kept for reference only.
They are **superseded** by the files in `results/` and `figures/`.

* `sentiment_*` and `refusal_*`: the first LLM sentiment run and an earlier
  reaction classifier. They use an older definition of a "donation dialog"
  (53.6% donation rate instead of the 69.9% used everywhere else), so their
  numbers do not match the current results.
* `interest_donation_*.png`, `strategy_sentiment_correlation.png`,
  `interest_v2_analysis.png` (Russian labels): earlier versions of current plots.
* `analyze_clusters.py`: embedding clustering used to find refusal examples for
  hand-labelling (iteration 3 in `docs/methodology.md`). Its inputs are not in
  this repository.
