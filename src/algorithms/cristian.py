from datetime import datetime, timedelta


class CristianSimulator:
    """Sincroniza varios clientes con un servidor horario."""

    TIME_FORMAT = "%H:%M:%S"
    MAX_CLIENTS = 5

    def __init__(self, server_time: str, clients: list[dict]) -> None:
        self.server_time = self._parse_time(server_time, "servidor")

        if not isinstance(clients, list) or not clients:
            raise ValueError("Debe existir al menos un cliente.")
        if len(clients) > self.MAX_CLIENTS:
            raise ValueError("Se permiten como maximo cinco clientes.")

        self.clients = clients

    def _parse_time(self, value: str, owner: str) -> datetime:
        try:
            return datetime.strptime(str(value), self.TIME_FORMAT)
        except ValueError as error:
            raise ValueError(f"La hora de {owner} debe usar el formato HH:MM:SS.") from error

    @staticmethod
    def _format_time(value: datetime) -> str:
        return value.strftime("%H:%M:%S.%f")[:-3]

    @staticmethod
    def _clock_difference_ms(target: datetime, current: datetime) -> float:
        difference_ms = (target - current).total_seconds() * 1000
        day_ms = 24 * 60 * 60 * 1000

        # Escoge el ajuste mas corto cuando los relojes estan a lados
        # distintos de la medianoche.
        if difference_ms > day_ms / 2:
            difference_ms -= day_ms
        elif difference_ms < -day_ms / 2:
            difference_ms += day_ms
        return difference_ms

    def simulate(self) -> dict:
        synchronized_clients = []

        for index, client in enumerate(self.clients, start=1):
            client_id = int(client.get("id", index))
            initial_time = self._parse_time(client.get("initial_time", ""), f"C{client_id}")
            round_trip_ms = max(20, min(int(client.get("round_trip_ms", 200)), 5000))
            estimated_one_way_ms = round_trip_ms / 2

            # El servidor marca su respuesta y el cliente suma media vuelta de red
            # para estimar la hora al momento en que recibe el mensaje.
            synchronized_time = self.server_time + timedelta(milliseconds=estimated_one_way_ms)
            difference_ms = self._clock_difference_ms(synchronized_time, initial_time)

            synchronized_clients.append(
                {
                    "id": client_id,
                    "initial_time": self._format_time(initial_time),
                    "server_time": self._format_time(self.server_time),
                    "round_trip_ms": round_trip_ms,
                    "estimated_one_way_ms": estimated_one_way_ms,
                    "synchronized_time": self._format_time(synchronized_time),
                    "adjustment_ms": difference_ms,
                    "result": "Sincronizado correctamente",
                }
            )

        return {
            "concept": (
                "Cada cliente pide la hora al servidor. Al recibirla, suma la mitad "
                "del tiempo de ida y vuelta (RTT/2) para compensar la demora de la red."
            ),
            "server_time": self._format_time(self.server_time),
            "clients": synchronized_clients,
            "all_synchronized": True,
        }
