import argparse
import sys
from typing import List
from hermes.core import Hermes

def parse_args(args: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Hermes Video Transcription and Commentary Tool")
    parser.add_argument("source", help="Source file, URL, or 'mic' for microphone input")
    parser.add_argument("-p", "--provider", choices=["groq", "openai", "mlx"], default="groq", help="Transcription provider")
    parser.add_argument("-m", "--model", help="Model to use for transcription")
    parser.add_argument("-o", "--output", help="Output file path")
    parser.add_argument("-f", "--force", action="store_true", help="Force transcription even if cached")
    parser.add_argument("--response_format", choices=["json", "text", "srt", "verbose_json", "vtt"], default="text", help="Response format")
    parser.add_argument("--llm_prompt", help="Prompt for LLM processing of transcription")
    parser.add_argument("--generate-commentary", action="store_true", help="Generate video commentary")
    parser.add_argument("--textual-commentary", action="store_true", help="Generate textual commentary")
    parser.add_argument("--interval-type", choices=["frames", "seconds", "total_snapshots"], default="frames", help="Interval type for frame extraction")
    parser.add_argument("--interval-value", type=int, default=60, help="Interval value for frame extraction")
    parser.add_argument("--snapshot-count", type=int, default=10, help="Number of snapshots to extract")
    parser.add_argument("--target-size", type=int, help="Target size for frame resizing")
    parser.add_argument("--video-output-size", type=int, nargs='+', help="Output video size (width height)")
    parser.add_argument("--bg-music-path", help="Path to background music file")

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
        hermes = Hermes()

        if known_args.generate_commentary:
            result = hermes.generate_video_commentary(
                known_args.source,
                force=known_args.force,
                interval_type=known_args.interval_type,
                interval_value=known_args.interval_value,
                target_size=known_args.target_size,
                video_output_size=tuple(known_args.video_output_size) if known_args.video_output_size else None,
                bg_music_path=known_args.bg_music_path,
                **extra_args
            )
            print(f"Commentary generated. Final video: {result['final_video_path']}")
            print("Commentary:")
            print(result['commentary'])
        elif known_args.textual_commentary:
            result = hermes.generate_textual_commentary(
                known_args.source,
                force=known_args.force,
                interval_type=known_args.interval_type,
                interval_value=known_args.interval_value,
                target_size=known_args.target_size,
                llm_prompt=known_args.llm_prompt,
                **extra_args
            )
            print("Textual Commentary:")
            print(result['textual_commentary'])
            if 'llm_processed' in result:
                print("\nLLM Processed Result:")
                print(result['llm_processed'])
        else:
            result = hermes.transcribe(
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