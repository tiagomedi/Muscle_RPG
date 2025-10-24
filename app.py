#!/usr/bin/env python3
"""CLI pequeño para generar rutinas de hipertrofia usando el generador del proyecto."""
import argparse
from src import routine_builder


def main():
	p = argparse.ArgumentParser(description="Generador de rutinas hipertrofia (3/4/5 días)")
	p.add_argument("--days", type=int, choices=[3, 4, 5], default=4, help="Número de días por semana (3/4/5)")
	p.add_argument("--time", type=int, default=120, help="Tiempo por sesión en minutos (por defecto 120)")
	p.add_argument("--level", type=int, choices=[0,1,2,3,4], default=2, help="Nivel del usuario 0..4 (0 principiante, 2 intermedio)")
	args = p.parse_args()

	routine = routine_builder.generate_routine(args.days, time_per_session=args.time, user_level=args.level)
	routine_builder.pretty_print_routine(routine)

if __name__ == "__main__":
	main()
