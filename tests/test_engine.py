from analyzers.audit_engine import evaluate_windows_requirement

result = evaluate_windows_requirement(

    "extracted/Server01",

    "3-1_AuditPolicy.txt",

    "config/mappings/audit_policy.json",

    "config/requirements/3_1.json"

)

print(result)