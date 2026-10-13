#!/usr/bin/env python3
"""Write IDs 1 and 2 on two Feetech STS3215 motors, one motor at a time."""

import argparse

from lerobot.motors import Motor, MotorNormMode
from lerobot.motors.feetech import FeetechMotorsBus


def set_id(port: str, target_id: int) -> None:
    name = f"motor_{target_id}"
    bus = FeetechMotorsBus(
        port=port,
        motors={name: Motor(target_id, "sts3215", MotorNormMode.DEGREES)},
    )
    bus.setup_motor(name)
    bus.disconnect(disable_torque=False)
    print(f"This motor is now ID {target_id}")


def main():
    parser = argparse.ArgumentParser(
        description="Set one connected STS3215 to ID 2, then another to ID 1."
    )
    parser.add_argument("--robot.port", type=str, required=True, help="Controller board COM port, for example COM7")
    args = parser.parse_args()
    port = getattr(args, "robot.port")

    print("Connect only one motor to the board. USB does not power the motor.")
    input("Plug in ONLY the motor that should become ID 2, then press Enter.")
    set_id(port, 2)

    input("Unplug it. Plug in ONLY the motor that should stay ID 1, then press Enter.")
    set_id(port, 1)

    print("Done. Mark the motors before connecting them on the same bus.")


if __name__ == "__main__":
    main()
