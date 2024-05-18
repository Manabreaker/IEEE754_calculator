"""v1.01 β"""
from flask import Flask, render_template, request
from math import pi, e, tau
import numpy as np
import struct

app = Flask(__name__)


def way_division(num1, num2, depth):
    # Длины битов и смещение для различных форматов с плавающей точкой
    depth_types = {
        '16-bit': [10, 5, 15],
        '32-bit': [23, 8, 127],
        '64-bit': [52, 11, 1023],
        '128-bit': [112, 15, 16383]
    }

    steps = []
    # Получаем длины битов и смещение для заданного формата
    mant_l, exp_l, bias = depth_types[depth]

    # Извлекаем знак, порядок и мантиссу первого числа
    sign1 = int(num1[0], 2)
    exp1 = int(num1[1:exp_l + 1], 2)
    mant1 = int('1' + num1[exp_l + 1:], 2) if exp1 + bias != 0 else int(num1[exp_l + 1:], 2)
    bin_exp1 = bin(exp1)[2:]
    bin_mant1 = bin(mant1)[2:]
    exp1 = int(num1[1:exp_l + 1], 2) - bias
    bin_mant2 = num2[1 + exp_l:]
    bin_mant1 = num1[1 + exp_l:]

    steps.append(
        f"Первое число: знак '{sign1}', экспонента {bin_exp1} (десятичное значение экспоненты: {int(bin_exp1, 2)}), мантисса {bin(mant1)[2:]} (десятичное значение мантиссы: {mant1}).\n")

    # Извлекаем знак, порядок и мантиссу второго числа
    sign2 = int(num2[0], 2)
    exp2 = int(num2[1:exp_l + 1], 2)
    mant2 = int('1' + num2[exp_l + 1:], 2) if exp2 + bias != 0 else int(num2[exp_l + 1:], 2)

    bin_exp2 = bin(exp2)[2:]
    exp2 = int(num2[1:exp_l + 1], 2) - bias
    steps.append(
        f"Второе число: знак '{sign2}', экспонента {bin_exp2} (десятичное значение экспоненты: {int(bin_exp2, 2)}), мантисса {bin(mant2)[2:]} (десятичное значение мантиссы: {mant2}).\n")

    # Добавляем шаг 1.1: проверка является ли первое число специальным случаем
    if bin_exp1 == '1' * exp_l and bin_mant1 == '0' * (mant_l):
        num1 = 'inf' if sign1 == 0 else '-inf'
        steps.append(f"Первое число является {'+' if sign1 == 0 else '-'}бесконечностью.\n")
    elif bin_exp1 == '1' * exp_l and bin_mant1.count('1') != 0:
        num1 = 'NaN'
        steps.append(f"Первое число является NaN.\n")

    # Добавляем шаг 1.1: проверка является ли второе число специальным случаем
    if bin_exp2 == '1' * exp_l and bin_mant2 == '0' * (mant_l):
        num2 = 'inf' if sign2 == 0 else '-inf'
        steps.append(f"Второе число является {'+' if sign2 == 0 else '-'}бесконечностью.\n")
    elif bin_exp2 == '1' * exp_l and bin_mant2.count('1') != 0:
        num2 = 'NaN'
        steps.append(f"Второе число является NaN.\n")

    # Рассчитываем десятичные порядки и определяем знак результата
    result_sign = sign1 ^ sign2

    if num1 == 'NaN' or num2 == 'NaN':
        steps.append('При любых операциях с NaN результатом всегда будет NaN.\n')
        result = 'NaN'
        return result, steps

    if num1 == 'inf' and num2 != '-inf':
        steps.append(
            f"При умножении любого числа на +inf и любое другое число его знак сохраняется, а модуль ответа становится равен inf.\n")
        steps.append(
            f"Окончательный результат: знак {result_sign}, экспонента {'1' * exp_l}, мантисса {'0' * mant_l}.\n")
        result = str(result_sign) + '1' * exp_l + '0' * mant_l
        return result, steps
    elif num2 == 'inf' and num1 != '-inf':
        steps.append(
            f"При умножении любого числа на +inf и любое другое число его знак сохраняется, а модуль ответа становится равен inf.\n")
        steps.append(
            f"Окончательный результат: знак {result_sign}, экспонента {'1' * exp_l}, мантисса {'0' * mant_l}.\n")
        result = str(result_sign) + '1' * exp_l + '0' * mant_l
        return result, steps
    elif num1 != 'NaN' and num2 == '-inf':
        steps.append(
            f"При умножении -inf на любое число его знак меняется на противополеженный, а модуль ответа становится равен inf.\n")
        steps.append(f"Окончательный результат: {'+' if result_sign == 0 else '-'}inf.\n")
        return str(result_sign) + '1' * exp_l + '0' * mant_l, steps
    elif num1 == '-inf' and num2 != 'NaN':
        steps.append(
            f"При умножении -inf на любое число его знак меняется на противополеженный, а модуль ответа становится равен inf.\n")
        steps.append(f"Окончательный результат: {'+' if result_sign == 0 else '-'}inf.\n")
        return str(result_sign) + '1' * exp_l + '0' * mant_l, steps
    elif num2 == '-inf' and num1 != 'inf':
        steps.append(
            f"В тех случаях когда в сложении участвуют -inf и любое другое число ≠ +inf, всегда получается -inf.\n")
        steps.append(f"Окончательный результат: знак 1, экспонента {'1' * exp_l}, мантисса {'0' * mant_l}.\n")
        result = '1' + '1' * exp_l + '0' * mant_l
        return result, steps

    steps.append(f"Определяем знак с помощью оператора XOR: {sign1} XOR {sign2} = {result_sign} \n")

    # Умножаем мантиссы и складываем порядки
    result_mant = mant1 // mant2

    result_exp = exp1 - exp2 + bias
    steps.append(f"Целочисленное деление мантисс: {bin(mant1)[2:]} // {bin(mant2)[2:]} = {bin(result_mant)[2:]}\n")
    steps.append(
        f"Вычитание экспонент: {bin_exp1} - {bin_exp2} + смещение ({bin(bias)[2:]}) = {bin(result_exp)[2:]}\n")
    # Обрабатываем случаи переполнения и потери значимости для порядка
    if result_exp >= (2 ** exp_l) - 1:
        result_exp = (2 ** exp_l) - 1
        result_mant = (1 << mant_l) - 1
        steps.append("Переполнение: экспонента и мантисса установлены на максимальные значения.\n")
    elif result_exp < 1:
        result_exp = 0
        result_mant = 0
        steps.append("Потеря значимости: экспонента и мантисса установлены на нули.\n")

    # Нормализация: мантисса может превысить размер, учитывая дополнительный бит
    while result_mant >= (1 << (2 * mant_l + 1)):
        result_exp += 1
        result_mant >>= 1
        steps.append(
            f"Нормализация: мантисса {result_mant} слишком велика, уменьшаем ее наполовину и увеличиваем экспоненту на 1. Новая мантисса: {result_mant}, новая экспонента: {result_exp}.\n")

    # Форматируем результат в двоичную строку
    final_exp = bin(result_exp)[2:].zfill(exp_l)
    final_mant = bin(result_mant)[2:mant_l].zfill(mant_l)[3:]
    final_mant += '0' * (mant_l - len(final_mant))
    result = str(result_sign) + str(final_exp) + str(final_mant)
    steps.append(f"Окончательный результат: знак {result_sign}, экспонента {final_exp}, мантисса {final_mant}.\n")
    return result, steps


def way_multiplication(num1, num2, depth):
    # Длины битов и смещения для различных форматов с плавающей точкой
    depth_types = {
        '16-bit': [10, 5, 15],
        '32-bit': [23, 8, 127],
        '64-bit': [52, 11, 1023],
        '128-bit': [112, 15, 16383]
    }

    steps = []
    # Получаем длины битов и смещение для заданного формата
    mant_l, exp_l, bias = depth_types[depth]

    # Извлекаем знак, порядок и мантиссу первого числа
    sign1 = int(num1[0], 2)
    exp1 = int(num1[1:exp_l + 1], 2)
    mant1 = int('1' + num1[exp_l + 1:], 2) if exp1 + bias != 0 else int(num1[exp_l + 1:], 2)
    bin_exp1 = bin(exp1)[2:]
    bin_mant1 = bin(mant1)[2:]
    exp1 = int(num1[1:exp_l + 1], 2) - bias
    bin_mant2 = num2[1 + exp_l:]
    bin_mant1 = num1[1 + exp_l:]

    steps.append(f"Первое число: знак '{sign1}', экспонента {bin_exp1} (десятичное значение экспоненты: {int(bin_exp1, 2)}), мантисса {bin_mant1} (десятичное значение мантиссы: {mant1}).\n")

    # Извлекаем знак, порядок и мантиссу второго числа
    sign2 = int(num2[0], 2)
    exp2 = int(num2[1:exp_l + 1], 2)
    mant2 = int('1' + num2[exp_l + 1:], 2) if exp2 + bias != 0 else int(num2[exp_l + 1:], 2)

    bin_exp2 = bin(exp2)[2:]
    exp2 = int(num2[1:exp_l + 1], 2) - bias
    steps.append(f"Второе число: знак '{sign2}', экспонента {bin_exp2} (десятичное значение экспоненты: {int(bin_exp2, 2)}), мантисса {bin_mant2} (десятичное значение мантиссы: {mant2}).\n")

    # Добавляем шаг 1.1: проверка является ли первое число специальным случаем
    if bin_exp1 == '1' * exp_l and bin_mant1 == '0' * (mant_l):
        num1 = 'inf' if sign1 == 0 else '-inf'
        steps.append(f"Первое число является {'+' if sign1 == 0 else '-'}бесконечностью.\n")
    elif bin_exp1 == '1' * exp_l and bin_mant1.count('1') != 0:
        num1 = 'NaN'
        steps.append(f"Первое число является NaN.\n")

    # Добавляем шаг 1.1: проверка является ли второе число специальным случаем
    if bin_exp2 == '1' * exp_l and bin_mant2 == '0' * (mant_l):
        num2 = 'inf' if sign2 == 0 else '-inf'
        steps.append(f"Второе число является {'+' if sign2 == 0 else '-'}бесконечностью.\n")
    elif bin_exp2 == '1' * exp_l and bin_mant2.count('1') != 0:
        num2 = 'NaN'
        steps.append(f"Второе число является NaN.\n")

    # Рассчитываем десятичные порядки и определяем знак результата
    result_sign = sign1 ^ sign2

    if num1 == 'NaN' or num2 == 'NaN':
        steps.append('При любых операциях с NaN результатом всегда будет NaN.\n')
        result = 'NaN'
        return result, steps

    if num1 == 'inf' and num2 != '-inf':
        steps.append(f"При умножении любого числа на +inf и любое другое число его знак сохраняется, а модуль ответа становится равен inf.\n")
        steps.append(f"Окончательный результат: знак {result_sign}, экспонента {'1' * exp_l}, мантисса {'0' * mant_l}.\n")
        result = str(result_sign) + '1' * exp_l + '0' * mant_l
        return result, steps
    elif num2 == 'inf' and num1 != '-inf':
        steps.append(f"При умножении любого числа на +inf и любое другое число его знак сохраняется, а модуль ответа становится равен inf.\n")
        steps.append(f"Окончательный результат: знак {result_sign}, экспонента {'1' * exp_l}, мантисса {'0' * mant_l}.\n")
        result = str(result_sign) + '1' * exp_l + '0' * mant_l
        return result, steps
    elif num1 != 'NaN' and num2 == '-inf':
        steps.append(f"При умножении -inf на любое число его знак меняется на противополеженный, а модуль ответа становится равен inf.\n")
        steps.append(f"Окончательный результат: {'+' if result_sign == 0 else '-'}inf.\n")
        return str(result_sign) + '1' * exp_l + '0' * mant_l, steps
    elif num1 == '-inf' and num2 != 'NaN':
        steps.append(f"При умножении -inf на любое число его знак меняется на противополеженный, а модуль ответа становится равен inf.\n")
        steps.append(f"Окончательный результат: {'+' if result_sign == 0 else '-'}inf.\n")
        return str(result_sign) + '1' * exp_l + '0' * mant_l, steps
    elif num2 == '-inf' and num1 != 'inf':
        steps.append(f"В тех случаях когда в сложении участвуют -inf и любое другое число ≠ +inf, всегда получается -inf.\n")
        steps.append(f"Окончательный результат: знак 1, экспонента {'1' * exp_l}, мантисса {'0' * mant_l}.\n")
        result = '1' + '1' * exp_l + '0' * mant_l
        return result, steps

    steps.append(f"Определяем знак с помощью оператора XOR: {sign1} XOR {sign2} = {result_sign} \n")

    # Умножаем мантиссы и складываем порядки
    result_mant = mant1 * mant2
    result_exp = exp1 + exp2 + bias
    steps.append(f"Умножение мантисс: {bin(mant1)[2:]} * {bin(mant2)[2:]} = {bin(result_mant)[2:]}\n")
    steps.append(f"Сложение экспонент: {bin_exp1} + {bin_exp2} + смещение ({bin(bias)[2:]}) = {bin(result_exp)[2:]}\n")
    # Обрабатываем случаи переполнения и потери значимости для порядка
    if result_exp >= (2 ** exp_l) - 1:
        result_exp = (2 ** exp_l) - 1
        result_mant = (1 << mant_l) - 1
        steps.append("Переполнение: экспонента и мантисса установлены на максимальные значения.\n")
    elif result_exp < 1:
        result_exp = 0
        result_mant = 0
        steps.append("Потеря значимости: экспонента и мантисса установлены на нули.\n")

    # Нормализация: мантисса может превысить размер, учитывая дополнительный бит
    while result_mant >= (1 << (2 * mant_l + 1)):
        result_exp += 1
        result_mant >>= 1
        steps.append(f"Нормализация: мантисса {result_mant} слишком велика, уменьшаем ее наполовину и увеличиваем экспоненту на 1. Новая мантисса: {result_mant}, новая экспонента: {result_exp}.\n")


    # Форматируем результат в двоичную строку
    final_exp = bin(result_exp)[2:].zfill(exp_l)
    final_mant = bin(result_mant)[2:mant_l].zfill(mant_l)[3:]
    final_mant += '0' * (mant_l - len(final_mant))
    result = str(result_sign) + str(final_exp) + str(final_mant)
    steps.append(f"Окончательный результат: знак {result_sign}, экспонента {final_exp}, мантисса {final_mant}.\n")
    return result, steps


def way(num1, num2, depth):
    # Таблица с данными о длине мантиссы, экспоненты и смещении для разных глубин
    depth_types = {
        '16-bit': [11, 5, 15],
        '32-bit': [24, 8, 127],
        '64-bit': [53, 11, 1023],
        '128-bit': [113, 15, 16383]
    }

    # Получаем длину мантиссы, экспоненты и смещение для заданной глубины
    mant_l, exp_l, shift = depth_types[depth]

    # Извлекаем знак, экспоненту и мантиссу из первого числа
    sign1 = num1[0]
    exp1 = num1[1:exp_l + 1]
    mant1 = num1[exp_l + 1:]

    # Извлекаем знак, экспоненту и мантиссу из второго числа
    sign2 = num2[0]
    exp2 = num2[1:exp_l + 1]
    mant2 = num2[exp_l + 1:]

    dec_exp1 = int(exp1, 2)
    dec_exp2 = int(exp2, 2)

    int_mant1 = int(mant1, 2)
    int_mant2 = int(mant2, 2)

    # Создаем список для хранения шагов
    steps = []

    # Добавляем шаг 1: разбор входных данных
    steps.append(f"Первое число: знак '{sign1}', экспонента {exp1} (десятичное значение экспоненты: {dec_exp1}), мантисса {mant1} (десятичное значение мантиссы: {int_mant1}).\n")
    steps.append(f"Второе число: знак '{sign2}', экспонента {exp2} (десятичное значение экспоненты: {dec_exp2}), мантисса {mant2} (десятичное значение мантиссы: {int_mant2}).\n")


    # Добавляем шаг 1.1: проверка является ли первое число специальным случаем
    if exp1 == '1' * exp_l and mant1 == '0' * (mant_l - 1):
        num1 = 'inf' if sign1 == '0' else '-inf'
        steps.append(f"Первое число является {'+' if sign1 == '0' else '-'}бесконечностью.\n")
    elif exp1 == '1' * exp_l and mant1.count('1') != 0:
        num1 = 'NaN'
        steps.append(f"Первое число является NaN.\n")

    # Добавляем шаг 1.1: проверка является ли второе число специальным случаем
    if exp2 == '1' * exp_l and mant2 == '0' * (mant_l - 1):
        num2 = 'inf' if sign2 == '0' else '-inf'
        steps.append(f"Второе число является {'+' if sign2 == '0' else '-'}бесконечностью.\n")
    elif exp2 == '1' * exp_l and mant2.count('1') != 0:
        num2 = 'NaN'
        steps.append(f"Второе число является NaN.\n")

    if num1 == 'NaN' or num2 == 'NaN':
        steps.append('При любых операциях с NaN результатом всегда будет NaN.\n')
        result = 'NaN'
        return result, steps

    if num1 == 'inf' and num2 != '-inf':
        steps.append(f"В тех случаях когда в сложении участвуют +inf и любое другое число ≠ -inf, всегда получается +inf.\n")
        steps.append(f"Окончательный результат: знак 0, экспонента {'1' * exp_l}, мантисса {'0' * mant_l}.\n")
        result = '0' + '1' * exp_l + '0' * mant_l
        return result, steps
    elif num2 == 'inf' and num1 != '-inf':
        steps.append(f"В тех случаях когда в сложении участвуют +inf и любое другое число ≠ -inf, всегда получается +inf.\n")
        steps.append(f"Окончательный результат: знак 0, экспонента {'1' * exp_l}, мантисса {'0' * mant_l}.\n")
        result = '0' + '1' * exp_l + '0' * mant_l
        return result, steps
    elif num1 == 'inf' and num2 == '-inf':
        steps.append(f"В тех случаях когда в сложении участвуют +inf и -inf, всегда получается NaN.\n")
        steps.append(f"Окончательный результат: NaN.\n")
        return 'NaN', steps
    elif num1 == '-inf' and num2 == 'inf':
        steps.append(f"В тех случаях когда в сложении участвуют +inf и -inf, всегда получается NaN.\n")
        steps.append(f"Окончательный результат: NaN.\n")
        return 'NaN', steps
    elif num1 == '-inf' and num2 != 'inf':
        steps.append(f"В тех случаях когда в сложении участвуют -inf и любое другое число ≠ +inf, всегда получается -inf.\n")
        steps.append(f"Окончательный результат: знак 1, экспонента {'1' * exp_l}, мантисса {'0' * mant_l}.\n")
        result = '1' + '1' * exp_l + '0' * mant_l
        return result, steps
    elif num2 == '-inf' and num1 != 'inf':
        steps.append(f"В тех случаях когда в сложении участвуют -inf и любое другое число ≠ +inf, всегда получается -inf.\n")
        steps.append(f"Окончательный результат: знак 1, экспонента {'1' * exp_l}, мантисса {'0' * mant_l}.\n")
        result = '1' + '1' * exp_l + '0' * mant_l
        return result, steps

    mant1 = '1' + num1[exp_l + 1:]  # Добавляем 1 перед мантиссой для нормализации
    mant2 = '1' + num2[exp_l + 1:]  # Добавляем 1 перед мантиссой для нормализации
    # Конвертируем бинарные экспоненты в целые числа и вычитаем смещение
    dec_exp1 = int(exp1, 2) - shift
    dec_exp2 = int(exp2, 2) - shift

    # Конвертируем мантиссы в целые числа
    int_mant1 = int(mant1, 2)
    int_mant2 = int(mant2, 2)

    # Добавляем шаг 2: сравнение экспонент и выравнивание мантисс
    if dec_exp1 > dec_exp2:
        # Выравниваем мантиссу второго числа
        int_mant2 >>= (dec_exp1 - dec_exp2)
        dec_exp2 = dec_exp1
        steps.append(f"Экспонента первого числа больше, выравниваем второе число, сдвигая мантиссу второго числа на {abs(dec_exp1 - dec_exp2)} позиции вправо.\n")
    elif dec_exp1 < dec_exp2:
        # Выравниваем мантиссу первого числа
        int_mant1 >>= (dec_exp2 - dec_exp1)
        dec_exp1 = dec_exp2
        steps.append(f"Экспонента второго числа больше, выравниваем первое число, сдвигая мантиссу первого числа на {abs(dec_exp2 - dec_exp1)} позиции вправо.\n")
    else:
        # Экспоненты равны, сдвиг мантисс не требуется
        steps.append("Экспоненты равны, сдвиг мантисс не требуется.\n")

    # Добавляем шаг 3: проверка знаков и выполнение операции
    if sign1 == sign2:
        # Знаки чисел равны, выполняем сложение мантисс
        result_mant = int_mant1 + int_mant2
        result_sign = sign1
        steps.append(f"Знаки одинаковые, складываем мантиссы: {bin(int_mant1)[2:]} + {bin(int_mant2)[2:]} = {bin(result_mant)[2:]}\n")
    else:
        # Знаки чисел разные
        if int_mant1 >= int_mant2:
            # Если первое число больше или равно второму по модулю, выполняем вычитание
            result_mant = int_mant1 - int_mant2
            result_sign = sign1  # Знак первого числа
            steps.append(f"Первое число больше или равно по модулю, вычитаем мантиссы: {bin(int_mant1)[2:]} - {bin(int_mant2)[2:]} = {bin(result_mant)[2:]}\n")
        else:
            # Если второе число больше по модулю, выполняем вычитание
            result_mant = int_mant2 - int_mant1
            result_sign = sign2  # Знак второго числа
            steps.append(f"Второе число больше по модулю, вычитаем мантиссы: {bin(int_mant2)[2:]} - {bin(int_mant1)[2:]} = {bin(result_mant)[2:]}\n")

    # Добавляем шаг 4: нормализация мантиссы
    while result_mant >= (1 << mant_l):  # Переполнение
        result_mant >>= 1
        dec_exp1 += 1
        steps.append(f"Мантисса слишком большая, уменьшаем ее вдвое и увеличиваем экспоненту на 1. Новая мантисса: {result_mant}, новая экспонента: {dec_exp1}.\n")
    else:
        steps.append("Нормализация мантиссы не требуется, её размер соответствует требованиям.\n")

    # Добавляем проверку для обработки равных мантисс с разными знаками
    if result_mant == 0:
        # Если мантисса равна нулю, вернуть результат равным нулю
        final_exp = '0' * exp_l
        final_mant = '0' * (mant_l - 1)
        result = result_sign + final_exp + final_mant
        steps.append("Мантисса равна нулю. Результат равен нулю.\n")
        return result, steps

    while result_mant < (1 << (mant_l - 1)):  # Недополнение
        result_mant <<= 1
        dec_exp1 -= 1
        steps.append(f"Мантисса слишком маленькая, удваиваем ее и уменьшаем экспоненту на 1. Новая мантисса: {result_mant}, новая экспонента: {dec_exp1}.\n")

    # Добавляем шаг 5: подготовка окончательного результата
    final_exp = bin(dec_exp1 + shift)[2:].zfill(exp_l)
    final_mant = bin(result_mant)[3:].zfill(mant_l - 1)
    result = result_sign + final_exp + final_mant
    steps.append(f"Окончательный результат: знак {result_sign}, экспонента {final_exp}, мантисса {final_mant}.\n")

    return result, steps

def half_to_binary(num):
    """Конвертирует число с плавающей запятой (16-битный формат) в его двоичное представление (в формате IEEE 754)"""
    try:
        num = struct.unpack('H', struct.pack('e', np.float16(num)))[0]
        num = str(format(num, 'b').zfill(16))
        sign = num[0]
        exponent = num[1:6]
        fraction = num[6:]
        return sign, exponent, fraction
    except OverflowError:
        return "Error", "Error", "Error"


def float_to_binary(num):
    """Конвертирует число с плавающей запятой (32-битный формат) в его двоичное представление (в формате IEEE 754)"""
    try:
        b = ''.join(f'{c:08b}' for c in struct.pack('!f', num))
        sign = b[0]
        exponent = b[1:9]
        fraction = b[9:]
        return sign, exponent, fraction
    except OverflowError:
        return "Error", "Error", "Error"


def double_to_binary(num):
    """Конвертирует число с плавающей запятой (64-битный формат) в его двоичное представление (в формате IEEE 754)"""
    try:
        b = ''.join(f'{c:08b}' for c in struct.pack('!d', num))
        sign = b[0]
        exponent = b[1:12]
        fraction = b[12:]
        return sign, exponent, fraction
    except OverflowError:
        return "Error", "Error", "Error"


def quad_to_binary(num):
    """Конвертирует число с плавающей запятой (128-битный формат) в его двоичное представление (в формате IEEE 754)"""
    # Обработка нуля
    if num == 0.0:
        return '0', '0' * 15, '0' * 112

    # Получение знака
    sign = '0' if num > 0 else '1'
    abs_num = abs(num)

    # Нормализация числа и вычисление экспоненты
    exponent1 = 0
    if abs_num >= 2:
        while abs_num >= 2:
            abs_num /= 2
            exponent1 += 1
    elif abs_num < 1:
        while abs_num < 1:
            abs_num *= 2
            exponent1 -= 1

    # Смещение экспоненты
    exponent1 += 16383
    if exponent1 >= 2**15 or exponent1 < 0:
        raise OverflowError("Число слишком большое или слишком маленькое для представления в 128-битном формате IEEE 754")

    exponent = format(exponent1, '015b')

    # Преобразование мантиссы
    abs_num -= 1  # Убираем ведущую 1
    mantissa = ''
    while len(mantissa) < 112:
        abs_num *= 2
        if abs_num >= 1:
            mantissa += '1'
            abs_num -= 1
        else:
            mantissa += '0'

    return sign, exponent, mantissa


def get_constant_from_string(constant_str):
    if constant_str == 'pi':
        return pi
    elif constant_str == 'exp':
        return e
    elif constant_str == 'tau':
        return tau
    elif constant_str == 'inf':
        return float('inf')
    elif constant_str == '-inf':
        return float('-inf')
    elif constant_str == 'NaN':
        return float('nan')
    else:
        raise ValueError(f"Недопустимая константа: {constant_str}")


def normalize(num):
    if num == float('inf') or num == float('-inf'):
        return "Нельзя нормализовать бесконечность"
    elif num == float('nan'):
        return "Нельзя нормализовать NaN"
    if not isinstance(num, (int, float)):
        return "Неверный тип данных"
    if num == 0:
        return "Нельзя нормализовать ноль"
    sign = "-" if num < 0 else ""
    num = abs(num)
    lennum = len(str(num))
    order = 0
    while num >= 10:
        num /= 10
        order += 1
    while num < 1:
        num *= 10
        order -= 1
    result = " = " + sign + str(round(num, lennum - str(num).count("."))) + " * 10^" + str(order)
    return result


@app.route('/')
def index():
    return render_template('calculator_detail.html')


@app.route('/calculate', methods=['POST'])
def calculate():
    if request.method == 'POST':
        num1 = request.form['num1']
        num2 = request.form['num2']
        fmt = request.form['format']

        Error = 0
        try:
            num1 = float(num1)
        except ValueError:
            try:
                num1 = get_constant_from_string(num1)
            except ValueError:
                Error = 1

        try:
            num2 = float(num2)
        except ValueError:
            try:
                num2 = get_constant_from_string(num2)
            except ValueError:
                if Error:
                    Error = 3
                else:
                    Error = 2

        if fmt == '16-bit':
            float_to_binary_func = half_to_binary
        elif fmt == '32-bit':
            float_to_binary_func = float_to_binary
        elif fmt == '64-bit':
            float_to_binary_func = double_to_binary
        elif fmt == '128-bit':
            float_to_binary_func = quad_to_binary

        if Error == 0:
            sign_num1, exponent_num1, fraction_num1 = float_to_binary_func(num1)
            sign_num2, exponent_num2, fraction_num2 = float_to_binary_func(num2)
        elif Error == 1:
            sign_num2, exponent_num2, fraction_num2 = float_to_binary_func(num2)
            return render_template('calculator_detail.html', operation="Error: Undefined constant",
                                   sign_num1="Error", exponent_num1="Error",
                                   fraction_num1="Error", sign_num2=sign_num2,
                                   exponent_num2=exponent_num2, fraction_num2=fraction_num2,
                                   sign_result="Error", exponent_result="Error",
                                   fraction_result="Error")
        elif Error == 2:
            sign_num1, exponent_num1, fraction_num1 = float_to_binary_func(num1)
            return render_template('calculator_detail.html', operation="Error: Undefined constant",
                                   sign_num1=sign_num1, exponent_num1=exponent_num1,
                                   fraction_num1=fraction_num1, sign_num2="Error",
                                   exponent_num2="Error", fraction_num2="Error",
                                   sign_result="Error", exponent_result="Error",
                                   fraction_result="Error")
        elif Error == 3:
            return render_template('calculator_detail.html', operation="Error: Undefined constant",
                                   sign_num1="Error", exponent_num1="Error",
                                   fraction_num1="Error", sign_num2="Error",
                                   exponent_num2="Error", fraction_num2="Error",
                                   sign_result="Error", exponent_result="Error",
                                   fraction_result="Error")

        operation = request.form['operation']

        if operation in ['add', 'subtract']:
            if operation == 'add':
                result, steps = way(sign_num1 + exponent_num1 + fraction_num1,
                                    sign_num2 + exponent_num2 + fraction_num2, fmt)
                operation_str = f"{num1} + {num2} = {num1 + num2} {normalize(num1 + num2)} = {result}(IEEE754)"
            elif operation == 'subtract':
                # Меняем знак второго числа для вычитания
                sign_num2 = '0' if sign_num2 == '1' else '1'
                result, steps = way(sign_num1 + exponent_num1 + fraction_num1,
                                    sign_num2 + exponent_num2 + fraction_num2, fmt)
                operation_str = f"{num1} - {num2} = {num1 - num2} {normalize(num1 - num2)} = {result}(IEEE754)"

            # Разделяем результат на знак, экспоненту и мантиссу
            sign_result = result[0]
            exponent_result = result[1:1 + len(exponent_num1)]
            fraction_result = result[1 + len(exponent_num1):]

            # Передаем список шагов вместе с другими данными в HTML-шаблон
            return render_template('calculator_detail.html', operation=operation_str,
                                   sign_num1=sign_num1, exponent_num1=exponent_num1,
                                   fraction_num1=fraction_num1, sign_num2=sign_num2,
                                   exponent_num2=exponent_num2, fraction_num2=fraction_num2,
                                   sign_result=sign_result, exponent_result=exponent_result,
                                   fraction_result=fraction_result, steps=steps)

        elif operation == 'multiply':
            result, steps = way_multiplication(sign_num1 + exponent_num1 + fraction_num1,
                                               sign_num2 + exponent_num2 + fraction_num2, fmt)
            operation_str = f"{num1} * {num2} = {num1 * num2} {normalize(num1 * num2)} = {result}(IEEE754)"

            # Разделяем результат на знак, экспоненту и мантиссу
            sign_result = result[0]
            exponent_result = result[1:1 + len(exponent_num1)]
            fraction_result = result[1 + len(exponent_num1):]

            # Передаем список шагов вместе с другими данными в HTML-шаблон
            return render_template('calculator_detail.html', operation=operation_str,
                                   sign_num1=sign_num1, exponent_num1=exponent_num1,
                                   fraction_num1=fraction_num1, sign_num2=sign_num2,
                                   exponent_num2=exponent_num2, fraction_num2=fraction_num2,
                                   sign_result=sign_result, exponent_result=exponent_result,
                                   fraction_result=fraction_result, steps=steps)

        elif operation == 'divide':
            if num2 != 0:
                result, steps = way_division(sign_num1 + exponent_num1 + fraction_num1,
                                                   sign_num2 + exponent_num2 + fraction_num2, fmt)
                operation_str = f"{num1} / {num2} = {num1 / num2} {normalize(num1 / num2)}"

                # Разделяем результат на знак, экспоненту и мантиссу
                sign_result = result[0]
                exponent_result = result[1:1 + len(exponent_num1)]
                fraction_result = result[1 + len(exponent_num1):]

                # Передаем список шагов вместе с другими данными в HTML-шаблон
                return render_template('calculator_detail.html', operation=operation_str,
                                       sign_num1=sign_num1, exponent_num1=exponent_num1,
                                       fraction_num1=fraction_num1, sign_num2=sign_num2,
                                       exponent_num2=exponent_num2, fraction_num2=fraction_num2,
                                       sign_result=sign_result, exponent_result=exponent_result,
                                       fraction_result=fraction_result, steps=steps)
            else:
                return render_template('calculator_detail.html', operation="Ошибка: на ноль делить нельзя",
                                       sign_num1=sign_num1, exponent_num1=exponent_num1,
                                       fraction_num1=fraction_num1, sign_num2=sign_num2,
                                       exponent_num2=exponent_num2, fraction_num2=fraction_num2,
                                       sign_result="Ошибка", exponent_result="Ошибка",
                                       fraction_result="Ошибка")



if __name__ == '__main__':
    app.run(debug=False)
