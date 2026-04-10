# Demo 1: Quick Start — Python API Mode
# Run: vhs assets/tapes/demo-1-quickstart.tape

Output assets/demo-1-quickstart.gif

Set FontSize 16
Set Width 900
Set Height 450
Set Theme "Homebrew"
Set Padding 20
Set Shell zsh

# Warm up + write scripts silently
Hide
Type "cd ~/Documents/dev/E2E_Skills_Work/claude-runner-python"
Enter
Sleep 1s
Type "export ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY"
Enter
Sleep 500ms
Type "cat <<'SCRIPT' > /tmp/cr_demo.py"
Enter
Type "import asyncio, os"
Enter
Type "from claude_runner import Runner"
Enter
Type ""
Enter
Type "async def main():"
Enter
Type "    runner = Runner(api_key=os.environ['ANTHROPIC_API_KEY'])"
Enter
Type "    result = await runner.run('What is Python? One sentence.')"
Enter
Type "    print(result.text)"
Enter
Type "    print(f'Cost: ${result.cost:.4f}')"
Enter
Type ""
Enter
Type "asyncio.run(main())"
Enter
Type "SCRIPT"
Enter
Sleep 500ms
Type "clear"
Enter
Sleep 500ms
Show

Set TypingSpeed 50ms

Type "cat /tmp/cr_demo.py"
Enter
Sleep 3s

Type "python /tmp/cr_demo.py"
Enter
Sleep 10s
