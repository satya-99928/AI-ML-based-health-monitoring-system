import time


def current_time():

    return time.strftime("%H:%M:%S")


def divider():

    print("-" * 50)


def banner():

    divider()

    print("AI/ML Patient Health Monitoring Robot")

    print(current_time())

    divider()


def clamp(value, minimum, maximum):

    return max(minimum, min(maximum, value))


def average(values):

    if not values:
        return 0

    return sum(values) / len(values)