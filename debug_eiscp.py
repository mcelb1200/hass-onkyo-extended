
import eiscp
from eiscp.core import command_to_iscp

def verify_radio_command():
    print("Verifying 'input-selector=radio'...")
    try:
        iscp = command_to_iscp("input-selector=radio")
        print(f"radio -> {iscp}")
    except Exception as e:
        print(f"radio -> Error: {e}")

    try:
        iscp = command_to_iscp("input-selector=tuner")
        print(f"tuner -> {iscp}")
    except Exception as e:
        print(f"tuner -> Error: {e}")

if __name__ == "__main__":
    verify_radio_command()
