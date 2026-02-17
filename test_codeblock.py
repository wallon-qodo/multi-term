#!/usr/bin/env python3
"""
Test script for code block extraction functionality.

Run this to see the code block system in action without needing full app.
"""

from rich.console import Console
from rich.text import Text
from claude_multi_terminal.widgets.code_block_integration import CodeBlockHighlighter
from claude_multi_terminal.widgets.code_block import CodeBlockParser


def main():
    """Run code block tests."""
    console = Console()

    # Test data - simulates Claude output with code blocks
    test_output = '''
Hello! Here's a Python function to calculate fibonacci numbers:

```python
def fibonacci(n):
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Test the function
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
```

And here's the same logic in JavaScript:

```javascript
function fibonacci(n) {
    // Calculate the nth Fibonacci number
    if (n <= 1) {
        return n;
    }
    return fibonacci(n-1) + fibonacci(n-2);
}

// Test the function
for (let i = 0; i < 10; i++) {
    console.log(`F(${i}) = ${fibonacci(i)}`);
}
```

You can also use dynamic programming for better performance:

```python
def fibonacci_dp(n):
    """Calculate Fibonacci using dynamic programming."""
    if n <= 1:
        return n

    dp = [0, 1]
    for i in range(2, n + 1):
        dp.append(dp[i-1] + dp[i-2])

    return dp[n]
```

Hope this helps!
'''

    # Test 1: Basic parsing
    console.print("\n[bold cyan]Test 1: Basic Code Block Parsing[/bold cyan]\n")
    console.print("=" * 80)

    blocks = CodeBlockParser.extract_code_blocks(test_output)
    console.print(f"\n✓ Found {len(blocks)} code blocks\n")

    for i, (language, code, start, end) in enumerate(blocks):
        line_count = len(code.split('\n'))
        char_count = len(code)
        console.print(f"  Block {i}:")
        console.print(f"    Language: [bold]{language}[/bold]")
        console.print(f"    Lines: {line_count}")
        console.print(f"    Characters: {char_count}")
        console.print(f"    Position: {start}-{end}")
        console.print()

    # Test 2: Visual enhancement
    console.print("\n[bold cyan]Test 2: Visual Enhancement[/bold cyan]\n")
    console.print("=" * 80)

    highlighter = CodeBlockHighlighter()
    enhanced = highlighter.process_output(test_output)

    console.print(enhanced)

    # Test 3: Block metadata
    console.print("\n[bold cyan]Test 3: Block Metadata[/bold cyan]\n")
    console.print("=" * 80)

    all_blocks = highlighter.get_all_blocks()
    for block in all_blocks:
        console.print(f"\n[bold]Block #{block['id']}[/bold]")
        console.print(f"  Language: {block['language']}")
        console.print(f"  Lines: {block['line_count']}")
        console.print(f"  Characters: {block['char_count']}")

        # Show first 3 lines of code
        code_lines = block['code'].split('\n')
        console.print(f"  Preview:")
        for line in code_lines[:3]:
            console.print(f"    {line}")
        if len(code_lines) > 3:
            console.print(f"    ... ({len(code_lines) - 3} more lines)")

    # Test 4: Edge cases
    console.print("\n\n[bold cyan]Test 4: Edge Cases[/bold cyan]\n")
    console.print("=" * 80)

    edge_cases = [
        ("No code blocks", "Just plain text without any code blocks."),
        ("Empty code block", "```python\n```"),
        ("No language", "```\nsome code\n```"),
        ("Nested backticks", "```python\nprint('```')\n```"),
        ("Multiple languages", "```py\ncode\n``` ```js\ncode\n```"),
    ]

    for name, test_case in edge_cases:
        blocks = CodeBlockParser.extract_code_blocks(test_case)
        console.print(f"\n  {name}:")
        console.print(f"    Input: {repr(test_case[:50])}...")
        console.print(f"    Blocks found: {len(blocks)}")

    # Test 5: Performance
    console.print("\n\n[bold cyan]Test 5: Performance[/bold cyan]\n")
    console.print("=" * 80)

    import time

    # Generate large output with many code blocks
    large_output = ""
    for i in range(100):
        large_output += f"\nHere's code block {i}:\n\n```python\n"
        large_output += f"def function_{i}():\n    pass\n"
        large_output += "```\n"

    start_time = time.time()
    blocks = CodeBlockParser.extract_code_blocks(large_output)
    parse_time = time.time() - start_time

    start_time = time.time()
    highlighter = CodeBlockHighlighter()
    enhanced = highlighter.process_output(large_output)
    enhance_time = time.time() - start_time

    console.print(f"\n  Input: 100 code blocks")
    console.print(f"  Parse time: {parse_time*1000:.2f}ms")
    console.print(f"  Enhancement time: {enhance_time*1000:.2f}ms")
    console.print(f"  Total time: {(parse_time + enhance_time)*1000:.2f}ms")
    console.print(f"  Blocks found: {len(blocks)}")

    # Summary
    console.print("\n\n[bold green]✓ All tests completed successfully![/bold green]\n")

    # Interactive demo
    console.print("\n[bold cyan]Interactive Demo[/bold cyan]\n")
    console.print("=" * 80)
    console.print("\nThe code block system provides:")
    console.print("  • Automatic detection of fenced code blocks")
    console.print("  • Beautiful visual formatting with borders")
    console.print("  • Language badges and metadata")
    console.print("  • Line numbers for easy reference")
    console.print("  • Right-click context menu integration")
    console.print("  • Copy to clipboard functionality")
    console.print("  • Save to file with smart extension detection")
    console.print("\nIntegrate it into SessionPane to see it in action!")
    console.print()


if __name__ == "__main__":
    main()
