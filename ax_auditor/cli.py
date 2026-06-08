import argparse
import sys
from .auditor import audit
from .reporter import generate_markdown, print_console


def main() -> None:
    parser = argparse.ArgumentParser(
        description="AX Auditor — Audit how agent-friendly any web service is",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ax-auditor https://example.com
  ax-auditor https://api.example.com --format markdown --output report.md
  ax-auditor https://example.com --timeout 60
        """,
    )
    parser.add_argument("url", help="Target URL to audit (e.g. https://example.com)")
    parser.add_argument("--format", "-f", choices=["console", "markdown"], default="console", help="Output format")
    parser.add_argument("--output", "-o", help="Write report to file (markdown only)")
    parser.add_argument("--timeout", "-t", type=int, default=30, help="HTTP request timeout in seconds")

    args = parser.parse_args()

    if not args.url.startswith(("http://", "https://")):
        print("Error: URL must start with http:// or https://", file=sys.stderr)
        sys.exit(1)

    try:
        report = audit(args.url, timeout=args.timeout)
    except Exception as e:
        print(f"Error auditing {args.url}: {e}", file=sys.stderr)
        sys.exit(1)

    if args.format == "markdown" or args.output:
        md = generate_markdown(report)
        if args.output:
            with open(args.output, "w") as f:
                f.write(md)
            print(f"Report written to {args.output}")
        else:
            print(md)
    else:
        print_console(report)


if __name__ == "__main__":
    main()
