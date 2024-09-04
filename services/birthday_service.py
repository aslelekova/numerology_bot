def reduce_to_single_digit(n):
    while n > 22:
        n = sum(int(digit) for digit in str(n))
    return n


def calculate_values(day, month, year):
    year = reduce_to_single_digit(sum(int(digit) for digit in str(year)))

    X = day
    Y = month
    Z = year

    G = X + Y + Z
    G = reduce_to_single_digit(G)

    A = X + Y + Z + G
    A = reduce_to_single_digit(A)

    B = X + Y
    B = reduce_to_single_digit(B)

    C = Y + Z
    C = reduce_to_single_digit(C)

    D = Z + G
    D = reduce_to_single_digit(D)

    E = X + G
    E = reduce_to_single_digit(E)

    G3 = A + G
    G3 = reduce_to_single_digit(G3)

    G2 = G3 + G
    G2 = reduce_to_single_digit(G2)

    Y3 = Y + A
    Y3 = reduce_to_single_digit(Y3)

    Y2 = Y3 + Y
    Y2 = reduce_to_single_digit(Y2)

    Z3 = A + Z
    Z3 = reduce_to_single_digit(Z3)

    A2 = G3 + Z3
    A2 = reduce_to_single_digit(A2)

    A3 = G3 + A2
    A3 = reduce_to_single_digit(A3)

    A1 = A2 + Z3
    A1 = reduce_to_single_digit(A1)

    Z2 = Z + Z3
    Z2 = reduce_to_single_digit(Z2)

    X3 = X + A
    X3 = reduce_to_single_digit(X3)

    X2 = X + X3
    X2 = reduce_to_single_digit(X2)

    B3 = B + A
    B3 = reduce_to_single_digit(B3)

    B2 = B3 + B
    B2 = reduce_to_single_digit(B2)

    C3 = C + A
    C3 = reduce_to_single_digit(C3)

    C2 = C3 + C
    C2 = reduce_to_single_digit(C2)

    D3 = D + A
    D3 = reduce_to_single_digit(D3)

    D2 = D3 + D
    D2 = reduce_to_single_digit(D2)

    E3 = E + A
    E3 = reduce_to_single_digit(E3)

    E2 = E3 + E
    E2 = reduce_to_single_digit(E2)

    N = Y + G
    N = reduce_to_single_digit(N)

    ZZ = X + Z
    ZZ = reduce_to_single_digit(ZZ)

    LP = N + ZZ
    LP = reduce_to_single_digit(LP)

    M = B + D
    M = reduce_to_single_digit(M)

    Zh = C + E
    Zh = reduce_to_single_digit(Zh)

    SP = M + Zh
    SP = reduce_to_single_digit(SP)

    DP = LP + SP
    DP = reduce_to_single_digit(DP)

    PP = SP + DP
    PP = reduce_to_single_digit(PP)

    return {
        "X": X, "Y": Y, "Z": Z,
        "G": G, "A": A, "B": B,
        "C": C, "D": D, "E": E,
        "G3": G3, "G2": G2, "Y3": Y3,
        "Y2": Y2, "A2": A2, "A3": A3,
        "A1": A1, "Z3": Z3, "Z2": Z2,
        "X3": X3, "X2": X2, "B3": B3,
        "B2": B2, "C3": C3, "C2": C2,
        "D3": D3, "D2": D2, "E3": E3,
        "E2": E2, "N": N, "ZZ": ZZ,
        "LP": LP, "M": M, "Zh": Zh,
        "SP": SP, "DP": DP, "PP": PP
    }

