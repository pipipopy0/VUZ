import logics as l
import parser as p
import time, asyncio
import json

# Не надо материться!


if __name__ == "__main__":
    id_input = input("Введи id: ")
    asyncio.run(l.check_id_directions(id=id_input))