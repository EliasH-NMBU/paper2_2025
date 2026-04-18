import subprocess
import tempfile
import os
import re
import unicodedata





def responseHandler(model, f1, f2):

    # Create temporary .smv file
    with tempfile.NamedTemporaryFile(suffix=".smv", delete=False, mode="w", encoding="utf-8") as tmp:
        tmp.write(model)
        tmp_path = tmp.name

    try:
        try:
            result = subprocess.run(
                ["nuxmv.exe", tmp_path],
                capture_output=True,
                text=True,
                timeout=45       # seconds
            )
        except subprocess.TimeoutExpired:
            print("⏳ NuXMV timed out — returning empty")
            return

    finally:
        # Ensure temporary file is always removed
        os.remove(tmp_path)

    output = result.stdout
    error_output = result.stderr
    print("NuXMV Output:", output)
    if "is true" in output:
        return True
    elif "is false" in output:
        return False
    else:
        print("⚠️ Unexpected NuXMV output format")
        print("---- STDOUT ----")
        print("Reference:", f1, "\n", "Generated:", f2)
        print("---- STDERR ----")
        print(error_output)
        print("----------------")
        return 
    

if __name__ == "__main__":
    f1 = "(G ((! (classifier = 0)) -> (distance_to_target >= 0)))"
    f2 = "G ((classifier != 0) -> (distance_to_target >= 0))"

    model = f"""
        MODULE main

        IVAR
        classifier : {{0, 1, 2}};
        distance_to_target : 0..10;

        VAR
        alert : boolean;
        halt : boolean;
        slowdown : boolean;
        turnoffUVC : boolean;
        OpState : {{0, 1, 2, 3}};

        DEFINE
        dgt_3 := distance_to_target > 3;
        dgt_7 := distance_to_target > 7;

        LTLSPEC ({f1}) <-> ({f2})"""

    result = responseHandler(model, f1, f2)
    print("Equivalence Result:", result)