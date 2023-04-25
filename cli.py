'''CLI to run structure as a package'''

import argparse
import uvicorn

def main():
    parser = argparse.ArgumentParser(description="Run the FastAPI server for your package.")
    parser.add_argument("--host", default="0.0.0.0", help="Host IP to bind the server to. (default: 0.0.0.0)")
    parser.add_argument("--port", default=8080, type=int, help="Port number to bind the server to. (default: 8080)")
    parser.add_argument("--log-level", default="info", help="Log level for the server. (default: info)")

    args = parser.parse_args()

    uvicorn.run("structure.server.server:app", host=args.host, port=args.port, log_level=args.log_level)

if __name__ == "__main__":
    main()