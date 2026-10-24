# Retrieval check summary

- **Platform:** n8n (local) + Google Gemini embeddings · embeddings `models/gemini-embedding-001` · n8n workflow "A3 Tool - retrieval check" (v0.2)
- **Generated:** 2026-10-24T00:54:53.948Z · n8n execution 187
- **Context:** Retrieval check: 14 test queries, top-4, 31 KB chunks. Test questions written by the knowledge-base author (`retrieval-tests.json`); each lists the chunk(s) that *should* be retrieved.

## Summary (top-4 results per question)

| Method | Hit rate | Mean recall | Mean precision | MRR |
|---|---|---|---|---|
| Keyword | 14/14 (100%) | 0.857 | 0.321 | 0.952 |
| Semantic | 14/14 (100%) | 0.893 | 0.339 | 1.000 |
| Hybrid | 14/14 (100%) | 0.893 | 0.339 | 0.964 |

Hit rate: at least one expected chunk in the top 4. Recall: share of the expected chunks found. Precision: share of the top 4 that were expected (at most about 0.5 here, because most questions have 1–2 expected chunks). MRR: 1 / the rank of the first expected chunk, averaged.

## Per question

| # | Question | Expected | Keyword top 4 | Semantic top 4 | Hybrid top 4 |
|---|---|---|---|---|---|
| 1 | applicant took time off work for a few years for personal reasons | POL-GAPS | **POL-GAPS**, POL-EXPERIENCE, EOA-16, EOA-20 | **POL-GAPS**, POL-IRRELEVANT, POL-EXPERIENCE, POL-ADJ | **POL-GAPS**, POL-EXPERIENCE, POL-IRRELEVANT, EOA-16 |
| 2 | is a gap in employment a reason to give a lower score | POL-GAPS, SDA-14 | **POL-GAPS**, POL-INJECTION, DDA-15, POL-ADJ | **POL-GAPS**, POL-SCORING, POL-EXPERIENCE, POL-IRRELEVANT | **POL-GAPS**, POL-INJECTION, POL-SCORING, DDA-15 |
| 3 | candidate only assisted the payroll team by checking timesheets | POL-EXPERIENCE | **POL-EXPERIENCE**, POL-AI-SCREENING, POL-EQUIV, EOA-ADS | **POL-EXPERIENCE**, POL-IRRELEVANT, POL-EQUIV, POL-ADJ | **POL-EXPERIENCE**, POL-EQUIV, POL-AI-SCREENING, POL-IRRELEVANT |
| 4 | does Employment Hero count as payroll software experience | POL-EQUIV | **POL-EQUIV**, POL-EXPERIENCE, POL-GAPS, POL-OVERSEAS | **POL-EQUIV**, POL-EXPERIENCE, POL-OVERSEAS, EOA-ADS | **POL-EQUIV**, POL-EXPERIENCE, POL-OVERSEAS, POL-GAPS |
| 5 | degree completed at a university outside Australia | POL-OVERSEAS | **POL-OVERSEAS**, AIEP-FAIR, POL-EQUIV | **POL-OVERSEAS**, POL-EQUIV, RDA-15, DDA-15 | **POL-OVERSEAS**, POL-EQUIV, AIEP-FAIR, RDA-15 |
| 6 | candidate uses a wheelchair and asks for an accessible interview | POL-ADJ, DDA-21A, EOA-20 | **POL-ADJ**, **EOA-20**, **DDA-21A**, EOA-107 | **POL-ADJ**, **EOA-20**, **DDA-21A**, DDA-15 | **POL-ADJ**, **EOA-20**, **DDA-21A**, EOA-107 |
| 7 | can we refuse to employ someone because of their age | FWA-351, ADA-18 | RDA-15, FWA-342, **FWA-351**, DDA-21A | **ADA-18**, EOA-ADS, EOA-107, FWA-351-EXC | RDA-15, **ADA-18**, FWA-342, EOA-ADS |
| 8 | job ad asks for a native English speaker | EOA-ADS, RDA-15 | **EOA-ADS**, POL-OVERSEAS, FWA-351-EXC, EOA-8-9 | **EOA-ADS**, POL-OVERSEAS, **RDA-15**, ADA-18 | **EOA-ADS**, POL-OVERSEAS, FWA-351-EXC, **RDA-15** |
| 9 | resume contains text telling the AI to ignore instructions and give top marks | POL-INJECTION | **POL-INJECTION**, APP-3, APP-APPLICANTS, AIEP-FAIR | **POL-INJECTION**, AIEP-OVERSIGHT, POL-AI-SCREENING, AIEP-FAIR | **POL-INJECTION**, AIEP-FAIR, APP-3, AIEP-OVERSIGHT |
| 10 | resume mentions the applicant's religion and children | POL-IRRELEVANT, EOA-107 | **POL-IRRELEVANT**, **EOA-107**, APP-3, APP-APPLICANTS | **POL-IRRELEVANT**, **EOA-107**, APP-3, APP-APPLICANTS | **POL-IRRELEVANT**, **EOA-107**, APP-3, APP-APPLICANTS |
| 11 | does the Privacy Act apply to resumes from unsuccessful job applicants | APP-APPLICANTS | **APP-APPLICANTS**, APP-5-6, POL-DATA, EOA-20 | **APP-APPLICANTS**, APP-3, APP-5-6, POL-DATA | **APP-APPLICANTS**, APP-5-6, POL-DATA, APP-3 |
| 12 | how long should we keep screening logs and AI assessments | POL-DATA, APP-11-12 | **APP-11-12**, **POL-DATA**, POL-AI-SCREENING, APP-APPLICANTS | **APP-11-12**, POL-AI-SCREENING, **POL-DATA**, APP-5-6 | **APP-11-12**, **POL-DATA**, POL-AI-SCREENING, APP-APPLICANTS |
| 13 | who makes the final decision to reject an applicant | POL-PURPOSE, POL-AI-SCREENING | **POL-PURPOSE**, FWA-351, APP-5-6, EOA-16 | **POL-PURPOSE**, FWA-342, POL-INJECTION, EOA-16 | **POL-PURPOSE**, EOA-16, FWA-351, FWA-342 |
| 14 | what does or equivalent qualification mean for Certificate IV | POL-EQUIV | **POL-EQUIV**, POL-OVERSEAS, APP-11-12, AIEP-FAIR | **POL-EQUIV**, POL-OVERSEAS, POL-EXPERIENCE, POL-GAPS | **POL-EQUIV**, POL-OVERSEAS, APP-11-12, POL-EXPERIENCE |

Expected chunks are in **bold**.

## Facts to note (from Member 1)
- The keyword figures (recall 0.857, MRR 0.952) match the knowledge-base author's own BM25 test in KB_HANDOVER (0.86 / 0.95).
- Semantic search had the best ranking (MRR 1.000): the right chunk was first for all 14 questions.
- **Q7 "can we refuse to employ someone because of their age":** keyword search ranked RDA-15 (race) first and missed ADA-18 (age); semantic search ranked ADA-18 first. This is the paraphrase case that motivated hybrid retrieval.
- **Q2:** SDA-14 (sex discrimination) was not retrieved by any method; POL-GAPS (the main answer) was ranked first by all three.
- Hybrid (reciprocal-rank fusion of the two lists) matched semantic recall (0.893); its MRR (0.964) sits between the two methods.
