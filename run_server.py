#!/usr/bin/env python3
"""
Custom server runner that supports --config-folder option.
"""

import argparse
import os
import sys

import uvicorn


def main():
    """Main entry point for the server runner."""
    parser = argparse.ArgumentParser(description="Mock API Server Runner")

    # Custom arguments
    parser.add_argument("--config-folder", type=str, help="Path to the configuration folder containing api.json, auth.json, and endpoints.json files")

    # Standard uvicorn arguments
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Bind socket to this host")
    parser.add_argument("--port", type=int, default=8000, help="Bind socket to this port")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes")
    parser.add_argument("--log-level", type=str, default="info", help="Log level")

    args = parser.parse_args()

    # Set config folder as environment variable if provided
    if args.config_folder:
        if not os.path.exists(args.config_folder):
            print(f"Error: Config folder '{args.config_folder}' does not exist")
            sys.exit(1)
        os.environ["MOCK_CONFIG_FOLDER"] = args.config_folder
        print(f"Using config folder: {args.config_folder}")

    # Run uvicorn with the remaining arguments
    uvicorn.run("src.main:app", host=args.host, port=args.port, reload=args.reload, workers=args.workers if not args.reload else 1, log_level=args.log_level)  # Workers must be 1 when reload is enabled


if __name__ == "__main__":
    main()
