import argparse
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

class EmojiChefCLI:
    def __init__(self):
        self.parser = self._create_parser()
        self.use_color = True

    def _create_parser(self):
        parser = argparse.ArgumentParser(description="EmojiChef - Emoji Encoding/Decoding Tool")
        parser.add_argument('operation', choices=['encode', 'decode'], help="Operation to perform")
        parser.add_argument('input', help="Input text or file path")
        parser.add_argument('--output', help="Output file path (optional)")
        parser.add_argument('--recipe', choices=['quick', 'light', 'classic', 'gourmet'], default='quick', help="Encoding recipe")
        parser.add_argument('--compression', choices=['none', 'zlib'], default='none', help="Compression method")
        parser.add_argument('--verification', choices=['none', 'sha256'], default='none', help="Verification method")
        parser.add_argument('--batch', action='store_true', help="Batch processing mode")
        parser.add_argument('--quiet', action='store_true', help="Suppress output")
        return parser

    def analyze_input(self, input_path, codec):
        file_info = codec.get_file_info(input_path)
        suggested_recipe = codec._suggest_recipe(file_info['size'])
        print(f"Suggested recipe: {suggested_recipe}")
        print(f"File info: {file_info}")

    def batch_process(self, pattern, output_dir, codec, operation, quiet):
        results = codec.batch_process(pattern, output_dir, operation)
        if not quiet:
            for result in results:
                print(result)

    def colorize(self, text, color):
        if self.use_color:
            return f"{color}{text}{Colors.ENDC}"
        return text

    def process_file(self, input_path, output_path, codec, operation, quiet):
        result = codec.process_file(input_path, output_path, operation)
        if not quiet:
            print(result)

    def process_text(self, text, codec, operation, quiet):
        if operation == 'encode':
            encoded = codec.encode(text)
            if not quiet:
                print(f"Encoded: {encoded}")
            return encoded
        else:
            decoded = codec.decode(text)
            if not quiet:
                print(f"Decoded: {decoded}")
            return decoded

    def run(self):
        args = self.parser.parse_args()
        codec = EmojiCodec(args.recipe, args.compression, args.verification)

        if args.batch:
            self.batch_process(args.input, args.output, codec, args.operation, args.quiet)
        elif args.output:
            self.process_file(args.input, args.output, codec, args.operation, args.quiet)
        else:
            self.process_text(args.input, codec, args.operation, args.quiet)

def main():
    cli = EmojiChefCLI()
    cli.run()

if __name__ == "__main__":
    main()