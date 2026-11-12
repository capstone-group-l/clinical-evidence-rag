# Frontend Query Flow Smoke Test Results

## Purpose

These tests verify that the frontend correctly presents the main user-facing states of the Clinical Evidence RAG application.

The tests focus on interface behavior and do not evaluate the medical correctness of generated answers.

## Test Environment

Date: November 2026

Frontend: React application

Backend: FastAPI Clinical Evidence RAG API

## Results

| Test | Expected Result | Actual Result | Status |
|---|---|---|---|
| Successful answer with source | Answer and source are displayed | | |
| Answer with multiple sources | All returned sources are available to the user | | |
| Insufficient evidence | Clear insufficient-evidence message is shown | | |
| Question shorter than 3 characters | Ask button remains disabled | | |
| Backend/API unavailable | Error state is displayed without breaking the page | | |

## Test Details

### 1. Successful Answer With Source

Question used: What is the most common mechanism of carbapenem resistance in carbapenem-resistant Pseudomonas aeruginosa (CRPA)?

Result: PASS. The application successfully returned an answer identifying inactivation or reduced expression of membrane porins, particularly OprD, as the most common mechanism. The answer included an inline citation and a supporting source was displayed below the response. The source included the document title, PMC identifier, chunk identifier, publication date, and the retrieved supporting passage.

Notes: The answer and supporting evidence were displayed correctly and the source could be inspected from the frontend. The response time was very high and should be considered a performance concern even though the frontend behavior itself was correct.

### 2. Multiple Sources

Question used: What percentage of patients with interstitial lung disease (ILD) received a new diagnosis through cryobiopsy?

Result: PASS. The application returned an answer of 35% and displayed three inline citations. Three source entries were shown in the Sources section.

Notes: The frontend successfully displayed multiple source entries. However, all three source entries referenced the same document, Positron Emission-Computed Tomography, Cryobiopsy versus Bronchoalveolar Lavage and Computed Tomography Findings for Interstitial Lung Disease: A Long-Term Follow-Up. This does not prevent the frontend test from passing, but it is worth noting that multiple retrieved chunks from the same document may appear as separate sources. We may later want to consider whether these should remain separate or be grouped by document in the user interface.

### 3. Insufficient Evidence

Question used: What is the recommended oseltamivir dose for influenza in children?

Result: PASS. The application displayed: Insufficient evidence to answer the question. No unsupported medical answer was displayed.

Notes: The insufficient-evidence state was clearly distinguishable from a normal answer and from an application error. The system correctly communicated that it was intentionally refusing to answer because adequate supporting evidence was unavailable.

### 4. Short Question Validation

Input used: Hi

Result: PASS. The Ask button remained disabled and the question could not be submitted.

Notes: The frontend correctly enforced the minimum question-length requirement before making an API request.

### 5. Backend/API Error

Method: The FastAPI backend was stopped while the React frontend remained running. A valid clinical question was then submitted through the frontend.

Result: PASS. The application displayed: Error occurred while fetching the answer. The frontend remained available instead of crashing or displaying a fabricated response.

Notes: The frontend correctly handled loss of backend connectivity and presented an error state to the user.

## Summary

Tests passed: 5

Tests failed: 5

Any failures or unexpected behavior: The main issue observed during testing was response latency. The successful real-pipeline requests took approximately 46.83 to 234.09 seconds, with the first tested request taking 234.09 seconds. Although response-time performance was not the objective of this frontend smoke test, these results indicate that latency should continue to be monitored and optimized separately.

A second observation was that the multiple-source test displayed three source entries originating from the same medical document. The frontend correctly displayed the returned sources, but future UI improvements may consider grouping multiple chunks from the same document to reduce repetition.
