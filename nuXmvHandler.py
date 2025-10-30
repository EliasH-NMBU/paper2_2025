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
    Alert : boolean;
    classifier : {{none, trained, untrained}};
    dgt_3 : boolean;
    dgt_7 : boolean;
    distance_to_target : 0..10;
    Halt : boolean;
    OpState : {{0, 1, 2, 3}};
    Slowdown : boolean;
    TurnoffUVC : boolean;

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
    f1 = "H((classifier = trained & dgt_7) -> (OpState = 1))"
    f2 = "H((classifier = trained) -> (dgt_7 -> (OpState = 1)))"

    g1 = "H((OpState=1 → (Alert ∧ ¬Slowdown ∧ ¬Halt ∧ ¬TurnoffUVC)))"
    g2 = "(H ((OpState = 1) -> ((((! slowdown) & (! halt)) & alert) & (! turnoffUVC))))"

    equiv = check_equivalence_master(g1, g2)
    print("\nEquivalent:", equiv)
