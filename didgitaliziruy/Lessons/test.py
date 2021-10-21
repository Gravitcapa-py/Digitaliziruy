def is_prime_number(num):
    if num == 1:
        return True
    else:
        for i in range(2, num):
            if num != i and num % i == 0:
                return False
    return True


def get_next_prime_number(number):
    for i in range(number + 1, number ** number):
        if is_prime_number(i):
            return i


print(get_next_prime_number(int(input())))

