from hellofib.lib import fib

# In .bzl config, setting python_config.run_module = "hellofib.main" should cause this to run as the entry point
if __name__ == "__main__":
    print("Launching HelloFib from __main__")
    fib()
