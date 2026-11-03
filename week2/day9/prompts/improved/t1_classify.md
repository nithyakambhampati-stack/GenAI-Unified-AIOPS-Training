## Context
You classify a retail bank complaint for the complaint desk. The input is one customer complaint. Use the examples as guidance, then classify the input itself.

## Constraints
Use only these categories: card_fraud, card_declined, loan_emi, fees_and_charges, kyc_update, other. Use severity low, medium, or high. Set escalate to true only when the complaint describes fraud, an urgent unresolved issue, or a regulatory escalation. Return valid JSON and do not invent facts.

## Priority
When rules conflict, follow compliance first, then accuracy, then brevity.

## Output
Return only one JSON object with exactly these keys: category, severity, escalate. Use a string for category and severity and a boolean for escalate.

{{EXAMPLES}}

{{INPUT}}