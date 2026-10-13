# Kickstart: control the XLeRobot arm

English | [繁體中文](README_CN.md)

This guide gets one real XLeRobot arm moving from your keyboard, then shows the short path to a second arm and to the whole mobile robot.

It is a local beginner guide for this workspace. The hardware, scripts, and plugins live in the upstream project: [Vector-Wangel/XLeRobot](https://github.com/Vector-Wangel/XLeRobot). Official docs: [xlerobot.readthedocs.io](https://xlerobot.readthedocs.io/en/latest/).

Commands below were checked against the project in October 2026. This guide is for Windows. The XLeRobot examples default to Linux names such as `/dev/ttyACM0`. On Windows that same cable is a COM port, such as `COM5`, and every command below uses the COM name.

If you build, buy, or run an XLeRobot from that repo, you are fully responsible for any physical or mental harm it causes to you or to anyone else. That is the project's own disclaimer.

## What you are controlling

XLeRobot's arm is an [SO-101](https://huggingface.co/docs/lerobot/en/so101) follower arm. "Follower" means the computer tells the motors where to go. A separate leader arm (a matching arm you move by hand) is optional. Keyboard control does not need one.

Each arm has six Feetech STS3215 servos on one controller board. They share one cable, called the bus. Each motor has a numeric ID so the computer can talk to the right one.

| Motor ID | Name in code | What it does |
| --- | --- | --- |
| 1 | `shoulder_pan` | Turns the whole arm left and right |
| 2 | `shoulder_lift` | Raises and lowers the upper arm |
| 3 | `elbow_flex` | Bends the elbow |
| 4 | `wrist_flex` | Tilts the wrist up and down |
| 5 | `wrist_roll` | Twists the wrist |
| 6 | `gripper` | Opens and closes the fingers |

The keyboard scripts in `software/examples/` create an `SO100Follower`. In current LeRobot, `SO100Follower` and `SO101Follower` are the same robot class registered under two names. XLeRobot states those scripts run on SO-101 hardware as well as SO-100. Use them for this arm.

A single arm can lift roughly 600 g to 1 kg. Reach is about 40 cm. Keep the first experiments inside that.

## Safety before any command

Do these every time, including the first "just a small move" test.

- The USB cable carries data only. It does not power the motors. Plug in the motor power supply as well as USB.
- Match the supply to the motors printed on the servo. Use a 5 V supply for 7.4 V motors. Use a 12 V supply for 12 V motors. The wrong supply can destroy a motor.
- Clear the table. The first control script drives every joint toward zero for about three seconds as soon as it is ready.
- Keep one hand on the power plug. Pulling power is the stop that always works.
- When a script disconnects, it turns motor torque off. The arm can droop. Rest it on the table, or hold the forearm, before you quit.
- Tap keys. Do not hold them down on the first try. The control loop runs at 50 Hz, so a held key keeps adding motion.
- Stay under the payload. A heavy object in the gripper will stall the wrist.

`X` in the single-arm scripts asks the arm to ease back toward the pose it had at startup. `Esc` or Ctrl+C stops the program. If the motion looks wrong, pull power first and debug second.

## Words you will see

- **Terminal.** The text window where you type commands. On Windows, use the Miniforge Prompt that the installer creates, or PowerShell after Miniforge is on your PATH. The line that waits for you is the prompt.
- **Conda environment.** A private Python install named `lerobot`. You activate it in every new terminal before any command in this guide. If you skip that, Python will not see LeRobot.
- **Port.** The name Windows gives the USB connection. It looks like `COM5`. Device Manager lists these under **Ports (COM & LPT)**. Your number may be `COM3`, `COM4`, or another COM port. Use the number you find. The `COM5` in the examples is only a placeholder.
- **Calibration.** A saved file that maps each motor's raw reading onto a joint angle. The first run has to create it. Later runs reuse it when you answer `n`.
- **Joint control.** You nudge one motor at a time.
- **End-effector control.** You nudge the gripper's position in space. The script computes the shoulder and elbow angles. That computation is inverse kinematics.
- **P control.** The script does not snap to the new angle. Each moment it moves partway across the remaining error (half of it, because the gain is 0.5), so the motion eases in.

Click the terminal after you start a control script. The keyboard reader (`pynput`) only receives keys while that window is focused.

## 1. Install the software

You need Git and Miniforge (a Conda installer). LeRobot's install guide asks for Python 3.12.

- Git for Windows: [git-scm.com/download/win](https://git-scm.com/download/win)
- Miniforge: the Windows x86_64 installer on the [Miniforge releases](https://github.com/conda-forge/miniforge/releases) page

During the Miniforge install, leave the option that registers Conda enabled. Then open **Miniforge Prompt**.

### Turn on symlinks before you clone XLeRobot

XLeRobot's later plugins are folders of symlinks (shortcuts that point at the real code). Windows can create those if Developer Mode is on, or if Git is allowed to use symlinks. Set this once, before the clone:

```powershell
git config --global core.symlinks true
```

The first arm scripts do not need those plugins. The setting still has to be in place before `git clone`, because Git decides at clone time.

### Create the Python environment

```powershell
conda create -y -n lerobot python=3.12
conda activate lerobot
```

`conda activate lerobot` is required in every new terminal.

### Install LeRobot with the motor and keyboard extras

LeRobot is the library that speaks to the Feetech bus. Clone it and install the editable package with the extras this arm needs. `feetech` is the servo driver. `core_scripts` pulls in serial ports, the keyboard library, calibration, and the `lerobot-*` commands.

In PowerShell, square brackets are wildcards, so the quotes around the extras are required.

```powershell
cd $HOME
git clone https://github.com/huggingface/lerobot.git
cd lerobot
pip install -e ".[feetech,core_scripts]"
```

Check that the commands exist:

```powershell
lerobot-find-port --help
```

You should see a help message, not "command not found".

### Clone XLeRobot

```powershell
cd $HOME
git clone https://github.com/Vector-Wangel/XLeRobot.git
```

The arm demos are in `XLeRobot\software\examples`. Leave that clone as-is. You run the scripts from there; you do not copy them into the LeRobot repo.

Upstream install notes, including the mobile-base plugins: [Install LeRobot and XLeRobot plugins](https://xlerobot.readthedocs.io/en/latest/software/getting_started/install.html).

## 2. Find the USB port

Windows calls this connection a COM port. There is no `chmod` step, and there is no `/dev/ttyACM0`. Those names belong to Linux. On your PC the board is `COM5`, `COM6`, or whichever number Device Manager shows.

1. Plug the controller board into the PC with a data USB cable. A charge-only cable will show nothing.
2. Plug in the motor power supply. The USB cable carries data only.
3. With the `lerobot` environment active, run:

```powershell
lerobot-find-port
```

The program lists ports such as `COM3` and `COM5`, asks you to unplug the board, and then tells you which port disappeared. That name is your arm. Write it down.

You can do the same check in Device Manager:

1. Right-click the Start button and choose **Device Manager**.
2. Open **Ports (COM & LPT)**.
3. Plug the board in and see which COM port appears. Unplug it and that entry disappears.

A second control board gets its own COM number, for example `COM6`. Leave the first board plugged in, plug in the second, and note the new COM port.

If the board is listed but no motor answers, unplug the motor power supply and plug it back in. Then run `lerobot-find-port` again.

If you use a Waveshare bus-servo board, both jumpers on the board must sit on the USB channel, marked `B`. The jumpers are hardware. They are set the same way on Windows as on any other computer. If they are on the other channel, Windows will not see a COM port.

## 3. Give each motor an ID (once)

A new servo ships as ID 1. Six motors on one bus must be 1 through 6, or they talk over each other. This writes the ID into the motor, so you do it once per motor.

Do this **before** the motors are daisy-chained. Only one motor is connected to the board at a time.

```powershell
lerobot-setup-motors --robot.type=so101_follower --robot.port=COM5
```

Replace `COM5` with the COM port from the previous step.

The script asks for one motor at a time, in this order:

1. Gripper → ID 6
2. Wrist roll → ID 5
3. Wrist flex → ID 4
4. Elbow flex → ID 3
5. Shoulder lift → ID 2
6. Shoulder pan → ID 1

For each step: unplug every other motor, connect only the one it named, then press Enter. When it finishes, chain the motors (shoulder pan connects to the board, then shoulder lift, and so on out to the gripper).

Write the ID on each motor with a marker. A second arm gets its own board and its own IDs 1–6. Label the sets, for example `L1`–`L6` and `R1`–`R6`.

Official walkthrough with the same commands: [SO-101](https://huggingface.co/docs/lerobot/en/so101).

## 4. Calibrate, then move one joint at a time

Calibration records the middle of each joint and how far it can travel. The control script stores that and asks on later runs.

From the examples folder, with the arm powered and the terminal focused:

```powershell
conda activate lerobot
cd $HOME\XLeRobot\software\examples
python 0_so100_keyboard_joint_control.py --robot.port=COM5
```

What happens:

1. The script connects. If LeRobot starts a calibration because none is saved yet, follow it.
2. It asks `Do you want to recalibrate the robot? (y/n)`. Answer `y` the first time. Answer `n` later, unless you rebuilt the arm or moved a motor horn.
3. Put every joint in the **middle** of its travel, then press Enter.
4. Move **each** joint slowly through its **full** travel, one at a time: base rotation, shoulder, elbow, wrist tilt, wrist twist, gripper open and closed. Press Enter when the script says to stop recording.
5. The arm then eases toward zero for about three seconds. Keep the workspace clear.
6. The keyboard takes over.

| Keys | Joint | Effect of one tap |
| --- | --- | --- |
| `Q` / `A` | Shoulder pan | About −1° / +1° |
| `W` / `S` | Shoulder lift | About −1° / +1° |
| `E` / `D` | Elbow | About −1° / +1° |
| `R` / `F` | Wrist flex | About −1° / +1° |
| `T` / `G` | Wrist roll | About −1° / +1° |
| `Y` / `H` | Gripper | About −5 / +5 on a 0–100 scale |
| `X` | Exit | Ease back toward the startup pose, then quit |
| `Esc` | Exit | Stop the program |

Arm joints are in degrees. The gripper is 0 (one end of travel) to 100 (the other). The script clamps the gripper to that range.

Practice one joint until the direction makes sense, then the next. Shoulder and elbow will swing a long way from a single held key, so tap.

Upstream page for this demo: [SO100/SO101 arm examples](https://xlerobot.readthedocs.io/en/latest/software/getting_started/SO101.html).

## 5. Move the hand instead of each joint

When joint control feels predictable, switch to end-effector control. `W` `S` `E` `D` move the gripper in the arm's side plane. The script's inverse kinematics turns that point into shoulder and elbow angles, and it tilts the wrist to follow.

```powershell
python 1_so100_keyboard_ee_control.py --robot.port=COM5
```

Answer the calibration question the same way as before (`n` if you just calibrated). The arm again eases toward zero before the keys work.

The gripper starts near `x = 0.163` m and `y = 0.113` m, measured in the arm's own frame. Each tap of `W` `S` `E` `D` steps by 4 mm. If you ask for a point the arm cannot reach, the script pulls the target back to the edge of the workspace.

| Keys | What moves |
| --- | --- |
| `Q` / `A` | Shoulder pan, still one joint |
| `W` / `S` | Gripper X (forward / back in the arm plane) |
| `E` / `D` | Gripper Y (up / down in the arm plane) |
| `R` / `F` | Wrist pitch. This adds to the wrist angle on top of the follow behavior |
| `T` / `G` | Wrist roll |
| `Y` / `H` | Gripper |
| `X` | Ease back toward the startup pose, then quit |
| `Esc` | Stop the program |

## 6. Two arms

Each arm has its own controller board and its own USB port. Find both with `lerobot-find-port` (unplug one board when it asks, so you learn which port is which).

```powershell
python 2_dual_so100_keyboard_ee_control.py --arm1.port=COM5 --arm2.port=COM6
```

Pass the two COM ports you found, in either order, as long as each flag matches one board. Both arms ease toward zero at the start. Calibrate each one when asked.

The script prints this map. Arm 1 uses the digit row. Arm 2 uses the home row.

**Arm 1**

| Keys | What moves |
| --- | --- |
| `7` / `Y` | Shoulder pan |
| `8` / `U` | Gripper X |
| `9` / `I` | Gripper Y |
| `=` / `[` | Wrist pitch |
| `0` / `O` | Wrist roll |
| `-` / `P` | Gripper |

**Arm 2**

| Keys | What moves |
| --- | --- |
| `H` / `B` | Shoulder pan |
| `J` / `N` | Gripper X |
| `K` / `M` | Gripper Y |
| `,` / `.` | Wrist pitch |
| `;` / `L` | Wrist roll |
| `'` / `/` | Gripper |

`X` eases both arms back and quits. `Esc` stops the program.

## 7. The whole robot (base, head, and both arms)

Skip this until one arm is boring and reliable. These scripts expect the extra motors, and they will fail on a bare arm.

XLeRobot adds two controller boards beyond a single table arm:

- One board: one SO-101 arm (IDs 1–6) plus the head (IDs 7 and 8).
- The other board: the other SO-101 arm (IDs 1–6) plus the wheel base (IDs 7, 8, and 9).

LeRobot's `lerobot-setup-motors` only assigns the arm IDs 1–6. For head and wheel motors, XLeRobot uses [Bambot's servo page](https://bambot.org/feetech.js): connect one motor, choose that board's COM port in the browser, scan it, and rename it to 7, 8, or 9 as the assembly pictures show. Label those motors too (`L7`, `L8`, `R7`–`R9`).

A laptop on the cart is enough. A Raspberry Pi is optional.

Install the plugins only when you are ready for this step. From the XLeRobot clone, with `lerobot` active:

```powershell
pip install -e software\plugins\xlerobot_model
pip install -e software\plugins\lerobot_robot_xlerobot
```

`lerobot_robot_xlerobot` is the 3-omniwheel base. If you built the dual-wheel version, install `software\plugins\lerobot_robot_xlerobot_2wheels` and run `4_xlerobot_2wheels_teleop_keyboard.py` instead. The mecanum base has its own plugin, `lerobot_robot_xlerobot_mecanum`. If `pip install -e` cannot see the plugin folders, the clone was made without symlink support. Turn on Developer Mode, set `core.symlinks` as in section 1, delete the clone, and clone again.

Then, from `software\examples` (the script also accepts a run from the repo root if `examples` is on the path it prints):

```powershell
python 4_xlerobot_teleop_keyboard.py --robot.port1=COM5 --robot.port2=COM6
```

`--robot.port1` is the arm-plus-head board. `--robot.port2` is the arm-plus-base board (the same pairing the Lekiwi base uses). Swapping them produces an error like "need 9 motors, but 8 detected". Fix it by swapping the two port arguments.

This script also eases the arms toward zero when it starts.

**Left arm and head**

| Keys | What moves |
| --- | --- |
| `Q` / `E` | Shoulder pan |
| `W` / `S` | Hand X |
| `A` / `D` | Hand Y |
| `Z` / `X` | Wrist pitch |
| `R` / `F` | Wrist roll |
| `T` / `G` | Gripper |
| `<` / `>` | Head motor 1 (on a US keyboard, Shift+, and Shift+.) |
| `,` / `.` | Head motor 2 |
| `C` | Left arm back toward zero |
| `Y` | Left arm traces a small rectangle (it will move on its own until the shape finishes) |
| `?` | Head back toward zero (on a US keyboard, Shift+/) |

**Right arm** (number pad or the digit keys above the letters; num lock on if you use the pad)

| Keys | What moves |
| --- | --- |
| `7` / `9` | Shoulder pan |
| `8` / `2` | Hand X |
| `4` / `6` | Hand Y |
| `1` / `3` | Wrist pitch |
| `/` / `*` | Wrist roll |
| `+` / `-` | Gripper |
| `0` | Right arm back toward zero |
| `Y` (Shift+y) | Right arm traces a small rectangle |

**Base** (defaults in the robot config)

| Keys | What moves |
| --- | --- |
| `I` / `K` | Forward / back |
| `J` / `L` | Strafe left / right |
| `U` / `O` | Rotate |
| `N` / `M` | Speed up / down |
| `B` | Quit |

Give the wheels a clear floor before you press `I`. More teleop options (Xbox, Joy-Con, VR) are on the [teleop page](https://xlerobot.readthedocs.io/en/latest/software/getting_started/XLeRobot_teleop.html).

## 8. Command the arm from your own Python

The demos are a loop around two calls: read `get_observation()`, then `send_action()`. You can do the same in a short script.

Save this as `move_once.py` somewhere outside the example folder, with the `lerobot` environment active. Use your COM port. `id` is the calibration file name; keep the same string every time you connect this arm.

```python
from lerobot.robots.so_follower import SO100Follower, SO100FollowerConfig

# Use the COM port from Device Manager, for example "COM5".
robot = SO100Follower(SO100FollowerConfig(port="COM5", id="my_arm"))

robot.connect()
print(robot.get_observation())

# Arm joints are degrees. Gripper is 0 to 100.
# This only changes the base rotation. Other joints hold their current command
# once you include them. Start with a small angle near where the arm already is.
robot.send_action({"shoulder_pan.pos": 10.0})

robot.disconnect()
```

Run it:

```powershell
python move_once.py
```

`get_observation()` prints keys like `shoulder_pan.pos`, `shoulder_lift.pos`, `elbow_flex.pos`, `wrist_flex.pos`, `wrist_roll.pos`, and `gripper.pos`.

A real move should be a short loop, like the examples: read the current angle, step a fraction of the way to the target, `send_action`, sleep about 0.02 seconds, repeat. One large `send_action` can make the arm jump. The examples use a gain of 0.5 at 50 Hz for that reason.

`send_action` wants every joint you intend to hold. A dictionary with only `shoulder_pan.pos` leaves the other motors to the controller's last target. For a first test, that is fine if the arm is already resting and powered. For a program that runs a while, send all six `.pos` keys each cycle, copying the latest observation for any joint you are not moving.

The same pattern is how the keyboard scripts work. They change a target when a key arrives, then every cycle they send `current + 0.5 * (target - current)`.

## Troubleshooting

**`conda` or `lerobot-find-port` is not recognized.** Open Miniforge Prompt, or run `conda activate lerobot` in this terminal. A new terminal starts outside the environment.

**No COM port appears.** Use a data USB cable, set the Waveshare jumpers to `B`, and install the board's USB serial driver if Device Manager shows an unknown device. Close any other serial monitor that already has the port open.

**No motor is detected.** Power is a separate plug from USB. Unplug and replug the motor power, then try again. Only the 3-pin servo cable should go from the board to the motor during ID setup.

**Wrong number of motors, or "need 9 motors, but 8 detected".** IDs collide or the two full-robot ports are swapped. On a single arm you want exactly IDs 1–6. On the full robot, port 1 is arm plus head (8 motors) and port 2 is arm plus base (9 motors).

**`ModuleNotFoundError` for `lerobot.robots.so_follower...`.** The example scripts import internal files:

```python
from lerobot.robots.so_follower.so_follower import SO100Follower
from lerobot.robots.so_follower.config_so_follower import SO100FollowerConfig
```

The supported public import, which your own scripts should use, is:

```python
from lerobot.robots.so_follower import SO100Follower, SO100FollowerConfig
```

If the example's longer import fails after a LeRobot update, the public import above is the one to follow, and the example file's two import lines are what you edit.

**Keys do nothing.** Click the terminal window. On Windows, some security tools block the keyboard hook `pynput` uses; allow the Python process if the script connects and then ignores every key.

**The arm jumps or a joint runs the wrong way.** Calibration was skipped or a motor horn was moved after calibration. Run the script again and answer `y`. Put every joint in the middle before the first Enter, then sweep the full range of each joint before the second Enter.

**The gripper number and the fingers disagree.** Gripper travel is 0–100 after calibration. Recalibrate with the fingers fully open and fully closed during the sweep.

**Plugin install fails on Windows with a missing file inside `software\plugins`.** Those folders are symlinks. Enable Developer Mode, run `git config --global core.symlinks true`, delete the XLeRobot folder, and clone it again.

## Where to go next

- [Software overview](https://xlerobot.readthedocs.io/en/latest/software/index.html) — the order the project recommends: one arm, then vision, then the full robot.
- [Arm examples](https://xlerobot.readthedocs.io/en/latest/software/getting_started/SO101.html) — joint, end-effector, dual-arm, and a YOLO follow demo (`3_so100_yolo_ee_control.py`) after the arm already moves.
- [Teleop](https://xlerobot.readthedocs.io/en/latest/software/getting_started/XLeRobot_teleop.html) — keyboard, Xbox, Joy-Con, and VR for the full robot.
- [SO-101 on Hugging Face](https://huggingface.co/docs/lerobot/en/so101) — assembly, motor IDs, and calibration videos.
- [LeRobot install](https://huggingface.co/docs/lerobot/installation) — if a future LeRobot release changes the extras or the Python version.

Simulation, if you want to practice keys before the real arm is built, starts at the [simulation getting started](https://xlerobot.readthedocs.io/en/latest/simulation/getting_started/) page. The browser demo is [MuJoCo-GS-Web](https://vector-wangel.github.io/MuJoCo-GS-Web/).
