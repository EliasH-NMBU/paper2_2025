import subprocess
import tempfile
import os

def run_nuxmv(model_text: str):
    # Create a temporary .smv file
    with tempfile.NamedTemporaryFile(suffix=".smv", delete=False, mode="w") as tmp:
        tmp.write(model_text)
        tmp_path = tmp.name

    try:
        # Run NuXMV on the temp file
        result = subprocess.run(
            ["nuxmv.exe", tmp_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout
    finally:
        os.remove(tmp_path)

# Example: a small SMV model with an LTL property
model = """
MODULE main
VAR
  x : boolean;
  y : boolean;

LTLSPEC H (x -> y)
"""

output = run_nuxmv(model)
print(output)
