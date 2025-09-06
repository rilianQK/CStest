import os
import glob
from emoji_codec import EmojiCodec, CompressionMethod, VerificationMethod

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    ENDC = '\033[0m'
    CYAN = '\033[96m'

def get_valid_input(prompt, valid_options):
    while True:
        user_input = input(prompt).strip().lower()
        if user_input in valid_options:
            return user_input
        print(f"Invalid option. Please choose from {valid_options}.")

def handle_batch_processing(codec):
    file_pattern = input("Enter file pattern (e.g., *.txt): ")
    output_dir = input("Enter output directory: ")
    operation = get_valid_input("Choose operation (encode/decode): ", ["encode", "decode"])
    results = codec.batch_process(file_pattern, output_dir, operation)
    for result in results:
        print(result)

def handle_file_operations(codec):
    input_path = input("Enter input file path: ")
    output_path = input("Enter output file path: ")
    operation = get_valid_input("Choose operation (encode/decode): ", ["encode", "decode"])
    result = codec.process_file(input_path, output_path, operation)
    print(result)

def handle_quick_operation(codec):
    operation = get_valid_input("Choose operation (encode/decode): ", ["encode", "decode"])
    if operation == "encode":
        data = input("Enter text to encode: ")
        encoded = codec.encode(data)
        print(f"Encoded: {encoded}")
    else:
        emoji_data = input("Enter emoji string to decode: ")
        decoded = codec.decode(emoji_data)
        print(f"Decoded: {decoded}")

def handle_settings(codec):
    recipe_type = get_valid_input("Choose recipe (quick/light/classic/gourmet): ", ["quick", "light", "classic", "gourmet"])
    compression = get_valid_input("Choose compression (none/zlib): ", ["none", "zlib"])
    verification = get_valid_input("Choose verification (none/sha256): ", ["none", "sha256"])
    return EmojiCodec(recipe_type, compression, verification)

def print_banner():
    print(f"{Colors.HEADER}{Colors.BOLD}Welcome to EmojiChef!{Colors.ENDC}")

def print_menu():
    print(f"{Colors.CYAN}1. Quick Encode/Decode")
    print("2. File Operations")
    print("3. Batch Processing")
    print("4. Settings")
    print("5. View Recipe Book")
    print("6. Exit{Colors.ENDC}")

def view_recipe_book():
    print(f"{Colors.GREEN}Available Recipes:")
    print("Quick (Base-64): Uses food emojis (🍅🍆🍇)")
    print("Light (Base-128): Uses activity emojis (🎰🎱🎲)")
    print("Classic (Base-256): Uses smiley emojis (😀😃😄)")
    print("Gourmet (Base-1024): Uses extended emoji set (🤠🤡🤢){Colors.ENDC}")

def main():
    codec = EmojiCodec('quick')
    while True:
        print_banner()
        print_menu()
        choice = get_valid_input("Choose an option: ", ["1", "2", "3", "4", "5", "6"])
        if choice == "1":
            handle_quick_operation(codec)
        elif choice == "2":
            handle_file_operations(codec)
        elif choice == "3":
            handle_batch_processing(codec)
        elif choice == "4":
            codec = handle_settings(codec)
        elif choice == "5":
            view_recipe_book()
        elif choice == "6":
            print("Goodbye!")
            break

if __name__ == "__main__":
    main()