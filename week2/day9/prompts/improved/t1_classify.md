## Context
First-pass triage for the retail bank complaint desk: read the supplied complaint as one case, learn the label boundaries from the examples, and classify only the current case.

## Constraints
Use only these categories: card_fraud, card_declined, loan_emi, fees_and_charges, kyc_update, other. Use severity low, medium, or high. Treat confirmed or suspected unauthorised loss, an overdue unresolved complaint, or a stated regulatory escalation as escalation signals. Do not infer facts that the case does not provide. Return valid JSON.

## Priority
When rules conflict, follow compliance first, then accuracy, then brevity.

## Output
Return only one JSON object with exactly these keys: category, severity, escalate. Category and severity must be strings; escalate must be a JSON boolean. Do not include an explanation outside the object.

{{EXAMPLES}}

{{INPUT}}