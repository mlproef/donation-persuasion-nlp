# Methodology

This page explains how each label was produced and how the approach evolved.
For a quick overview, start with the [README](../README.md).

## The three classification tasks

| Task | Applied to | Labels | Script |
|---|---|---|---|
| 1. Sentiment | persuadee messages (10,332) | negative / neutral / positive | `src/classification/llama_sentiment.py` |
| 2. Interest in donating | persuadee messages (10,332) | Not Interested (0) / Neutral (1) / Interested (2) | `src/classification/llama_interest.py` |
| 3. Persuasion strategy | persuader messages (10,600) | one of 49 strategies in 12 categories | `src/classification/llama_strategies.py` |

All three run against a local LLM served by [Ollama](https://ollama.com).
Code defaults: `gpt-oss:20b` for tasks 1 and 2, `qwen3:30b` for task 3
(both can be changed with the `OLLAMA_MODEL` environment variable).

### Tasks 1 and 2: one request per dialog

Whether a reply like *"maybe later"* is a polite refusal or genuine interest
depends on what came before it. So instead of classifying messages one by one,
the scripts send a whole dialog in a single request and ask the model to label
every persuadee message in it. The model must answer with JSON between
`BEGIN_JSON` / `END_JSON` markers; the script extracts and parses it, keeps only
labels in the allowed set and leaves the rest empty. Progress is saved as it
goes, and a rerun only processes messages that are still unlabelled, so a long
run can be interrupted and resumed.

### Task 3: hierarchical strategy taxonomy

The taxonomy (`src/classification/strategies_hierarchical.py`) was compiled from
persuasion and social-influence literature (sources in
[`strategies_sources.md`](strategies_sources.md)). Every strategy has a
definition, typical marker phrases and explicit *use if / avoid if* rules that
separate look-alike strategies (for example *Pre-giving* vs *Reciprocity* vs
*Rewarding Activity*).

Each persuader message is classified separately, together with the five
preceding turns as context. The prompt makes the model decide in two steps:
first the **category** (e.g. *Exchange / Incentives*, *Norms / Morality / Values*),
then the **strategy** inside it, instead of choosing among ~50 strategies at once.

Result: 97.7% of persuader messages received a strategy, 45 of the 49 strategies
occurred at least once, on average 7.5 distinct strategies per dialog.

## Linking labels to donations

Donations come from the corpus (`B6`). A dialog counts as ending in a donation
when either participant donated more than $0; 711 of 1,017 dialogs (69.9%) did.

* **Reaction vs donation** (`analyze_interest_donation_correlation.py`,
  `make_key_findings_figure.py`): persuadee labels are aggregated per dialog
  (highest interest reached, dominant sentiment, any refusal) and donation rates
  are compared between groups.
* **Strategy vs outcome** (`analyze_strategy_*_correlation.py`): every strategy
  is paired with the persuadee's **next** message (for sentiment and interest)
  or with the dialog's final outcome (for donation).
* **Joint view** (`analyze_joint_strategies_effect.py`): four contrasting
  strategies (two pressure-based, two cooperative) side by side on all three
  outcomes.

## How the approach evolved

The LLM pipeline is the fourth iteration. Earlier attempts are documented in
Russian in [`dev-notes/`](dev-notes/); in short:

1. **Zero-shot NLI.** `facebook/bart-large-mnli` and `roberta-large-mnli` scored
   hypotheses such as *"The person refuses to donate"* for each message.
   Fast, but it ignored context and confused polite small talk with agreement.
2. **Calibrated NLI features.** 500 persuadee messages were labelled by hand and
   a logistic regression was trained on four NLI hypothesis scores.
3. **Fine-tuned RoBERTa with context.** RoBERTa was fine-tuned on the hand-labelled
   messages plus the two preceding turns. Refusals are rare (about 1 in 10
   messages), and the first model never predicted them at all; class weights and
   macro-F1 model selection were added, and clustering of message embeddings
   was used to surface more refusal examples for labelling.
4. **LLM with dialog context** (current). Needs no training data and lets the
   model see the conversation around each message, which matters most for the
   *interest* label.

## Limitations

* **The LLM labels were not validated against human labels.** The hand-labelled
  set from iteration 2 would allow measuring agreement; that is the most useful
  next step.
* **Correlation, not causation.** Persuaders choose strategies in response to how
  the conversation is going, so a strategy that appears in successful dialogs is
  not necessarily what caused the donation.
* **Small groups.** Some strategies occur only a handful of times
  (`results/strategy_donation_stats.csv` lists the counts); their rates are not
  reliable.
* **Donation definition.** Counting a dialog as successful when *either* side
  donated also includes persuaders' own donations. A persuadee-only outcome would
  be a cleaner target.
