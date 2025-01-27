# 🖱️ Chun's AutoClicker v2

A modern, feature-rich autoclicker with a sleek interface and powerful customization options. Perfect for games, testing, or any situation where you need automated clicking!

![AutoClicker Interface](https://github.com/user-attachments/assets/f9e0df2f-50f4-48e4-b731-995a9f886d53)


## ✨ Features

- 🎯 Support for left, right, and middle mouse buttons
- ⚡ Customizable click intervals (0.01 to 10 seconds)
- 🎲 Random interval variation to simulate human behavior
- 🔄 Double-click support
- 🎮 Convenient hotkey controls (F6-F9)
- 💪 Multi-process architecture for reliable performance
- 🎨 Modern, sleek user interface
- 📊 Click count limiting
- 🔝 Always-on-top window option

## 🚀 Getting Started

### Prerequisites
- Windows OS
- Python 3.6 or higher (if running from source)

### Installation

#### Option 1: Download the Executable
1. Head to the [Releases](https://github.com/Chungus1310/AutoClicker/releases) page
2. Download the latest `.exe` file
3. Run it - no installation needed!

#### Option 2: Run from Source
1. Clone the repository:
   ```bash
   git clone https://github.com/Chungus1310/AutoClicker.git
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python autoclicker.py
   ```

## 🎮 How to Use

1. Launch the application
2. Configure your preferences:
   - Set your desired click interval
   - Choose click type (left/right/middle)
   - Enable/disable double-click
   - Set up random timing if desired
   - Configure maximum clicks (optional)
   - Select your preferred hotkeys

3. Start/Stop clicking:
   - Press F6 (default) to start/stop
   - Press F12 (default) to exit
   - Use the GUI to adjust settings on the fly

## 🛠️ Advanced Features

### Random Timing
Enable more human-like clicking patterns by adding random variations to click intervals. Adjust the randomization range to fine-tune the variation.

### Multi-Process Architecture
The application uses Python's multiprocessing to ensure reliable clicking performance, even during intensive operations.

### Process Count
Customize the number of worker processes (1-4) based on your system's capabilities and needs.

## 🤝 Contributing

Feel free to contribute to this project! Here's how:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💖 Support

If you find this tool helpful, consider:
- Starring the repository
- Reporting bugs or suggesting features through [Issues](https://github.com/Chungus1310/AutoClicker/issues)
- Sharing it with others who might find it useful

## 🔍 Technical Details

Built with:
- PyQt5 for the GUI
- pynput for keyboard monitoring
- pyautogui for mouse control
- Python's multiprocessing for performance
- Modern Python features and best practices

The application uses a multi-process architecture to ensure reliable clicking while maintaining a responsive interface. The main process handles the GUI and user input, while separate processes manage the clicking operations.

## ⚠️ Note

This tool is intended for legitimate use cases such as testing and automation. Please use responsibly and in accordance with the terms of service of any software you're using it with.

Happy clicking! 🎉
