import subprocess

def check_realizable(formula):
    spec = f"""
    [INPUT]
    classifier distance_to_target

    [OUTPUT]
    alert halt slowdown turnoffUVC OpState

    [SYS_LTL]
    {formula}
    """

    with open("spec.tlsf", "w") as f:
        f.write(spec)

    result = subprocess.run(
        ["strix", "spec.tlsf"],
        capture_output=True,
        text=True
    )

    return "REALIZABLE" in result.stdout