import subprocess

class SecurityChecker:
    def identify_hash(self, hash_input):
        """Identify the type of hash using hash-identifier."""
        try:
            # Call the hash-identifier script with the input hash
            process = subprocess.run(
                ["hash-identifier"],
                input=hash_input.encode(),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            # Print the result
            print("\nHash-Identifier Output:")
            print(process.stdout)
        except FileNotFoundError:
            print("\nError: hash-identifier is not installed on this system.")
            print("Install it using: sudo apt install hash-identifier or clone it from GitHub.")
        except Exception as e:
            print(f"\nAn error occurred while identifying the hash: {e}")