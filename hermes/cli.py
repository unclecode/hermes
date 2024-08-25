import argparse
import sys
from typing import List
from hermes.core import Hermes, transcribe

def parse_args(args: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Hermes Video Transcription Tool")
    parser.add_argument("source", help="Source file, URL, or 'mic' for microphone input")
    parser.add_argument("-p", "--provider", choices=["groq", "openai", "mlx"], default="groq", help="Transcription provider")
    parser.add_argument("-m", "--model", help="Model to use for transcription")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("-f", "--force", action="store_true", help="Force transcription even if cached")
    parser.add_argument("--response_format", choices=["json", "text", "srt", "verbose_json", "vtt"], default="text", help="Response format")
    parser.add_argument("--llm_prompt", help="Prompt for LLM processing of transcription")
    
    # Parse known args first
    known_args, unknown_args = parser.parse_known_args(args)
    
    # Parse remaining args as key-value pairs
    extra_args = {}
    for i in range(0, len(unknown_args), 2):
        if i + 1 < len(unknown_args):
            key = unknown_args[i].lstrip('-')
            value = unknown_args[i + 1]
            extra_args[key] = value
    
    return known_args, extra_args

def main():
    known_args, extra_args = parse_args(sys.argv[1:])
    
    try:
        result = transcribe(
            source=known_args.source,
            provider=known_args.provider,
            force=known_args.force,
            llm_prompt=known_args.llm_prompt,
            model=known_args.model,
            response_format=known_args.response_format,
            **extra_args
        )
        
        if known_args.output:
            with open(known_args.output, 'w') as f:
                f.write(result['transcription'])
            print(f"Transcription saved to {known_args.output}")
        else:
            print(result['transcription'])
        
        if 'llm_processed' in result:
            print("\nLLM Processed Result:")
            print(result['llm_processed'])
    
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

def cli_entry_point():
    main()

if __name__ == "__main__":
    cli_entry_point()