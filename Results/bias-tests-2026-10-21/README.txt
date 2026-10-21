Bias test results: 21 Oct 2026 (produced by Member 1 on the official workflow, v0.2)

results_bias_tests.csv               one line per run (20 runs): execution ID, timestamp, platform, models, scores, route, retrieved chunks, reasons
bias_summary.md                      readable summary: per-variant scores, mean/SD, routes, paired comparisons, notes and limits
redaction_equivalence_R00a_R00f.json check that with redaction ON the two resumes reach the model as identical text
bias_outputs_readable.md             full output of every run (for Appendix C), labelled with platform, date, execution ID and context
run-logs/                            full JSON log of each run (every attempt, searches, reviewer feedback, gate reasons, labels)
inputs/                              the batch definition, the 4 resumes and the job ad exactly as used
