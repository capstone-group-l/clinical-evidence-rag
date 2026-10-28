# User Acceptance Testing Plan

## Purpose

The purpose of this User Acceptance Testing (UAT) plan is to evaluate whether intended users can understand and use the Clinical Evidence RAG application effectively.

Testing will focus on the usability of the interface, clarity of generated answers, visibility of citations, ability to inspect supporting evidence, and understanding of insufficient-evidence responses.

This testing evaluates the usability of the prototype and does not validate the system for use in real clinical decision-making.

## Participants

The target is approximately 5–10 volunteer participants, including clinicians, medical students, or other healthcare-related users when available.

Participants should not enter real patient information or personally identifiable medical information during testing.

## Test Procedure

Each participant will be given the same basic instructions and a set of tasks to complete using the application.

Participants should attempt each task without being guided through individual interface controls unless they become unable to continue.

The tester will record whether each task was completed successfully, whether assistance was required, and any problems or confusion encountered.

Sample clinical questions used during testing may be selected from `demo-questions.md`.

## User Tasks

### Task 1: Submit a Clinical Question

Enter a provided sample clinical question into the question field and submit it.

**Success criteria:**
- The participant can identify where to enter a question.
- The participant can identify how to submit the question.
- The participant understands when the system is processing the request.

### Task 2: Understand the Generated Answer

Review the response returned by the system and explain in your own words what answer the system provided.

**Success criteria:**
- The generated answer is easy to locate.
- The participant can understand the basic structure and meaning of the response.

### Task 3: Locate Supporting Sources

Find the citation or source associated with one of the medical claims in the generated answer.

**Success criteria:**
- The participant can identify which source is associated with the claim.
- The participant understands that citations represent evidence retrieved by the system.

### Task 4: Inspect Supporting Evidence

Open or inspect the supporting passage associated with a citation and compare it with the corresponding claim in the answer.

**Success criteria:**
- The supporting passage is easy to access.
- The participant understands the relationship between the generated claim and its supporting evidence.

### Task 5: Interpret an Insufficient-Evidence Response

Submit or review a provided question for which the system does not have sufficient supporting evidence.

**Success criteria:**
- The participant understands that the system is intentionally refusing to provide an unsupported answer.
- The insufficient-evidence message is clear.
- The participant does not confuse the response with a system error.

## Post-Test Questionnaire

Participants will rate each statement from 1 to 5:

- **1 - Strongly disagree**
- **2 - Disagree**
- **3 - Neutral**
- **4 - Agree**
- **5 - Strongly agree**

1. It was easy to understand where to enter a clinical question.
2. It was easy to understand how to submit a question.
3. It was clear when the system was processing my request.
4. The generated answer was clearly presented.
5. It was easy to find the citations or sources associated with the answer.
6. It was easy to inspect the evidence supporting a claim.
7. The relationship between a claim and its supporting evidence was clear.
8. The insufficient-evidence message was understandable.
9. I understood when the system was answering a question and when it was refusing to answer because sufficient evidence was unavailable.
10. The interface was easy to use overall.

## Written Feedback

Participants will also be asked the following questions:

- What part of the interface was easiest to understand?
- What part of the interface was most confusing?
- Was there any information you expected to see but could not find?
- Were the citations and supporting evidence presented in a useful way?
- Was the insufficient-evidence response clear?
- What would you change about the interface?
- Did you encounter any errors or unexpected behavior?
- Do you have any additional comments or suggestions?

## Information to Record

For each participant, the team will record:

- Participant category, such as clinician or medical student
- Tasks completed successfully
- Tasks requiring assistance
- Questionnaire ratings
- Written feedback
- Errors or unexpected behavior encountered

No patient-identifiable or sensitive medical information should be recorded.

## Evaluation of Results

After user acceptance testing is completed, the team will summarize:

- Task completion rates
- Tasks that commonly required assistance
- Average questionnaire ratings
- Common usability problems
- Common participant comments or requests
- Errors encountered during testing
- Interface changes made in response to participant feedback

The results will be used to identify usability problems and guide improvements to the user-facing application before the final project demonstration.
