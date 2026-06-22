from datetime import datetime, timedelta


TIME_FORMAT = "%H:%M:%S"


def parse_time(value):
    return datetime.strptime(value, TIME_FORMAT)


def format_time(value):
    return value.strftime("%H:%M:%S.%f")[:-3]


def simulate(server_time_text, clients):
    server_time = parse_time(server_time_text)
    synchronized_clients = []

    for client in clients:
        client_id = int(client["id"])
        initial_time = parse_time(client["initial_time"])
        round_trip_ms = int(client["round_trip_ms"])

        # Cristian estima la demora de un trayecto usando RTT / 2.
        one_way_delay_ms = round_trip_ms / 2
        synchronized_time = server_time + timedelta(milliseconds=one_way_delay_ms)
        adjustment_ms = (synchronized_time - initial_time).total_seconds() * 1000

        synchronized_clients.append(
            {
                "id": client_id,
                "initial_time": format_time(initial_time),
                "server_time": format_time(server_time),
                "estimated_one_way_ms": one_way_delay_ms,
                "synchronized_time": format_time(synchronized_time),
                "adjustment_ms": adjustment_ms,
                "result": "Sincronizado correctamente",
            }
        )

    return {
        "concept": (
            "Cada cliente recibe la hora del servidor y suma RTT / 2 "
            "para compensar la demora de la red."
        ),
        "clients": synchronized_clients,
    }
