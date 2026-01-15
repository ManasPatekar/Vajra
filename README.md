# ⚡ Vajra (वज्र)
![Vajra Logo](vajra_logo.png)
### *The Indestructible System Sentinel*

**Vajra** is not just a system monitor; it is an **active guardian** for your PC. Unlike passive tools that simply watch your system freeze, Vajra proactively manages resources to keep your machine alive under heavy load.

---

## 🚀 Why Vajra?

Most monitoring tools are **passive observers**. They show you a graph while your RAM hits 100% and your PC crashes.

**Vajra represents a new philosophy:**
*   **🛡️ Active Protection:** Automatically detects high RAM usage (>90%) and triggers a safe, OS-level memory trim to free up resources instantly.
*   **⚡ Zero-Lag Dashboard:** Built with a high-performance Text User Interface (TUI). It runs smoothly even when Windows Task Manager hangs.
*   **📂 Forensic Logging:** Every resource spike and cleanup action is recorded in `vajra.log`. perfect for diagnosing performance issues the next day.
*   **🎒 Portable Power:** A single, standalone `.exe` file. No installation. No administrative bloat. Run it on any Windows laptop or server.

---

## 🖥️ The Dashboard

Vajra provides a unified "Heads-Up Display" (HUD) for your system vitals:

*   **CPU**: Live usage bar + Frequency (GHz).
*   **RAM**: Real-time Used vs. Available memory.
*   **Disks**: Storage health and free space.
*   **Network**: Live upload/download speeds.
*   **Top Processes**: The top 5 resource-hungry apps, updated intelligently to save CPU.
*   **Event Log**: A scrolling history of alerts and auto-clean actions.

---

## 📥 How to Run

### Option 1: The Easy Way (Recommended)
**Works on any Windows PC/Laptop.**

1.  Download the latest **`Vajra.exe`** from the [Releases](https://github.com/ManasPatekar/Vajra/releases) page.
2.  Double-click `Vajra.exe`.
3.  That's it! The guardian is now active.

### Option 2: For Developers (Python)
If you want to modify the source code:

```bash
# Clone the repository
git clone https://github.com/ManasPatekar/Vajra.git
cd Vajra

# Install dependencies
pip install psutil rich

# Run the guardian
python vajra.py
```

---

## 🛠️ Commands

You can run Vajra with arguments for different modes:

*   `vajra.exe` (Default) → Starts the live dashboard.
*   `vajra.exe logs` → Follows the `vajra.log` file in real-time (like `tail -f`).
*   `vajra.exe help` → Shows usage instructions.

---

## 📊 Vajra vs. Task Manager

| Feature | Windows Task Manager | ⚡ Vajra |
| :--- | :--- | :--- |
| **Philosophy** | Passive Observer | **Active Guardian** |
| **Action** | Watches PC freeze | **Auto-Cleans RAM** |
| **History** | None | **Permanent Logs** |
| **Interface** | Heavy GUI | **Fast Terminal UI** |
| **Portable** | No | **Yes (Single File)** |

---

### *Origin*
*The name **Vajra** (Sanskrit: वज्र) refers to a legendary indestructible weapon, symbolizing both the brilliance of diamond and the force of a thunderbolt.*

---
**Author**: [Manas Patekar](https://github.com/ManasPatekar)
