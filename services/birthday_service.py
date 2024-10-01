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


LETTER_VALUES = {
    'А': 1, 'И': 1, 'С': 1, 'Ъ': 1,
    'Б': 2, 'Й': 2, 'Т': 2, 'Ы': 2,
    'В': 3, 'К': 3, 'У': 3, 'Ь': 3,
    'Г': 4, 'Л': 4, 'Ф': 4, 'Э': 4,
    'Д': 5, 'М': 5, 'Х': 5, 'Ю': 5,
    'Е': 6, 'Н': 6, 'Ц': 6, 'Я': 6,
    'Ё': 7, 'О': 7, 'Ч': 7,
    'Ж': 8, 'П': 8, 'Ш': 8,
    'З': 9, 'Р': 9, 'Щ': 9
}


def calculate_name_value(name):
    total_value = sum(LETTER_VALUES.get(letter.upper(), 0) for letter in name)
    return reduce_to_single_digit(total_value)

def calculate_birth_values(day, month, year):
    day = reduce_to_single_digit(day if day <= 22 else day - 22)
    month = reduce_to_single_digit(month)
    
    year = sum(int(digit) for digit in str(year))
    year = reduce_to_single_digit(year)
    
    return day, month, year


def calculate_houses(user_name, day, month, year):
    name_parts = user_name.split()

    if len(name_parts) != 3:
        raise ValueError("Ожидается строка с тремя частями: фамилия, имя, отчество")

    surname = name_parts[0]
    name = name_parts[1]
    patronymic = name_parts[2]

    A0 = calculate_name_value(name)
    D3 = calculate_name_value(surname)
    F5 = calculate_name_value(patronymic)


    B1, C2, E4 = calculate_birth_values(day, month, year)


    G6 = C2 + F5
    H7 = A0 + C2
    Y8 = C2 + D3
    M9 = B1 + D3
    N10 = D3 + E4
    Q11 = A0 + E4
    T12 = E4 + F5
    P13 = B1 + F5
    O14 = H7 + P13
    I16 = H7 + M9
    L15 = O14 + I16
    V18 = M9 + Q11
    X17 = I16 + V18
    R20 = Q11 + P13
    Z19 = V18 + R20
    K21 = O14 + R20

    houses = {
        'A0': reduce_to_single_digit(A0),
        'B1': reduce_to_single_digit(B1),
        'C2': reduce_to_single_digit(C2),
        'D3': reduce_to_single_digit(D3),
        'E4': reduce_to_single_digit(E4),
        'F5': reduce_to_single_digit(F5),
        'G6': reduce_to_single_digit(G6),
        'H7': reduce_to_single_digit(H7),
        'Y8': reduce_to_single_digit(Y8),
        'M9': reduce_to_single_digit(M9),
        'N10': reduce_to_single_digit(N10),
        'Q11': reduce_to_single_digit(Q11),
        'T12': reduce_to_single_digit(T12),
        'P13': reduce_to_single_digit(P13),
        'O14': reduce_to_single_digit(O14),
        'I16': reduce_to_single_digit(I16),
        'L15': reduce_to_single_digit(L15),
        'V18': reduce_to_single_digit(V18),
        'X17': reduce_to_single_digit(X17),
        'R20': reduce_to_single_digit(R20),
        'Z19': reduce_to_single_digit(Z19),
        'K21': reduce_to_single_digit(K21)
    }

    return houses


def calculate_partner_matrix(day, month, year):
    year = reduce_to_single_digit(sum(int(digit) for digit in str(year)))

    X = day
    Y = month
    Z = year

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
    A2 = reduce_to_single_digit(G3 + Z3)  # A2 = G3 + Z3
    A3 = reduce_to_single_digit(G3 + A2)   # A3 = G3 + A2
    A1 = reduce_to_single_digit(A2 + Z3)
    return {
        "X": X, "Y": Y, "Z": Z, "G": G, "A": A, "B": B,
        "C": C, "D": D, "E": E, "G3": G3, "G2": G2,
        "Y3": Y3, "Y2": Y2, "Z3": Z3, "Z2": Z2, "X3": X3,
        "X2": X2, "B3": B3, "B2": B2, "C3": C3, "C2": C2,
        "D3": D3, "D2": D2, "E3": E3, "E2": E2, "N": N, 
        "S": S, "LP": LP, "M": M, "J": J, "CP": CP, "DP": DP,
        "A2": A2, "A3": A3, "A1": A1
    }

def calculate_compatibility(date1, date2):

    day1, month1, year1 = date1
    day2, month2, year2 = date2

    partner1_matrix = calculate_partner_matrix(day1, month1, year1)
    partner2_matrix = calculate_partner_matrix(day2, month2, year2)

    combined_matrix = {}
    for key in partner1_matrix:
        combined_value = partner1_matrix[key] + partner2_matrix[key]
        combined_matrix[key] = reduce_to_single_digit(combined_value)
    
    print(combined_matrix)
    return combined_matrix