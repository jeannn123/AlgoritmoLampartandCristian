PROCESS_IDS = [1, 2, 3, 4, 5]


def simulate(request_rounds):
    tickets = {process_id: 0 for process_id in PROCESS_IDS}
    requested_ids = []
    normalized_rounds = []

    # Los procesos de una misma ronda reciben el mismo ticket.
    for request_round in request_rounds:
        if not request_round:
            raise ValueError("La ronda no puede estar vacia.")

        ticket = max(tickets.values()) + 1
        current_round = []

        for process_id in request_round:
            process_id = int(process_id)

            if process_id not in PROCESS_IDS:
                raise ValueError("El proceso no existe.")
            if process_id in requested_ids:
                raise ValueError("El proceso ya tiene un ticket.")

            tickets[process_id] = ticket
            requested_ids.append(process_id)
            current_round.append(process_id)

        normalized_rounds.append(current_round)

    def priority(process_id):
        return tickets[process_id], process_id

    access_order = sorted(requested_ids, key=priority)

    processes = []
    for process_id in PROCESS_IDS:
        is_requesting = process_id in requested_ids
        processes.append(
            {
                "id": process_id,
                "requesting": is_requesting,
                "ticket": tickets[process_id] if is_requesting else None,
                "queue_position": (
                    access_order.index(process_id) + 1 if is_requesting else None
                ),
                "status": "En espera" if is_requesting else "No solicito acceso",
            }
        )

    rounds = []
    for number, request_round in enumerate(normalized_rounds, start=1):
        rounds.append(
            {
                "number": number,
                "ticket": tickets[request_round[0]],
                "processes": request_round,
            }
        )

    return {
        "concept": (
            "Los procesos de una ronda reciben el mismo ticket. "
            "El orden final se calcula por (ticket, ID)."
        ),
        "processes": processes,
        "rounds": rounds,
        "access_order": access_order,
        "first_process": access_order[0] if access_order else None,
    }
