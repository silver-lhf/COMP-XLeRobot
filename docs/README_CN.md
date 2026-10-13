# 入門：控制 XLeRobot 機械臂

[English](README.md) | 繁體中文

這份指南帶你用鍵盤讓一條真實的 XLeRobot 機械臂動起來，接著說明怎麼接上手腕相機、並在手臂移動時讀到畫面，然後再走一條很短的路：加上第二條手臂，以及整台移動機器人。

這是本工作區裡的一份本地入門說明。硬體、腳本和外掛都在上游專案裡：[Vector-Wangel/XLeRobot](https://github.com/Vector-Wangel/XLeRobot)。官方文件：[xlerobot.readthedocs.io](https://xlerobot.readthedocs.io/en/latest/)。

下面的指令對照 2026 年 10 月的專案核對過。這份指南是給 Windows 用的。XLeRobot 的範例預設使用 Linux 名稱，例如 `/dev/ttyACM0`。在 Windows 上，同一條線是 COM 埠，例如 `COM5`，下面每條指令都使用這個 COM 名稱。

如果你根據那個儲存庫組裝、購買或運行 XLeRobot，它對你或他人造成的任何身體或精神傷害，都由你本人承擔。這是該專案自己的免責聲明。

## 你在控制什麼

XLeRobot 的手臂是一條 [SO-101](https://huggingface.co/docs/lerobot/en/so101) 從動臂。「從動臂」的意思是：電腦告訴馬達轉到哪裡。另外一條主臂（你用手掰動的同款手臂）是可選的。用鍵盤控制時不需要主臂。

每條手臂有六顆飛特 STS3215 舵機，接在同一塊控制板上。它們共用一條線，這條線叫匯流排。每顆馬達有一個數字 ID，電腦靠它找到要溝通的那一顆。

| 馬達 ID | 程式裡的名字 | 它做什麼 |
| --- | --- | --- |
| 1 | `shoulder_pan` | 整條手臂左右轉 |
| 2 | `shoulder_lift` | 大臂抬起、放下 |
| 3 | `elbow_flex` | 肘部彎曲 |
| 4 | `wrist_flex` | 手腕上下擺 |
| 5 | `wrist_roll` | 手腕扭轉 |
| 6 | `gripper` | 夾爪張開、閉合 |

`software/examples/` 裡的鍵盤腳本建立的是 `SO100Follower`。在目前的 LeRobot 裡，`SO100Follower` 和 `SO101Follower` 是同一個機器人類別，只是註冊了兩個名字。XLeRobot 說明這些腳本在 SO-101 和 SO-100 硬體上都能跑。控制這條手臂時就用它們。

單臂大約能舉起 600 公克到 1 公斤。工作半徑大約 40 公分。第一次實驗就停在這個範圍裡。

## 下任何指令之前的安全事項

每一次都要做，包括第一次「只動一點點」的測試。

- USB 線只傳資料，不給馬達供電。馬達電源和 USB 都要插上。
- 電源要和舵機上印的電壓一致。7.4 V 馬達用 5 V 電源。12 V 馬達用 12 V 電源。電壓不對會燒毀馬達。
- 把桌面清空。第一個控制腳本一旦準備好，就會用大約三秒把每個關節推向零位。
- 一隻手放在電源插頭上。拔掉電源是始終有效的停止方式。
- 腳本中斷連線時會關掉馬達力矩。手臂會下垂。結束之前，把手臂放在桌上，或托住小臂。
- 點按按鍵。第一次不要按住不放。控制迴圈是 50 Hz，按住時會一直疊加動作。
- 不要超過負載。夾爪裡的東西太重，手腕會堵轉。

單臂腳本裡的 `X` 會讓手臂緩緩回到啟動時的姿態。`Esc` 或 Ctrl+C 會停止程式。動作看起來不對時，先拔電源，再查原因。

## 你會看到的詞

- **終端機（Terminal）。** 你輸入指令的文字視窗。在 Windows 上，用安裝程式建立的 Miniforge Prompt；如果 Miniforge 已經加進 PATH，也可以用 PowerShell。等你輸入的那一行叫提示字元。
- **Conda 環境。** 一份名叫 `lerobot` 的獨立 Python。本指南裡的每條指令之前，都要在新開的終端機裡先啟動它。跳過這一步，Python 就找不到 LeRobot。
- **埠（Port）。** Windows 給這條 USB 連線的名字。它看起來像 `COM5`。裝置管理員把這些列在 **連接埠 (COM 和 LPT)** 下面。你的編號可能是 `COM3`、`COM4`，或其他 COM 埠。用你找到的那個編號。範例裡的 `COM5` 只是佔位。
- **相機編號（Camera index）。** OpenCV 用來指一顆 USB 相機的數字。它看起來像 `0` 或 `1`。它不是 COM 埠。馬達控制板仍然在它的 COM 埠上。相機是另外一顆 USB 裝置，`lerobot-find-cameras` 會印出它的編號。
- **校正（Calibration）。** 一份儲存下來的檔案，把馬達的原始讀數換成關節角度。第一次執行必須產生它。以後再執行時，回答 `n` 就會沿用這份檔案。
- **關節控制。** 一次只推動一顆馬達。
- **末端控制。** 你推動的是夾爪在空間中的位置。腳本會算出肩部和肘部的角度。這個計算叫逆向運動學。
- **P 控制。** 腳本不會一下子跳到新角度。每一時刻只走完剩餘誤差的一部分（增益是 0.5，所以是一半），動作因此是緩進去的。

啟動控制腳本之後，用滑鼠點一下終端機視窗。鍵盤讀取函式庫（`pynput`）只在這個視窗處於焦點時才能收到按鍵。

## 1. 安裝軟體

你需要 Git 和 Miniforge（一種 Conda 安裝程式）。LeRobot 的安裝說明要求 Python 3.12。

- Windows 版 Git：[git-scm.com/download/win](https://git-scm.com/download/win)
- Miniforge：[Miniforge 發布頁](https://github.com/conda-forge/miniforge/releases)上的 Windows x86_64 安裝檔

安裝 Miniforge 時，保留「註冊 Conda」那個選項。然後打開 **Miniforge Prompt**。

### 複製 XLeRobot 之前先打開符號連結

XLeRobot 後面的外掛是一串符號連結資料夾（指向真實程式碼的捷徑）。Windows 要能建立它們，需要打開開發人員模式，或者允許 Git 使用符號連結。複製儲存庫之前設定一次：

```powershell
git config --global core.symlinks true
```

最開始的手臂腳本用不到這些外掛。但這個設定必須在 `git clone` 之前生效，因為 Git 在複製時就決定了要不要建立符號連結。

### 建立 Python 環境

```powershell
conda create -y -n lerobot python=3.12
conda activate lerobot
```

每個新的終端機裡都要執行 `conda activate lerobot`。

### 安裝帶馬達和鍵盤功能的 LeRobot

LeRobot 是和飛特匯流排通訊的函式庫。複製它，再以可編輯方式安裝這條手臂需要的額外套件。`feetech` 是舵機驅動。`core_scripts` 會帶上序列埠、鍵盤函式庫、校正，以及 `lerobot-*` 指令。

在 PowerShell 裡，方括號是萬用字元，所以額外套件外面的引號必須保留。

```powershell
cd $HOME
git clone https://github.com/huggingface/lerobot.git
cd lerobot
pip install -e ".[feetech,core_scripts]"
```

確認指令已經裝上：

```powershell
lerobot-find-port --help
```

你應該看到說明文字。如果出現 “command not found”，表示目前這個終端機裡還沒有這個指令。

### 複製 XLeRobot

```powershell
cd $HOME
git clone https://github.com/Vector-Wangel/XLeRobot.git
```

手臂範例在 `XLeRobot\software\examples`。這個複本保持原樣。腳本就在那裡執行，不要把它們複製進 LeRobot 儲存庫。

上游安裝說明（含移動底盤外掛）：[安裝 LeRobot 和 XLeRobot 外掛](https://xlerobot.readthedocs.io/en/latest/software/getting_started/install.html)。

## 2. 找到 USB 埠

Windows 把這條連線叫做 COM 埠。沒有 `chmod` 這一步，也沒有 `/dev/ttyACM0`。那些名字屬於 Linux。在你的電腦上，控制板是 `COM5`、`COM6`，或裝置管理員顯示的任何編號。

1. 用一條能傳資料的 USB 線把控制板接到電腦。只能充電的線什麼都不會出現。
2. 插上馬達電源。USB 線只傳資料。
3. 在已啟動的 `lerobot` 環境裡執行：

```powershell
lerobot-find-port
```

程式會列出像 `COM3`、`COM5` 這樣的埠，請你拔掉控制板，然後告訴你哪一個埠消失了。那個名字就是你的手臂。把它記下來。

也可以在裝置管理員裡做同樣的檢查：

1. 在開始按鈕上按右鍵，選擇 **裝置管理員**。
2. 打開 **連接埠 (COM 和 LPT)**。
3. 插上控制板，看哪一個 COM 埠出現。拔掉它，那個項目就會消失。

第二塊控制板會有自己的 COM 編號，例如 `COM6`。第一塊板保持插著，再插上第二塊，記下新出現的 COM 埠。

如果板子已經列出來、馬達卻沒有回應，把馬達電源拔掉再插上，然後再執行一次 `lerobot-find-port`。

如果用的是微雪（Waveshare）匯流排舵機板，板上的兩隻跳線都要插在標著 `B` 的 USB 通道上。跳線是硬體，在 Windows 上和在其他電腦上一樣設定。如果插在另一個通道，Windows 就不會出現 COM 埠。

## 3. 給每顆馬達寫一次 ID

新舵機出廠 ID 是 1。同一條匯流排上的六顆馬達必須是 1 到 6，否則它們會互相搶著回應。這一步把 ID 寫進馬達，每顆只做一次。

**在馬達串接起來之前**做。每次只把一顆馬達接到控制板上。

```powershell
lerobot-setup-motors --robot.type=so101_follower --robot.port=COM5
```

把 `COM5` 換成上一步找到的 COM 埠。

腳本會一次要一顆馬達，順序是：

1. 夾爪 → ID 6
2. 手腕扭轉 → ID 5
3. 手腕擺動 → ID 4
4. 肘部 → ID 3
5. 大臂抬升 → ID 2
6. 底座旋轉 → ID 1

每一步：拔掉其他馬達，只接它指定的那一顆，然後按 Enter。全部完成後，再把馬達串起來（底座旋轉接控制板，然後是大臂，一直串到夾爪）。

用馬克筆把 ID 寫在每顆馬達上。第二條手臂用自己的控制板，也是自己的 1–6。兩組分開標，例如 `L1`–`L6` 和 `R1`–`R6`。

同一套指令的官方步驟：[SO-101](https://huggingface.co/docs/lerobot/en/so101)。

## 4. 校正，然後一次只動一個關節

校正記錄每個關節的中點和能轉到的範圍。控制腳本會儲存它，以後再執行時還會問你。

手臂已上電、終端機已點中的情況下，在範例目錄裡：

```powershell
conda activate lerobot
cd $HOME\XLeRobot\software\examples
python 0_so100_keyboard_joint_control.py --robot.port=COM5
```

接下來會發生：

1. 腳本連線到手臂。如果還沒有儲存過校正，LeRobot 自己開始校正時，按它的提示做。
2. 它會問 `Do you want to recalibrate the robot? (y/n)`。第一次回答 `y`。以後回答 `n`，除非你重新裝過手臂，或轉過馬達舵盤。
3. 把每個關節都放到行程的**正中間**，然後按 Enter。
4. **逐個**關節慢慢走完**整個範圍**：底座旋轉、大臂、肘、手腕上下、手腕扭轉、夾爪開合。腳本說停止記錄時再按 Enter。
5. 然後手臂會用大約三秒緩緩走向零位。工作區保持清空。
6. 鍵盤接手。

| 按鍵 | 關節 | 點一下的效果 |
| --- | --- | --- |
| `Q` / `A` | 底座旋轉 | 大約 −1° / +1° |
| `W` / `S` | 大臂抬升 | 大約 −1° / +1° |
| `E` / `D` | 肘部 | 大約 −1° / +1° |
| `R` / `F` | 手腕擺動 | 大約 −1° / +1° |
| `T` / `G` | 手腕扭轉 | 大約 −1° / +1° |
| `Y` / `H` | 夾爪 | 在 0–100 的刻度上大約 −5 / +5 |
| `X` | 結束 | 緩緩回到啟動姿態，然後結束 |
| `Esc` | 結束 | 停止程式 |

手臂關節的單位是度。夾爪是 0（行程一端）到 100（另一端）。腳本會把夾爪限制在這個範圍裡。

先把一個關節練到方向清楚，再換下一個。肩和肘按住一個鍵就會擺很大，所以用點按。

這個示範的上游頁面：[SO100/SO101 手臂範例](https://xlerobot.readthedocs.io/en/latest/software/getting_started/SO101.html)。

## 5. 移動手，而不是逐個關節

關節控制已經可預期之後，換成末端控制。`W` `S` `E` `D` 在手臂的側面平面裡移動夾爪。腳本的逆向運動學把這個點換成肩和肘的角度，並讓手腕跟著傾斜。

```powershell
python 1_so100_keyboard_ee_control.py --robot.port=COM5
```

校正問題的回答和前面一樣（如果剛剛校過，就答 `n`）。按鍵生效之前，手臂會再次緩緩走向零位。

夾爪從大約 `x = 0.163` 公尺、`y = 0.113` 公尺開始，這是手臂自己座標系統裡的位置。`W` `S` `E` `D` 每點一下走 4 公釐。如果你要的點手臂搆不到，腳本會把目標拉回到工作空間的邊緣。

| 按鍵 | 動的是什麼 |
| --- | --- |
| `Q` / `A` | 底座旋轉，仍然是單個關節 |
| `W` / `S` | 夾爪的 X（在手臂平面裡向前 / 向後） |
| `E` / `D` | 夾爪的 Y（在手臂平面裡向上 / 向下） |
| `R` / `F` | 手腕俯仰。這是在「跟隨」之外，再給手腕加一個角度 |
| `T` / `G` | 手腕扭轉 |
| `Y` / `H` | 夾爪 |
| `X` | 緩緩回到啟動姿態，然後結束 |
| `Esc` | 停止程式 |

## 6. 接上手腕相機，並讀到一張畫面

手腕相機看的是夾爪正要去拿的東西。它是一顆小的 USB 相機，鎖在手腕上、夾爪馬達旁邊。它不在舵機匯流排上。它沒有馬達 ID，也不用馬達電源。它的 USB 插頭插到電腦上，就在馬達控制板的 USB 插頭旁邊。兩者可以同時接上：控制板仍然是一個 COM 埠，例如 `COM5`，相機則拿到一個數字，例如 `1`。

做這一步時，手臂要斷電，並放在桌上。線被勾住是這一步最常見的問題，所以重新給馬達通電之前，先把線留出餘量。

### 零件

任何 32 公釐 × 32 公釐、至少 720p、30 fps 的 USB 相機模組都能裝上。SO-101 的支架是照著[這顆 Innomaker 模組](https://www.amazon.com/innomaker-Computer-Raspberry-Support-Windows/dp/B0CNCSFQC1)畫的。另外還需要：

- [3D 列印的六角螺帽相機轉接座](https://github.com/TheRobotStudio/SO-ARM100/blob/main/Optional/SO101_Wrist_Cam_Hex-Nut_Mount_32x32_UVC_Module/stl/SO-ARM101_camera_wrist_mount.stl)。按 STL 裡的方向列印，使用樹狀支撐，填充大約 40%，相機才不會晃。
- 4 顆 M2 螺絲。這些是飛特舵機附的小螺絲。
- 2 顆 M3 × 8 公釐螺絲，和 2 顆 M3 六角螺帽。舵機套件裡沒有這兩樣。

同一套步驟的圖解：[SO-101 手腕相機支架](https://github.com/TheRobotStudio/SO-ARM100/tree/main/Optional/SO101_Wrist_Cam_Hex-Nut_Mount_32x32_UVC_Module)。

### 裝到手腕上

1. 拔掉馬達電源和控制板的 USB 線。
2. 拆下馬達 6（夾爪）。活動夾爪件可以留在馬達上。
3. 把兩顆 M3 六角螺帽放進手腕扭轉件上的凹槽。
4. 把馬達 6 裝回去，用原來的 M2 螺絲鎖上。
5. 用兩顆 M3 螺絲把列印好的轉接座鎖到這兩顆螺帽上。
6. 把相機的四個孔對準轉接座，用四顆 M2 螺絲鎖上。

### 插上線

1. 把相機的 USB 線插到和馬達控制板同一台電腦的空 USB 埠。要用能傳資料的線。只能充電的線不會出現相機。電腦沒有空埠時，USB 集線器可以用。
2. 把線沿著手臂拉回電腦。手腕留一圈鬆的線，肘部再留一圈，兩個關節走完整個範圍時才不會把插頭扯掉。線不要碰到手指，也不要伸進底座旋轉的掃過範圍。
3. 按第 2 節的方式，把馬達控制板和馬達電源插回去。相機留在它自己的 USB 埠上。

### 找出相機的編號

LeRobot 已經帶了 OpenCV，不必再裝其他套件。在已啟動的 `lerobot` 環境裡：

```powershell
lerobot-find-cameras opencv
```

這條指令會列出每顆相機，並在你執行時所在的資料夾底下，把測試畫面存到 `outputs\captured_images`。名叫 `opencv_1.png` 的檔案，就是 Id 為 `1` 的那顆相機。

在 Windows 上，這個 Id 是一個小整數。筆記型電腦內建相機常常是 `0`，手腕相機是下一個。要確認的話，拔掉手腕相機，再執行一次，看哪一個 Id 消失了。插回去之後就用那個 Id。

打開存下來的畫面。鏡頭是手動對焦的，一開始會很糊。轉動鏡頭，直到下一次存下來的畫面清楚。之後用 640 × 480、30 fps。再高只是手臂用不到的額外資料。

也可以先打開 Windows 的 **相機** 應用程式，在裡面切換相機，確認模組在進 Python 之前是好的。執行 `lerobot-find-cameras` 或你的腳本之前，把這個應用程式關掉。Windows 一次只讓一個程式佔用相機。

### 手臂連著的時候讀一張畫面

`software\examples` 裡的鍵盤腳本不會打開相機。你自己的腳本可以：把相機傳進你已經用來移動手臂的那個 `SO100Follower`。

把下面存成 `arm_and_camera.py`。埠改成你的 COM 埠，相機 Id 用上一步找到的編號。

```python
from PIL import Image

from lerobot.cameras.opencv import OpenCVCameraConfig
from lerobot.robots.so_follower import SO100Follower, SO100FollowerConfig

robot = SO100Follower(
    SO100FollowerConfig(
        port="COM5",
        id="my_arm",
        cameras={
            "wrist": OpenCVCameraConfig(
                index_or_path=1,
                width=640,
                height=480,
                fps=30,
            )
        },
    )
)

robot.connect()
obs = robot.get_observation()
print(obs["shoulder_pan.pos"], obs["wrist"].shape)
Image.fromarray(obs["wrist"]).save("wrist.jpg")

# 手臂和相機共用這一次連線。
# 先用一個靠近手臂目前位置的小角度。
robot.send_action({"shoulder_pan.pos": 10.0})
obs = robot.get_observation()
Image.fromarray(obs["wrist"]).save("wrist_after_move.jpg")

robot.disconnect()
```

手臂已上電、桌面已清空時執行。如果進入校正，手臂仍可能緩緩走向零位，和第 4 節一樣。

```powershell
python arm_and_camera.py
```

`obs["wrist"]` 是一張 NumPy 影像，形狀是 `(480, 640, 3)`，顏色是 RGB。`wrist` 這個名字就是你寫進 `cameras` 的鍵。`shoulder_pan.pos` 這類關節鍵不變。`wrist.jpg` 是相機在那一刻看到的畫面。

在同一個腳本裡、`connect()` 之後，一個一直同時做這兩件事的迴圈，寫法和鍵盤腳本一樣：先讀，再下指令，然後等大約 0.02 秒。

```python
import time

while True:
    obs = robot.get_observation()
    frame = obs["wrist"]
    # 在這裡使用 frame。下面這行讓肩部停在目前的位置。
    robot.send_action({"shoulder_pan.pos": obs["shoulder_pan.pos"]})
    time.sleep(0.02)
```

按 Ctrl+C 停止，然後呼叫 `robot.disconnect()`，力矩才會關掉。`send_action` 仍然需要你打算維持的每一個關節。程式要跑一段時間時，其他 `.pos` 就從 `obs` 裡抄過來。見第 9 節。

### 不只一顆相機

每多一顆相機，就是多一個 USB 插頭、多一個 Id。再加一筆，例如 `"head"`，並填上它自己的 `index_or_path`。整台機器人通常是每條手腕一顆，再加上頭部一顆。馬達控制板仍然是僅有的 COM 埠。相機不會和它們共用這些埠。

推車裡的樹莓派在插上兩塊馬達控制板之後，還剩兩個 USB-A 埠。第三顆相機要用 USB 集線器。

## 7. 兩條手臂

每條手臂有自己的控制板和自己的 USB 埠。用 `lerobot-find-port` 分別找出兩個埠（它讓你拔線時，拔掉其中一塊板，就能知道哪個埠是哪一塊）。

```powershell
python 2_dual_so100_keyboard_ee_control.py --arm1.port=COM5 --arm2.port=COM6
```

把你找到的兩個 COM 埠分別填進這兩個參數，哪一塊板對哪一個參數都可以，只要各對上一塊板。開始時兩條手臂都會緩緩走向零位。提示校正時，兩條都要校。

腳本會印出下面這張表。手臂 1 用數字那一排。手臂 2 用主鍵盤中間那一排。

**手臂 1**

| 按鍵 | 動的是什麼 |
| --- | --- |
| `7` / `Y` | 底座旋轉 |
| `8` / `U` | 夾爪 X |
| `9` / `I` | 夾爪 Y |
| `=` / `[` | 手腕俯仰 |
| `0` / `O` | 手腕扭轉 |
| `-` / `P` | 夾爪 |

**手臂 2**

| 按鍵 | 動的是什麼 |
| --- | --- |
| `H` / `B` | 底座旋轉 |
| `J` / `N` | 夾爪 X |
| `K` / `M` | 夾爪 Y |
| `,` / `.` | 手腕俯仰 |
| `;` / `L` | 手腕扭轉 |
| `'` / `/` | 夾爪 |

`X` 讓兩條手臂緩緩回去並結束。`Esc` 停止程式。

## 8. 整台機器人（底盤、頭部和兩條手臂）

等一條手臂已經穩定、操作變得無聊之後再做這一節。這些腳本需要額外的馬達，只有一條手臂時會失敗。

在單條桌面手臂之外，XLeRobot 還有兩塊控制板：

- 一塊板：一條 SO-101 手臂（ID 1–6）加上頭部（ID 7 和 8）。
- 另一塊板：另一條 SO-101 手臂（ID 1–6）加上輪式底盤（ID 7、8 和 9）。

LeRobot 的 `lerobot-setup-motors` 只分配手臂的 ID 1–6。頭部和輪子馬達要用 [Bambot 的舵機頁面](https://bambot.org/feetech.js)：接上一顆馬達，在瀏覽器裡選擇那塊板的 COM 埠，掃描，再按組裝圖把它改成 7、8 或 9。這些馬達也要標上（`L7`、`L8`、`R7`–`R9`）。

把筆記型電腦放進推車裡就夠用。樹莓派是可選的。

準備好這一步時再安裝外掛。在 XLeRobot 的複本目錄裡，並且 `lerobot` 已啟動：

```powershell
pip install -e software\plugins\xlerobot_model
pip install -e software\plugins\lerobot_robot_xlerobot
```

`lerobot_robot_xlerobot` 是三輪全向底盤。如果你裝的是兩輪差速版，就安裝 `software\plugins\lerobot_robot_xlerobot_2wheels`，並改跑 `4_xlerobot_2wheels_teleop_keyboard.py`。麥克納姆底盤有自己的外掛 `lerobot_robot_xlerobot_mecanum`。如果 `pip install -e` 看不到外掛資料夾，表示複製時沒有符號連結支援。打開開發人員模式，按第 1 節設定 `core.symlinks`，刪掉這個複本，再複製一次。

然後在 `software\examples` 裡執行（如果腳本開頭印出的路徑把 `examples` 算進去了，從儲存庫根目錄執行也可以）：

```powershell
python 4_xlerobot_teleop_keyboard.py --robot.port1=COM5 --robot.port2=COM6
```

`--robot.port1` 是「手臂加頭部」那塊板。`--robot.port2` 是「手臂加底盤」那塊板（和 Lekiwi 底盤的接法相同）。兩塊接反時，會出現類似 “need 9 motors, but 8 detected” 的錯誤。把兩個埠參數對調即可。

這個腳本啟動時也會讓手臂緩緩走向零位。

**左臂和頭部**

| 按鍵 | 動的是什麼 |
| --- | --- |
| `Q` / `E` | 底座旋轉 |
| `W` / `S` | 手的 X |
| `A` / `D` | 手的 Y |
| `Z` / `X` | 手腕俯仰 |
| `R` / `F` | 手腕扭轉 |
| `T` / `G` | 夾爪 |
| `<` / `>` | 頭部馬達 1（美式鍵盤上是 Shift+, 和 Shift+.） |
| `,` / `.` | 頭部馬達 2 |
| `C` | 左臂回到零位附近 |
| `Y` | 左臂畫一個小矩形（畫完之前它會自己動） |
| `?` | 頭部回到零位附近（美式鍵盤上是 Shift+/） |

**右臂**（數字鍵盤，或字母上方的數字鍵；用數字鍵盤時打開 Num Lock）

| 按鍵 | 動的是什麼 |
| --- | --- |
| `7` / `9` | 底座旋轉 |
| `8` / `2` | 手的 X |
| `4` / `6` | 手的 Y |
| `1` / `3` | 手腕俯仰 |
| `/` / `*` | 手腕扭轉 |
| `+` / `-` | 夾爪 |
| `0` | 右臂回到零位附近 |
| `Y`（Shift+y） | 右臂畫一個小矩形 |

**底盤**（機器人設定裡的預設按鍵）

| 按鍵 | 動的是什麼 |
| --- | --- |
| `I` / `K` | 前進 / 後退 |
| `J` / `L` | 左平移 / 右平移 |
| `U` / `O` | 旋轉 |
| `N` / `M` | 加速 / 減速 |
| `B` | 結束 |

按 `I` 之前，先給輪子留出空地。更多遙控操作方式（Xbox、Joy-Con、VR）在[遙控操作頁面](https://xlerobot.readthedocs.io/en/latest/software/getting_started/XLeRobot_teleop.html)。

## 9. 用你自己的 Python 指揮手臂

這些示範就是一個迴圈裡的兩次呼叫：先讀 `get_observation()`，再 `send_action()`。你可以用一段很短的腳本做同樣的事。

把下面存成 `move_once.py`，放在範例資料夾外面，並保持 `lerobot` 環境處於啟動狀態。埠改成你的 COM 埠。`id` 是校正檔案的名字；每次連線這條手臂都用同一個字串。

```python
from lerobot.robots.so_follower import SO100Follower, SO100FollowerConfig

# 用裝置管理員裡的 COM 埠，例如 "COM5"。
robot = SO100Follower(SO100FollowerConfig(port="COM5", id="my_arm"))

robot.connect()
print(robot.get_observation())

# 手臂關節的單位是度。夾爪是 0 到 100。
# 這裡只改底座旋轉。其他關節會保持控制板裡上一次的目標，
# 你把它們也寫進字典後就會一併保持。先用一個靠近手臂目前位置的小角度。
robot.send_action({"shoulder_pan.pos": 10.0})

robot.disconnect()
```

執行：

```powershell
python move_once.py
```

`get_observation()` 會印出類似 `shoulder_pan.pos`、`shoulder_lift.pos`、`elbow_flex.pos`、`wrist_flex.pos`、`wrist_roll.pos` 和 `gripper.pos` 的鍵。

真正要移動時，應該像範例那樣寫一個短迴圈：讀目前角度，朝目標走一小段，`send_action`，暫停大約 0.02 秒，再重複。一次發出很大的 `send_action` 會讓手臂突然跳一下。範例用 0.5 的增益、50 Hz，就是為了避免這個。

`send_action` 需要你打算維持的每一個關節。字典裡只有 `shoulder_pan.pos` 時，其他馬達會留在控制板的上一個目標上。第一次試驗、手臂已經放穩並通電時，這樣可以。程式要跑一段時間時，每個週期都送出全部六個 `.pos`，你不想動的關節就沿用上一次讀到的值。

鍵盤腳本也是這個模式。按鍵到來時改目標，每個週期送出 `current + 0.5 * (target - current)`。

如果像第 6 節那樣傳了 `cameras`，同一次 `get_observation()` 也會帶上影像，鍵名就是你取的那個名字。

## 排除問題

**系統找不到 `conda` 或 `lerobot-find-port`。** 打開 Miniforge Prompt，或在這個終端機裡執行 `conda activate lerobot`。新開的終端機預設不在這個環境裡。

**沒有出現 COM 埠。** 換一條能傳資料的 USB 線，把微雪跳線設到 `B`。如果裝置管理員裡是未知裝置，安裝這塊板的 USB 序列埠驅動程式。關掉其他已經佔用這個埠的序列埠監控程式。

**相機沒有出現。** 關掉 Windows 的相機應用程式，以及其他已經打開相機的程式，然後再執行一次 `lerobot-find-cameras opencv`。換一個 USB 埠，並使用能傳資料的線。相機不會顯示成 COM 埠。

**畫面是筆記型電腦的內建相機。** 內建相機的編號常常是 `0`。拔掉手腕相機，再執行一次尋找指令，用消失的那個 Id。

**畫面很糊。** 轉動模組上的鏡頭，直到新的測試畫面變清楚。這個對焦是手動的。

**`lerobot-find-cameras` 報錯，或一直等不到畫面。** 有些 UVC 模組在 Windows 上需要 DirectShow。在 `OpenCVCameraConfig` 裡設定 `backend=Cv2Backends.DSHOW`，並先寫 `from lerobot.cameras import Cv2Backends`。如果畫面仍然逾時，把 `fps` 從 30 降到 20。

**手臂一動，USB 線就被拉緊。** 在手腕和肘部再留一些餘量，並把線移開夾爪。線拉緊時，插頭會自己脫落，或把某個關節卡住。

**偵測不到馬達。** 電源是和 USB 分開的插頭。把馬達電源拔掉再插上，然後再試。設定 ID 時，控制板到馬達只接那條 3 針舵機線。

**馬達數量不對，或出現 “need 9 motors, but 8 detected”。** ID 衝突了，或者整機的兩個埠接反了。單臂必須正好是 ID 1–6。整機上，埠 1 是手臂加頭部（8 顆馬達），埠 2 是手臂加底盤（9 顆馬達）。

**`lerobot.robots.so_follower...` 出現 `ModuleNotFoundError`。** 範例腳本匯入的是內部檔案：

```python
from lerobot.robots.so_follower.so_follower import SO100Follower
from lerobot.robots.so_follower.config_so_follower import SO100FollowerConfig
```

你自己的腳本應該用這個公開匯入：

```python
from lerobot.robots.so_follower import SO100Follower, SO100FollowerConfig
```

LeRobot 更新之後，如果範例裡較長的那兩行匯入失敗，就改用上面這個公開匯入，要改的就是範例檔案裡的那兩行。

**按鍵沒有反應。** 用滑鼠點一下終端機視窗。在 Windows 上，有些安全性軟體會攔截 `pynput` 用的鍵盤掛鉤；腳本已經連上、卻忽略所有按鍵時，允許這個 Python 處理程序。

**手臂突然跳動，或某個關節方向反了。** 跳過了校正，或校正之後轉過舵盤。再執行腳本並回答 `y`。第一次按 Enter 之前，把每個關節放到中間；第二次按 Enter 之前，把每個關節的整個範圍都走一遍。

**夾爪的數字和手指對不上。** 校正之後，夾爪行程是 0–100。重新校正時，掃描階段要把手指完全張開、再完全閉合。

**在 Windows 上安裝外掛失敗，提示 `software\plugins` 裡找不到檔案。** 那些資料夾是符號連結。打開開發人員模式，執行 `git config --global core.symlinks true`，刪掉 XLeRobot 資料夾，再複製一次。

## 接下來去哪裡

- [軟體總覽](https://xlerobot.readthedocs.io/en/latest/software/index.html) — 專案建議的順序：先一條手臂，再視覺，再整台機器人。
- [相機](https://huggingface.co/docs/lerobot/en/cameras) — 找出相機，再用 OpenCV 讀取畫面。
- [SO-101 手腕相機支架](https://github.com/TheRobotStudio/SO-ARM100/tree/main/Optional/SO101_Wrist_Cam_Hex-Nut_Mount_32x32_UVC_Module) — 六角螺帽轉接座的圖解。
- [手臂範例](https://xlerobot.readthedocs.io/en/latest/software/getting_started/SO101.html) — 關節、末端、雙臂，以及手臂已經能動之後的 YOLO 跟隨示範（`3_so100_yolo_ee_control.py`）。
- [遙控操作](https://xlerobot.readthedocs.io/en/latest/software/getting_started/XLeRobot_teleop.html) — 整機的鍵盤、Xbox、Joy-Con 和 VR。
- [Hugging Face 上的 SO-101](https://huggingface.co/docs/lerobot/en/so101) — 組裝、馬達 ID 和校正影片。
- [LeRobot 安裝](https://huggingface.co/docs/lerobot/installation) — 以後的 LeRobot 版本如果改了額外套件或 Python 版本，看這裡。

如果想在真手臂組好之前先練按鍵，模擬從[模擬入門](https://xlerobot.readthedocs.io/en/latest/simulation/getting_started/)開始。瀏覽器裡的示範是 [MuJoCo-GS-Web](https://vector-wangel.github.io/MuJoCo-GS-Web/)。
