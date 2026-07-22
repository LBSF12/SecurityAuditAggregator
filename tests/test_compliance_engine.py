from analyzers.audit_engine import load_windows_audit
from analyzers.compliance_engine import evaluate

audit = load_windows_audit(

    "extracted/Server01"

)

result = evaluate(

    audit,

    "config/requirements/3_1.json"

)

print(result)