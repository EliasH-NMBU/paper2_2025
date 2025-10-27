import spot

# This script requires the Spot library to be installed.
# You can install it on Ubuntu/Debian systems using the following commands.

# lsb_release -a , If you’re on Ubuntu or Debian, you’re golden.

# sudo apt update
# sudo apt install python3-spot spot libspot-dev

'''
spot --version
python3 -c "import spot; print(spot.formula('G(a -> Fb)'))" , G(a -> Fb)


spot 2.12.3 (compiled with GCC 11.4.0)
pkg-config --cflags --libs spot
-I/usr/include/spot -lspot -lbuddy

'''

f1 = spot.formula("G(((Classifier = 1 ∧ dgt_7) → (OpState = 1)))")
f2 = spot.formula("(G ((classifier = 1) -> (dgt_7 -> (OpState = 1))))")

print("Formula 1:", f1)
print("Formula 2:", f2)
print("Equivalent:", f1.equivalent_to(f2))
