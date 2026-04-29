import sys
from ui.app import SecurePassApp

if __name__ == "__main__":
    try:
        app = SecurePassApp()
        app.mainloop()
    except KeyboardInterrupt:
        sys.exit(0)
