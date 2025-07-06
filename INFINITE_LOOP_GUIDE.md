# 🔄 Infinite Loop Auto-Execution Script

This script automatically runs `python .\start_all_python.py` every 15 minutes forever. You only need to start it once!

## 🚀 Quick Start

### 1. Run the infinite loop script once:
```bash
python infinite_loop.py
```

### 2. That's it! 
The script will now:
- ✅ Run `python .\start_all_python.py` immediately
- ⏰ Wait 15 minutes
- 🔄 Run `python .\start_all_python.py` again
- ♾️ Repeat forever

## 📋 What You'll See

```
[2025-07-06 13:23:18] 🔄 Infinite Loop Script Started
[2025-07-06 13:23:18] 📋 Will run 'python .\start_all_python.py' every 15 minutes
[2025-07-06 13:23:18] 🛑 Press Ctrl+C to stop the loop
[2025-07-06 13:23:18] ============================================================
[2025-07-06 13:23:18] 🔢 Execution #1
[2025-07-06 13:23:18] 🚀 Starting execution of start_all_python.py...
[2025-07-06 13:23:20] ✅ start_all_python.py completed successfully
[2025-07-06 13:23:20] ⏰ Next execution scheduled at: 13:38:20
[2025-07-06 13:23:20] 💤 Waiting 15 minutes...
[2025-07-06 13:23:20] ------------------------------------------------------------
```

## 🛑 How to Stop

Press `Ctrl+C` in the terminal where the script is running:

```
[2025-07-06 13:38:20] 🛑 Infinite loop stopped by user (Ctrl+C)
[2025-07-06 13:38:20] 📊 Total executions completed: 2
[2025-07-06 13:38:20] 👋 Goodbye!
```

## 📁 File Requirements

Make sure you have these files in the same directory:

```
📂 Your Project Directory
├── 📄 infinite_loop.py          # The auto-execution script
├── 📄 start_all_python.py       # Your main script to run every 15 minutes
└── 📄 (other files...)
```

## 🔧 Features

### ✅ Automatic Execution
- Runs your script every 15 minutes precisely
- No manual intervention needed
- Continues running until you stop it

### 📊 Detailed Logging
- Timestamps for every action
- Execution counter
- Success/error reporting
- Next execution time display

### 🛡️ Error Handling
- Continues running even if your script fails
- Shows error messages clearly
- Doesn't crash the infinite loop

### 🔍 File Validation
- Checks if `start_all_python.py` exists
- Warns you if the file is missing
- Asks for confirmation before continuing

## 🧪 Testing with Demo

Want to test with shorter intervals? Use the demo version:

```bash
# Runs every 30 seconds instead of 15 minutes
python demo_infinite_loop.py
```

## 💡 Use Cases

Perfect for:
- 🤖 **Bot maintenance scripts**
- 📊 **Data collection tasks**
- 🧹 **Cleanup operations**
- 📧 **Periodic notifications**
- 🔄 **System health checks**
- 📈 **Report generation**

## 🎯 Example start_all_python.py

Your `start_all_python.py` can contain any Python code:

```python
#!/usr/bin/env python3
"""
Your main script that runs every 15 minutes
"""

def main():
    print("🚀 Running my automated tasks...")
    
    # Your code here
    # - Check databases
    # - Send emails
    # - Process files
    # - Update reports
    # - etc.
    
    print("✅ Tasks completed!")

if __name__ == "__main__":
    main()
```

## 🔧 Customization

### Change the Interval

Edit `infinite_loop.py` and modify this line:
```python
# Change 900 to your desired seconds
# 900 = 15 minutes
# 300 = 5 minutes  
# 1800 = 30 minutes
time.sleep(900)
```

### Change the Target Script

Edit `infinite_loop.py` and modify this line:
```python
# Change to your script name
[sys.executable, ".\\your_script_name.py"]
```

## 🌐 Running in Background

### Windows
```bash
# Run in background (closes when terminal closes)
start /B python infinite_loop.py

# Run as Windows service (advanced)
# Use tools like NSSM or create a Windows service
```

### Linux/Mac
```bash
# Run in background
nohup python infinite_loop.py &

# Run as systemd service (advanced)
# Create a service file in /etc/systemd/system/
```

## 🚨 Important Notes

1. **Keep Terminal Open**: The script runs as long as the terminal/command prompt is open
2. **File Location**: Both scripts must be in the same directory
3. **Python Path**: Make sure Python is in your system PATH
4. **Error Handling**: The loop continues even if your script fails
5. **Resource Usage**: Minimal CPU usage while waiting between executions

## 🎉 Benefits

- ✅ **Set and Forget**: Run once, works forever
- ✅ **No Cron Jobs**: No need to configure system schedulers
- ✅ **Cross-Platform**: Works on Windows, Linux, Mac
- ✅ **Simple Setup**: Just two Python files
- ✅ **Detailed Logging**: See exactly what's happening
- ✅ **Error Resilient**: Continues running despite errors

## 🔍 Troubleshooting

### Script Not Found Error
```
❌ Error: start_all_python.py not found in current directory
```
**Solution**: Make sure `start_all_python.py` exists in the same folder

### Permission Errors
```
❌ Permission denied
```
**Solution**: Run with appropriate permissions or check file permissions

### Python Not Found
```
❌ 'python' is not recognized
```
**Solution**: Make sure Python is installed and in your system PATH

Your infinite loop script is ready to use! 🎉
