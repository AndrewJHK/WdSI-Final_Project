import re
import itertools


def count_ones(binary_str):
    """
    Zlicza liczbę jedynek w reprezentacji binarnej.
    """
    return binary_str.count('1')


def is_adjacent(term1, term2):
    """
    Sprawdza, czy dwa terminy różnią się dokładnie jedną pozycją.
    """
    diff_count = sum(1 for a, b in zip(term1, term2) if a != b)
    return diff_count == 1


def merge_terms(term1, term2):
    """
    Łączy dwa terminy, które różnią się dokładnie jedną pozycją.
    """
    return ''.join(a if a == b else '-' for a, b in zip(term1, term2))


def is_covered(minterm, implicant):
    """
    Sprawdza, czy minterm jest pokrywany przez implicant.
    """
    return all(m == i or i == '-' for m, i in zip(minterm, implicant))


def remove_redundant_implicants(essential_prime_implicants, coverage, minterms_bin):
    """
    Usuwa nadmiarowe implicanty, pozostawiając minimalny zestaw pokrywający wszystkie mintermy.
    """
    minimized_implicants = set(essential_prime_implicants)
    for implicant in list(minimized_implicants):
        # Sprawdź, czy implicant można usunąć
        if all(any(is_covered(m, other) for other in minimized_implicants - {implicant})
               for m in minterms_bin if is_covered(m, implicant)):
            minimized_implicants.remove(implicant)
    return list(minimized_implicants)


def quine_mccluskey(minterms):
    """
    Implementacja algorytmu Quine-McCluskey.
    """
    num_vars = max(minterms).bit_length()
    minterms_bin = [f"{m:0{num_vars}b}" for m in minterms]

    # Grupowanie według liczby jedynek
    grouped = {}
    for m in minterms_bin:
        count = count_ones(m)
        grouped.setdefault(count, []).append(m)

    # Redukcja mintermów
    all_terms = set(minterms_bin)
    implicants = set()
    used = set()
    while grouped:
        next_grouped = {}
        for count, group in grouped.items():
            for term1 in group:
                for term2 in grouped.get(count + 1, []):
                    if is_adjacent(term1, term2):
                        merged = merge_terms(term1, term2)
                        next_grouped.setdefault(count_ones(merged), []).append(merged)
                        used.add(term1)
                        used.add(term2)
                        implicants.add(merged)
        grouped = next_grouped
        all_terms.update(implicants)

    # Identyfikacja implicantów prostych
    prime_implicants = all_terms - used

    # Minimalizacja tabeli pokrycia
    coverage = {m: [] for m in minterms_bin}
    for m in minterms_bin:
        for p in prime_implicants:
            if all(p[i] == '-' or p[i] == m[i] for i in range(len(p))):
                coverage[m].append(p)

    # Wybór istotnych implicantów
    essential_prime_implicants = set()
    covered_minterms = set()
    for m, covers in coverage.items():
        if len(covers) == 1:
            essential_prime_implicants.add(covers[0])
            covered_minterms.add(m)

    # Pozostałe mintermy do pokrycia
    uncovered_minterms = set(minterms_bin) - covered_minterms
    remaining_implicants = set(prime_implicants) - essential_prime_implicants
    while uncovered_minterms:
        if not remaining_implicants:
            break
        best_implicant = max(
            remaining_implicants,
            key=lambda imp: sum(
                1 for m in uncovered_minterms if all(imp[i] == '-' or imp[i] == m[i] for i in range(len(imp))))
        )
        essential_prime_implicants.add(best_implicant)
        uncovered_minterms -= {
            m for m in uncovered_minterms if
            all(best_implicant[i] == '-' or best_implicant[i] == m[i] for i in range(len(best_implicant)))
        }
        remaining_implicants.remove(best_implicant)

    # Eliminacja nadmiarowych implicantów
    minimized_terms = remove_redundant_implicants(essential_prime_implicants, coverage, minterms_bin)
    return minimized_terms


def bit2num(bits):
    ret = 0
    bits = [-b for b in bits]
    for b in bits:
        ret = (ret << 1) | b
    return ret


def parser(str):
    if re.fullmatch("([ \\^\\&\\|\\~\\(\\)]|(x\\d+))+", str) is None:
        raise ValueError('Incorect expression.')
    a = sorted(list(set(re.findall("x\\d+", str))))
    lst = list(itertools.product([0, -1], repeat=len(a)))
    l = eval("lambda " + ",".join(a) + ":" + str)
    return ([bit2num(x) for x in lst if l(*x) == -1], a)


def minterm_print(minterms, a):
    ret = ""
    for term in minterms:
        ret += "("
        for i, t in enumerate(term):
            if t == '-':
                continue
            if i > 0 and ret[-1] != "(":
                ret += " & "
            if t == '1':
                ret += a[i]
            elif t == '0':
                ret += '~' + a[i]
        ret += ") | "
    return ret[:-3]


def test():
    l, a = parser("x3|x1^(~(x0&(~x2))&(x3|(x1^x3|(~x5))^x4))")
    print(l, a)
    terms = quine_mccluskey(l)
    print(terms)
    str = minterm_print(terms, a)
    print(str)
    l2, a2 = parser(str)
    print(l == l2)


if __name__ == "__main__":
    test()
