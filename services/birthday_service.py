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



def calculate_partner_values(X, Y, Z):
    G = reduce_to_single_digit(X + Y + Z)
    A = reduce_to_single_digit(X + Y + Z + G)
    B = reduce_to_single_digit(X + Y)
    C = reduce_to_single_digit(Y + Z)
    D = reduce_to_single_digit(Z + G)
    E = reduce_to_single_digit(X + G)
    G3 = reduce_to_single_digit(A + G)
    G2 = reduce_to_single_digit(G3 + G)
    Y3 = reduce_to_single_digit(Y + A)
    Y2 = reduce_to_single_digit(Y3 + Y)
    Z3 = reduce_to_single_digit(A + Z)
    A2 = reduce_to_single_digit(G3 + Z3)
    A3 = reduce_to_single_digit(G3 + A2)
    A1 = reduce_to_single_digit(A2 + Z3)
    Z2 = reduce_to_single_digit(Z + Z3)
    X3 = reduce_to_single_digit(X + A)
    X2 = reduce_to_single_digit(X + X3)
    B3 = reduce_to_single_digit(B + A)
    B2 = reduce_to_single_digit(B3 + B)
    C3 = reduce_to_single_digit(C + A)
    C2 = reduce_to_single_digit(C3 + C)
    D3 = reduce_to_single_digit(D + A)
    D2 = reduce_to_single_digit(D3 + D)
    E3 = reduce_to_single_digit(E + A)
    E2 = reduce_to_single_digit(E3 + E)
    N = reduce_to_single_digit(Y + G)
    S = reduce_to_single_digit(X + Z)
    LP = reduce_to_single_digit(N + S)
    M = reduce_to_single_digit(B + D)
    J = reduce_to_single_digit(C + E)
    CP = reduce_to_single_digit(M + J)
    DP = reduce_to_single_digit(LP + CP)

    return {
        "X": X, "Y": Y, "Z": Z,
        "G": G, "A": A, "B": B,
        "C": C, "D": D, "E": E,
        "G3": G3, "G2": G2, "Y3": Y3,
        "Y2": Y2, "Z3": Z3, "A2": A2,
        "A3": A3, "A1": A1, "Z2": Z2,
        "X3": X3, "X2": X2, "B3": B3,
        "B2": B2, "C3": C3, "C2": C2,
        "D3": D3, "D2": D2, "E3": E3,
        "E2": E2, "N": N, "S": S,
        "LP": LP, "M": M, "J": J,
        "CP": CP, "DP": DP
    }

# Функция для расчета общей матрицы
def calculate_compatibility_values(partner1_values, partner2_values):
    X = reduce_to_single_digit(partner1_values['X'] + partner2_values['X'])
    Y = reduce_to_single_digit(partner1_values['Y'] + partner2_values['Y'])
    Z = reduce_to_single_digit(partner1_values['Z'] + partner2_values['Z'])
    G = reduce_to_single_digit(partner1_values['G'] + partner2_values['G'])
    A = reduce_to_single_digit(partner1_values['A'] + partner2_values['A'])
    B = reduce_to_single_digit(partner1_values['B'] + partner2_values['B'])
    C = reduce_to_single_digit(partner1_values['C'] + partner2_values['C'])
    D = reduce_to_single_digit(partner1_values['D'] + partner2_values['D'])
    E = reduce_to_single_digit(partner1_values['E'] + partner2_values['E'])
    G3 = reduce_to_single_digit(partner1_values['G3'] + partner2_values['G3'])
    G2 = reduce_to_single_digit(partner1_values['G2'] + partner2_values['G2'])
    Y3 = reduce_to_single_digit(partner1_values['Y3'] + partner2_values['Y3'])
    Y2 = reduce_to_single_digit(partner1_values['Y2'] + partner2_values['Y2'])
    Z3 = reduce_to_single_digit(partner1_values['Z3'] + partner2_values['Z3'])
    A2 = reduce_to_single_digit(partner1_values['A2'] + partner2_values['A2'])
    A3 = reduce_to_single_digit(partner1_values['A3'] + partner2_values['A3'])
    A1 = reduce_to_single_digit(partner1_values['A1'] + partner2_values['A1'])
    Z2 = reduce_to_single_digit(partner1_values['Z2'] + partner2_values['Z2'])
    X3 = reduce_to_single_digit(partner1_values['X3'] + partner2_values['X3'])
    X2 = reduce_to_single_digit(partner1_values['X2'] + partner2_values['X2'])
    B3 = reduce_to_single_digit(partner1_values['B3'] + partner2_values['B3'])
    B2 = reduce_to_single_digit(partner1_values['B2'] + partner2_values['B2'])
    C3 = reduce_to_single_digit(partner1_values['C3'] + partner2_values['C3'])
    C2 = reduce_to_single_digit(partner1_values['C2'] + partner2_values['C2'])
    D3 = reduce_to_single_digit(partner1_values['D3'] + partner2_values['D3'])
    D2 = reduce_to_single_digit(partner1_values['D2'] + partner2_values['D2'])
    E3 = reduce_to_single_digit(partner1_values['E3'] + partner2_values['E3'])
    E2 = reduce_to_single_digit(partner1_values['E2'] + partner2_values['E2'])
    N = reduce_to_single_digit(partner1_values['N'] + partner2_values['N'])
    S = reduce_to_single_digit(partner1_values['S'] + partner2_values['S'])
    LP = reduce_to_single_digit(N + S)
    M = reduce_to_single_digit(partner1_values['M'] + partner2_values['M'])
    J = reduce_to_single_digit(partner1_values['J'] + partner2_values['J'])
    CP = reduce_to_single_digit(M + J)
    DP = reduce_to_single_digit(CP + LP)

    return {
        "X": X, "Y": Y, "Z": Z,
        "G": G, "A": A, "B": B,
        "C": C, "D": D, "E": E,
        "G3": G3, "G2": G2, "Y3": Y3,
        "Y2": Y2, "Z3": Z3, "A2": A2,
        "A3": A3, "A1": A1, "Z2": Z2,
        "X3": X3, "X2": X2, "B3": B3,
        "B2": B2, "C3": C3, "C2": C2,
        "D3": D3, "D2": D2, "E3": E3,
        "E2": E2, "N": N, "S": S,
        "LP": LP, "M": M, "J": J,
        "CP": CP, "DP": DP
    }

# Пример использования:
# partner1_values = calculate_partner_values(10, 5, 1995)  # Значения для первого партнера
# partner2_values = calculate_partner_values(12, 7, 1993)  # Значения для второго партнера
# compatibility_values = calculate_compatibility_values(partner1_values, partner2_values)  # Общие значения
# print(compatibility_values)