def chunkit(data: list or tuple, n=None):
    """
    Функция разбивает исходный массив на N частей (N == n).

    Arguments
    ---------
    data_list: list or tuple
        Массив, который будет разделен на n частей
    n: int
        Число подмассивов в возвращаемом массиве (default: 2)

    Returns
    -------
    list: разделенный на части список

    Example
    -------
    >>> l = [1, 2, 3, 4, 5, 6, 7, 8]
    >>> a = chunkit(l)
    >>> print(a)
    [[1, 2, 3, 4], [5, 6, 7, 8]]
    >>> b = chunkit(l, n=4)
    >>> print(b)
    [[1, 2], [3, 4], [5, 6], [7, 8]]
    """
    new_data = []
    if not n:
        n = 2
    avg = len(data) / n
    last = 0
    while last < len(data):
        new_data.append(data[int(last):int(last + avg)])
        last += avg
    return new_data


def read_data_cosmo(file_path: str):
    with open(file_path, 'r') as file:
        data = []
        for line in file:
            if line.split():
                if 'Setting' in line:
                    jobs_data = []
                    jobs_data.append(line)
                    data.append(jobs_data)
                elif 'job' not in line:
                    jobs_data.append(line)
                else:
                    pass
    return data

def parser():
    pass


def setting_parser():
    pass


def main():
    import doctest
    print(doctest.testmod())


if __name__ == '__main__':
    main()
