from statistics import mean, stdev


# ПО контроль позиционных ограничений
def pos_control(a, b):
    def f(x):
        if a <= x or x <= b:
            return [x, True]
        else:
            return [x, False]

    return f


# КС - контроль стабильности величины X в кадре
def const_control(x):
    if max(x) == min(x):
        return [x, True]
    else:
        return [x, False]


# НИ - нормирование измерений
def normalize_measure(b1, b2):
    def f(x):
        return [(x - b1)/b2, True]
    return f


# РФ - расчет заданной функции от измеренных значений F(X1,X2,...).
def get_new_x(x):
    return [0.3 * x / (0.1 * x - 154), True]


# СД - расчет среднего значения и оценки дисперсии по повторным измерениям
def get_std(x):
    return [stdev(x), True]


def get_mean(x):
    return [mean(x), True]


def get_data_from_model(channels_list, plant):
    def f():
        measures = []
        errors = []
        for channel, prop in channels_list.items():
            measure = plant.measure(channel)
            if callable(prop):
                result = prop(measure)
                if  result[1]:
                    measure = result[0]
                else:
                    # Проброс сообщения об ошибке
                    error_message = 'Измерение с канала ' + str(channel) + \
                                    ' выходит из интервала позиционных ограничений'
                    if len(errors) > 0:
                        error_message = '\n' + error_message
                    errors.append(error_message)

            if type(prop) == list:
                added_measures = plant.get_measures_from_channel(channel, prop[1]-1)
                added_measures.append(measure)
                result = prop[0](added_measures)
                

                if channel == 77 or channel == 9:
                    if not result[1]:
                        # Сброс опроса
                        print("Hello!")
                        return []

                if channel == 6:
                    measure = result[0]
                    measures.append(measure)
                    added_measures = plant.get_measures_from_channel(channel, prop[1]-1)
                    added_measures.append(measure)
                    result = get_std(added_measures)
                    a = get_std(added_measures)
                    measure = result[0]


            if not (channel == 77 or channel == 9):
                measures.append(measure)

        return measures, errors
    return f

channels = {
    1: '',
    2: normalize_measure(730, 70),
    3: '',
    4: '',
    5: pos_control(-100, -10),
    6: [get_mean, 7],
    19: '',
    49: '',
    69: get_new_x,
    77: [const_control, 4],
    9: [const_control, 3]
}
