import subprocess
import tempfile
import os


def check_equivalence_master(formula1, formula2):
    
    model = f"""
    MODULE main
    VAR
    classifier : {{none, trained, untrained}};
    dgt_3 : boolean;
    dgt_7 : boolean;
    distance_to_target : 0..10;
    OpState : 0..3;

    LTLSPEC ({formula1}) <-> ({formula2})
    """

    with tempfile.NamedTemporaryFile(suffix=".smv", delete=False, mode="w") as tmp:
        tmp.write(model)
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            ["nuxmv.exe", tmp_path],
            capture_output=True,
            text=True,
            timeout=30
        )

        output = result.stdout
        print(output)

        if "is true" in output:
            return True
        elif "is false" in output:
            return False
        else:
            return None
        
    finally:
        os.remove(tmp_path)


if __name__ == "__main__":

    # Example usage
    f1 = "H((classifier = trained & dgt_7) -> (OpState = 1))"
    f2 = "H((classifier = trained) -> (dgt_7 -> (OpState = 1)))"

    equiv = check_equivalence_master(f1, f2)
    print("\nEquivalent:", equiv)
