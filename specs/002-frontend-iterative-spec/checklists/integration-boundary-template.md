# Integration Boundary Template

Define integration behavior per capability before implementation.

## Capability

- cycle_id:
- capability_name:
- related_story:

## Contract Status

- contract_status: CONTRACTED | NOT_CONTRACTED
- endpoint_reference:

## Runtime Behavior

- fallback_strategy:
- transition_criteria_to_real_api:
- error_behavior:

## Endpoint Request Gate

- new_endpoint_required: yes | no
- endpoint_request_id:
- endpoint_request_reference:

## Validation

- [ ] Contract status is explicit
- [ ] Fallback is defined when not contracted
- [ ] Endpoint request exists before backend demand (if required)
