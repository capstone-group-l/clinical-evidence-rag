# Frontend Accessibility and Responsive Test Results

## Purpose

This testing evaluates the basic accessibility and responsive behavior of the
Clinical Evidence RAG user interface.

Testing includes automated accessibility analysis, keyboard navigation, and
manual inspection at common viewport sizes.

## Test Environment

Date: November 2026

Frontend: React

Browser: Chrome

Automated accessibility tool: Axe

## Automated Accessibility Testing

| Test | Result |
|---|---|
| Initial query page accessibility scan | PASS |
| Answer and source view accessibility scan | PASS |
| Source control exposes expanded state | PASS |

Automated accessibility tests were executed using Axe within the existing
Vitest frontend test suite.

## Keyboard Navigation

| Test | Expected Behavior | Actual Result | Status |
|---|---|---|---|
| Reach clinical question input | Input can be reached using Tab | | |
| Reach Ask button | Ask button can be reached using Tab | | |
| Reach source control | Source control can be reached using Tab | | |
| Activate source control | Enter or Space expands the source | | |

## Responsive Testing

### Mobile — 375 × 667

- Query input visible: ✓
- Ask button visible: ✓
- Horizontal overflow: ✓
- Answer readable: ✓
- Sources accessible: ✓
- Result: PASS

### Tablet — 768 × 1024

- Query input visible: ✓
- Ask button visible: ✓
- Horizontal overflow: ✓
- Answer readable: ✓
- Sources accessible: ✓
- Result: PASS

### Desktop — 1440 × 900

- Query input visible: ✓
- Ask button visible: ✓
- Horizontal overflow: ✓
- Answer readable: ✓
- Sources accessible: ✓
- Result: PASS

## Error and Abstention States

Verify that the following remain readable and visually distinguishable:

- Insufficient evidence response
- Backend/API error response

Result: PASS

## Summary

Automated accessibility tests passed: 3

Keyboard tests passed: 3

Responsive viewport tests passed: 3

Failures or issues identified: 0

Overall result: PASS
