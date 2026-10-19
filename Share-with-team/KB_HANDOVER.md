
## Files
| File | Source | Type | Chunks | IDs |
|---|---|---|---|---|
| `01_fair-work-act.md` | Fair Work Act 2009 (Cth), general protections | Legislation | 3 | `FWA-` |
| `02_cth-discrimination-acts.md` | Sex, Age, Disability and Racial Discrimination Acts | Legislation | 5 | `SDA-` `ADA-` `DDA-` `RDA-` |
| `03_vic-equal-opportunity-act.md` | Equal Opportunity Act 2010 (Vic) and the Victorian Equal Opportunity and Human Rights Commission (VEOHRC) recruitment guideline | Legislation and regulator guidance | 6 | `EOA-` |
| `04_privacy-act-apps.md` | Privacy Act 1988 (Cth), Australian Privacy Principles (APPs) and Office of the Australian Information Commissioner (OAIC) guidance | Legislation and regulator guidance | 4 | `APP-` |
| `05_ai-ethics-principles.md` | Australia's AI Ethics Principles | National framework | 2 | `AIEP-` |
| `06_mbs-hiring-policy.md` | Melbourne Business Services Recruitment and Selection Policy (**fictional**, written by us) | Company policy | 11 | `POL-` |
| **Total** | | | **31** | |

## How it was prepared (for B2)
- **Chunking.** Each chunk covers one legal section or one policy rule, and is 104–187 words. We split by topic rather than by a fixed number of characters, so each chunk can be cited on its own. The workflow keeps each chunk whole ("Keep chunks whole" node, 6,000-character limit).
- **Metadata.** Each chunk has the following fields:
  - `source`, `section`, `title`, `jurisdiction`, `topic`, `url` and `accessed`, which show where the chunk came from and when it was checked;
  - `keywords`, which list the **everyday words a resume or recruiter would use**, not just the legal terms. For example, the career-break chunk lists "time out, personal reasons, returning to work". BM25 keyword search counts the title and keywords twice, and they are also embedded for semantic search.
- **Practical meaning.** Each legal chunk ends with a "Practical meaning for screening" paragraph. It turns the law into something the agent can apply to a resume, such as "a name must not affect any score".
- **Why the company policy matters.** The policy contains rules the model cannot know without retrieval, for example:
  - POL-EXPERIENCE: "assisting" payroll scores at most 1 for E1;
  - POL-EQUIV: Employment Hero counts as a payroll system for D1;
  - POL-GAPS: experience before a career break counts in full.

  This is what should make the with/without-RAG comparison in D1 clearly different. **Suggested comparison cases:** R00b (assisting versus processing payroll) and R00d (career break).
- **Accuracy.** The legal content is closely summarised, not quoted in full. It was checked against AustLII, legislation.gov.au, fairwork.gov.au, humanrights.gov.au, humanrights.vic.gov.au, oaic.gov.au and industry.gov.au on 20 Oct 2026. The SDA s 14 and ADA s 18 wording is from the standard text of those Acts, so spot-check it on legislation.gov.au if there is time.

## Retrieval test result (keyword search only, run outside n8n)
Using the workflow's own BM25 code on the 14 questions in `retrieval-tests.json`, with the top 4 results per question:
- **Hit rate:** 14/14 (100%)
- **Mean recall:** 0.86
- **MRR:** 0.95

Run the n8n retrieval check to get the semantic and hybrid figures as well.
