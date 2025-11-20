
import eiscp
from eiscp import eISCP
import inspect

def inspect_conn_logic():
    print("Inspecting eISCP._ensure_socket_connected and disconnect...")
    try:
        print("--- ENSURE ---")
        print(inspect.getsource(eISCP._ensure_socket_connected))
        print("\n--- DISCONNECT ---")
        print(inspect.getsource(eISCP.disconnect))
    except Exception as e:
        print(f"Could not get source: {e}")

if __name__ == "__main__":
    inspect_conn_logic()
