# -*- coding: utf-8 -*-


"""def overlap_time_unavailables(time, lista_unavailables):
    # Verifica se há coincidência de horário entre um horário (time)
    # e uma lista de horários (lista_unavailables). Retorna True caso haja
    # coincidência e False, caso contrário.
    t_start = int(time.get('start'))
    t_length = int(time.get('length'))
    t_end = t_start + t_length
    t_days = int(time.get('days'), 2)
    t_weeks = int(time.get('weeks'), 2)
    for u in lista_unavailables:
        u_start = int(u.get('start'))
        u_length = int(u.get('length'))
        u_end = u_start + u_length
        u_days = int(u.get('days'), 2)
        u_weeks = int(u.get('weeks'), 2)

        if Constraint.overlap(t_start, t_end, u_start, u_end, t_days, u_days, t_weeks, u_weeks):
            return True

    return False


def checa_disponibilidade_sala_horario(room, time):
    # Verifica se há disponibilidade de uma sala (room) em um determinado
    # horário (time). Retorna True caso haja disponibilidade, ou seja, a sala
    # pode ser reservada naquele horário. Retorna False, caso contrário.
    
    return not(overlap_time_unavailables(time, get_unavailables_by_room(room)))"""