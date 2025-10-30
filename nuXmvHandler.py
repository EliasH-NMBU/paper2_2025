import subprocess
import tempfile
import os


def check_equivalence_master(formula1, formula2):
    
    
    def normalize(f):
        return (f.replace("∧", "&")
                .replace("∨", "|")
                .replace("¬", "!")
                .replace("→", "->")
                .replace("≥", ">=")
                .replace("≤", "<=")
                .replace("=", "=")
                )

    f1 = normalize(formula1)
    f2 = normalize(formula2)


    model = f"""
    MODULE main
    VAR
    alert : boolean;
    classifier : {{0, 1, 2}};
    dgt_3 : boolean;
    dgt_7 : boolean;
    distance_to_target : 0..10;
    halt : boolean;
    OpState : {{0, 1, 2, 3}};
    slowdown : boolean;
    turnoffUVC : boolean;

    LTLSPEC ({f1}) <-> ({f2})
    """

    with tempfile.NamedTemporaryFile(suffix=".smv", delete=False, mode="w", encoding="utf-8") as tmp:
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

        if "is true" in output:
            return True
        elif "is false" in output:
            return False
        else:
            print("⚠️ Unexpected NuXMV output format")
            return False
        
    finally:
        os.remove(tmp_path)


if __name__ == "__main__":

    # Example usage
    f1 = "H((classifier = 1 & dgt_7) -> (OpState = 1))"
    f2 = "H((classifier = 1) -> (dgt_7 -> (OpState = 1)))"

    g1 = "H((OpState=1 → (alert ∧ ¬slowdown ∧ ¬halt ∧ ¬turnoffUVC)))"
    g2 = "(H ((OpState = 1) -> ((((! slowdown) & (! halt)) & alert) & (! turnoffUVC))))"

    h1 = "(H ((classifier = 2) -> ((! dgt_3) -> (OpState = 3))))"
    h2 = "H(((classifier = 2) ∧ ¬dgt_3) → (OpState = 3))"

    equiv = check_equivalence_master(h1, h2)
    print("\nEquivalent:", equiv)
