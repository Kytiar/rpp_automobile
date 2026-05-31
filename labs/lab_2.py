import numpy as np

def generate(n, m):
    return np.random.randint(1, 10, size=(n, m))

def calculate(matrix):
    total_sum = np.sum(matrix)
    column_sums = np.sum(matrix, axis=0)
    proportions = column_sums / total_sum
    return total_sum, column_sums, proportions

def create(matrix, proportions):
    proportions = proportions.astype(float)
    result = np.vstack((matrix, proportions))
    return result

def save(matrix, total_sum, column_sums, proportions):
    with open('results.txt', 'w') as f:
        f.write('Sum2: {}\n'.format(total_sum))
        f.write('Sum row: {}\n'.format(column_sums))
        np.savetxt(f, matrix, fmt='%f')

def input_matrix(n, m):
    matrix = []
    for i in range(n):
        while True:
            row = input('Строка {}: '.format(i+1))
            try:
                row = [int(x) for x in row.split()]
                if len(row) != m:
                    print('Неправильное количество элементов в строке. Пожалуйста, введите строку еще раз.')
                else:
                    matrix.append(row)
                    break
            except ValueError:
                print('Неправильный ввод. Пожалуйста, введите строку еще раз.')
    return np.array(matrix)

def main():
    print('Ввод матрицы вручную (введите \'1\') или сгенерировать автоматически (введите \'2\')?')
    choice = input()
    if choice == '1':
        n = int(input('Введите количество строк матрицы: '))
        m = int(input('Введите количество столбцов матрицы: '))
        matrix = input_matrix(n, m)
    elif choice == '2':
        n = int(input('Введите количество строк матрицы: '))
        m = int(input('Введите количество столбцов матрицы: '))
        matrix = generate(n, m)
        print('Сгенерированная матрица:')
        print(matrix)
    else:
        print('Неправильный выбор. Выход из программы.')
        return

    total_sum, column_sums, proportions = calculate(matrix)
    result = create(matrix, proportions)
    save(result, total_sum, column_sums, proportions)
    print('Результаты сохранены в файл \'results.txt\'')

main()
