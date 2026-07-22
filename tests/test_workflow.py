from utils.workflow_loader import load_workflow

workflow = load_workflow(
    "config/workflows/windows.json"
)

print(workflow)