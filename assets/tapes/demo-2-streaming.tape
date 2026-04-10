# Demo 2: Streaming with Custom Tools
# Run: vhs assets/tapes/demo-2-streaming.tape

Output assets/demo-2-streaming.gif

Set FontSize 16
Set Width 900
Set Height 500
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
Type "python -c 'import claude_runner' 2>/dev/null"
Enter
Sleep 2s
Type "cat <<'SCRIPT' > /tmp/demo_stream.py"
Enter
Type "import asyncio, os"
Enter
Type "from claude_runner import Runner, define_tool, ToolResult"
Enter
Type ""
Enter
Type "async def get_weather(city: str) -> ToolResult:"
Enter
Type "    return ToolResult(content=[{'type': 'text', 'text': f'72F and sunny in {city}'}])"
Enter
Type ""
Enter
Type "weather = define_tool('get_weather', 'Get weather for a city', {'city': {'type': 'string'}}, get_weather)"
Enter
Type ""
Enter
Type "async def main():"
Enter
Type "    runner = Runner(api_key=os.environ['ANTHROPIC_API_KEY'], tools=[weather])"
Enter
Type "    async for event in runner.stream('What is the weather in Tokyo and Paris?'):"
Enter
Type "        match event.type:"
Enter
Type "            case 'text': print(event.text, end='', flush=True)"
Enter
Type "            case 'tool_start': print(f'  > {event.tool}')"
Enter
Type "            case 'tool_end': print(f'  < {event.tool} ({event.duration:.0f}ms)')"
Enter
Type "            case 'done': print(f'\\nCost: ${event.result.cost:.4f}')"
Enter
Type ""
Enter
Type "asyncio.run(main())"
Enter
Type "SCRIPT"
Enter
Sleep 500ms
Type "cat <<'DISPLAY' > /tmp/demo_display.py"
Enter
Type "import asyncio, os"
Enter
Type "from claude_runner import Runner, define_tool, ToolResult"
Enter
Type ""
Enter
Type "async def get_weather(city: str) -> ToolResult:"
Enter
Type "    return ToolResult(content=[{'type': 'text', 'text': f'72F and sunny in {city}'}])"
Enter
Type ""
Enter
Type "weather = define_tool('get_weather', 'Get weather', {'city': {'type': 'string'}}, get_weather)"
Enter
Type ""
Enter
Type "async def main():"
Enter
Type "    runner = Runner(api_key=os.environ['ANTHROPIC_API_KEY'], tools=[weather])"
Enter
Type "    async for event in runner.stream('What is the weather in Tokyo and Paris?'):"
Enter
Type "        match event.type:"
Enter
Type "            case 'text': print(event.text, end='')"
Enter
Type "            case 'tool_start': print(f'  > {event.tool}')"
Enter
Type "            case 'tool_end': print(f'  < {event.tool}')"
Enter
Type "            case 'done': print(f'Cost: ${event.result.cost:.4f}')"
Enter
Type ""
Enter
Type "asyncio.run(main())"
Enter
Type "DISPLAY"
Enter
Sleep 500ms
Type "clear"
Enter
Sleep 500ms
Show

Set TypingSpeed 50ms

Type "cat /tmp/demo_display.py"
Enter
Sleep 3s

Type "python /tmp/demo_stream.py"
Enter
Sleep 20s
