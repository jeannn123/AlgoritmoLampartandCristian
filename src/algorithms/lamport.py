class LamportBakerySimulator:
    """Simula tickets concurrentes del algoritmo de la panaderia."""

    PROCESS_IDS = (1, 2, 3, 4, 5)

    def __init__(self, request_rounds: list[list[int]]) -> None:
        if not isinstance(request_rounds, list):
            raise TypeError("Las rondas de solicitud no son validas.")

        self.request_rounds = []
        requested_ids = []

        for request_round in request_rounds:
            if not isinstance(request_round, list) or not request_round:
                raise ValueError("Cada ronda debe incluir al menos un proceso.")

            process_ids = [int(process_id) for process_id in request_round]
            self.request_rounds.append(process_ids)
            requested_ids.extend(process_ids)

        invalid_ids = set(requested_ids).difference(self.PROCESS_IDS)
        if invalid_ids:
            raise ValueError("Solo existen los procesos P1, P2, P3, P4 y P5.")
        if len(requested_ids) != len(set(requested_ids)):
            raise ValueError("Un proceso no puede solicitar acceso dos veces.")

        self.requested_ids = set(requested_ids)

    def _assign_tickets(self) -> dict[int, int]:
        tickets = {process_id: 0 for process_id in self.PROCESS_IDS}

        for request_round in self.request_rounds:
            next_ticket = max(tickets.values()) + 1
            for process_id in request_round:
                tickets[process_id] = next_ticket

        return tickets

    def simulate(self) -> dict:
        tickets = self._assign_tickets()
        access_order = sorted(
            self.requested_ids,
            key=lambda process_id: (tickets[process_id], process_id),
        )

        processes = []
        for process_id in self.PROCESS_IDS:
            is_requesting = process_id in self.requested_ids
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

        rounds = [
            {
                "number": index,
                "ticket": tickets[request_round[0]],
                "processes": request_round,
            }
            for index, request_round in enumerate(self.request_rounds, start=1)
        ]

        return {
            "concept": (
                "Los procesos seleccionados en una misma ronda solicitan acceso al mismo "
                "tiempo y reciben el mismo ticket. El orden final compara (ticket, ID)."
            ),
            "processes": processes,
            "rounds": rounds,
            "access_order": access_order,
            "first_process": access_order[0] if access_order else None,
        }
